__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import os
import sqlite3
import math
from collections import namedtuple, defaultdict
import logging

import trueskill

from slugathon.util import prefs, Dice
from slugathon.ai import BotParams, CleverBot
from slugathon.net import config


DB_PATH = os.path.join(prefs.RESULTS_DIR, "slugathon.db")

GENERATION_SIZE = 10
BREEDING_SIGMA_THRESHOLD = 1.0


ddl = """
CREATE TABLE game (
    game_id INTEGER PRIMARY KEY ASC,
    name TEXT,
    start_time INTEGER,
    finish_time INTEGER
);

CREATE TABLE type (
    type_id INTEGER PRIMARY KEY ASC,
    class TEXT, -- "Human" or "CleverBot"
    info TEXT   -- name for humans; any info that distinguishes AIs
);

CREATE TABLE player (
    player_id INTEGER PRIMARY KEY ASC,
    name TEXT,
    type_id INTEGER REFERENCES type(type_id)
);

CREATE TABLE rank (
    player_id INTEGER REFERENCES player(player_id),
    game_id INTEGER REFERENCES game(game_id),
    rank INTEGER  -- rank in the game from 1 (winner) through 6.  Ties okay.
);

CREATE TABLE trueskill (
    type_id INTEGER PRIMARY KEY REFERENCES type(type_id),
    mu REAL,
    sigma REAL
);
"""


class Ranking(namedtuple("Ranking", ["mu", "sigma"])):

    @property
    def skill(self):
        """Return an integer rating based on mu - 3 * sigma, at least 1."""
        return max(1, int(math.floor(self.mu - 3 * self.sigma)))

    def __repr__(self):
        return "Ranking: mu=%f sigma=%f skill=%d" % (self.mu, self.sigma,
          self.skill)


class Results(object):
    """Game results tracking using a sqlite database."""

    def __init__(self, db_path=DB_PATH):
        exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0
        dirname = os.path.dirname(db_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.connection = sqlite3.connect(db_path)
        # Allow accessing row items by name.
        self.connection.row_factory = sqlite3.Row
        self.enable_foreign_keys()
        if not exists:
            self.create_db()

    def enable_foreign_keys(self):
        query = "PRAGMA foreign_keys = ON"
        self.connection.execute(query)

    def create_db(self):
        self.connection.executescript(ddl)

    def save_game(self, game):
        """Save a finished Game to the results database.

        XXX This involves a non-trivial amount of computation and I/O, so
        maybe it should be run from a thread to avoid blocking the reactor.
        But sqlite is not thread-safe so we can't reuse connections.
        """
        logging.info("")
        with self.connection:
            cursor = self.connection.cursor()
            for player in game.players:
                logging.info("%s %s", player.player_class, player.player_info)

                # See if that type is already in the database
                query = """SELECT type_id FROM type
                           where class = ? AND info = ?"""
                cursor.execute(query, (player.player_class,
                  player.player_info))
                row = cursor.fetchone()
                # If not, insert it.
                if row is None:
                    query = "INSERT INTO type (class, info) VALUES (?, ?)"
                    cursor.execute(query, (player.player_class,
                      player.player_info))
                    # And fetch the type_id.
                    query = """SELECT type_id FROM type
                               where class = ? AND info = ?"""
                    cursor.execute(query, (player.player_class,
                      player.player_info))
                    row = cursor.fetchone()

                type_id = row["type_id"]

                # See if that player is already in the database
                name = player.name
                query = """SELECT player_id FROM player
                           WHERE name = ? AND type_id = ?"""
                cursor.execute(query, (name, type_id))
                row = cursor.fetchone()
                # If not, insert it.
                if row is None:
                    query = "INSERT INTO player (name, type_id) VALUES (?, ?)"
                    cursor.execute(query, (name, type_id))

            # Add the game.
            query = """INSERT INTO game (name, start_time, finish_time)
                       VALUES (?, ?, ?)"""
            cursor.execute(query, (game.name, int(game.start_time),
              int(game.finish_time)))
            # Find the game_id for the just-inserted game.
            query = """SELECT game_id FROM game WHERE
                       name = ? AND start_time = ? AND finish_time = ?"""
            cursor.execute(query, (game.name, int(game.start_time),
              int(game.finish_time)))
            row = cursor.fetchone()
            game_id = row["game_id"]
            rank = 1
            for tup in game.finish_order:
                for player in tup:
                    # Find the player_id
                    query = """SELECT player_id FROM player p, type t
                               WHERE p.type_id = t.type_id
                               AND p.name = ? AND t.class = ? AND t.info = ?"""
                    name = player.name
                    cursor.execute(query, (name, player.player_class,
                      player.player_info))
                    row = cursor.fetchone()
                    player_id = row["player_id"]
                    # Add to rank.
                    query = \
                      """INSERT INTO rank(player_id, game_id, rank)
                         VALUES (?, ?, ?)"""
                    cursor.execute(query, (player_id, game_id, rank))
                rank += len(tup)

            # Update trueskill table
            # There is a slight bias when there are ties, so we process tied
            # players in random order.
            query = """SELECT p.type_id, r.rank
                       FROM player p, rank r
                       WHERE p.player_id = r.player_id AND r.game_id = ?
                       ORDER BY r.rank, RANDOM()"""
            cursor.execute(query, (game_id, ))
            rows = cursor.fetchall()
            cursor2 = self.connection.cursor()
            type_ids = []
            rating_tuples = []
            ranks = []
            for row in rows:
                type_id = row["type_id"]
                type_ids.append(type_id)
                rank = row["rank"]
                ranks.append(rank)
                query2 = "SELECT mu, sigma FROM trueskill WHERE type_id = ?"
                cursor2.execute(query2, (player_id, ))
                row2 = cursor2.fetchone()
                if row2 is not None:
                    mu = row2["mu"]
                    sigma = row2["sigma"]
                else:
                    mu = None
                    sigma = None
                rating = trueskill.Rating(mu=mu, sigma=sigma)
                rating_tuples.append((rating, ))
            rating_tuples2 = trueskill.transform_ratings(rating_tuples, ranks)
            # If we have a duplicate type_id, average the mu and take the
            # maximum sigma.
            type_id_to_ratings = defaultdict(list)
            while type_ids:
                type_id = type_ids.pop()
                rating = rating_tuples2.pop()[0]
                type_id_to_ratings[type_id].append(rating)
            # If all players are the same type, then don't update trueskill,
            # as we have no new information.
            if len(type_id_to_ratings) > 1:
                for type_id, ratings in type_id_to_ratings.iteritems():
                    mu = sum(rating.mu for rating in ratings) / float(len(
                      ratings))
                    sigma = max(rating.sigma for rating in ratings)
                    query = """INSERT INTO trueskill (type_id, mu, sigma)
                               VALUES (?, ?, ?)"""
                    try:
                        cursor.execute(query, (type_id, mu, sigma))
                    except Exception:
                        query = """UPDATE trueskill SET mu = ?, sigma = ?
                                   WHERE type_id = ?"""
                        cursor.execute(query, (mu, sigma, type_id))
            else:
                logging.info("all players have same type_id")
        logging.info("")

    def get_ranking(self, playername):
        """Return a Ranking object for one player name.

        If the player is not found, return default values.
        """
        with self.connection:
            cursor = self.connection.cursor()
            query = """SELECT tr.mu, tr.sigma
                       FROM trueskill tr, player p, type ty
                       WHERE p.type_id = ty.type_id AND ty.type_id = tr.type_id
                       AND p.name = ?"""
            cursor.execute(query, (playername, ))
            rows = cursor.fetchall()
            if rows:
                row = rows[0]
                mu = row["mu"]
                sigma = row["sigma"]
            else:
                rating = trueskill.Rating()
                mu = rating.mu
                sigma = rating.sigma
            ranking = Ranking(mu, sigma)
            return ranking

    def get_player_info(self, type_id):
        """Return the player_info string for type_id, from the database."""
        with self.connection:
            cursor = self.connection.cursor()
            # See if that type is already in the database
            query = "SELECT info FROM type where type_id = ?"
            cursor.execute(query, (type_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return row["info"]

    def get_weighted_random_type_id(self):
        """Return a random type_id, weighted by mu.

        If there are fewer than GENERATION_SIZE AI type_ids in the database,
        add a new AI type (by mutating the default) and return its type_id.

        If there are fewer than GENERATION_SIZE AI type_ids in the database
        with sigma > BREEDING_SIGMA_THRESHOLD, breed a new AI type (by crossing
        two parent AI types with sigma <= BREEDING_SIGMA_THRESHOLD, chosen
        randomly weighted by mu), and return its type_id.

        Otherwise, choose an existing type_id randomly, weighted by mu, and
        return it.
        """
        with self.connection:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM type WHERE class='CleverBot'"
            cursor.execute(query)
            total_ai_count = cursor.fetchone()[0]
            if total_ai_count < GENERATION_SIZE:
                # Spawn a new AI, mutated from default_bot_params.
                bp = BotParams.default_bot_params.mutate_all_fields()
                bot = CleverBot.CleverBot("spawn",
                  config.DEFAULT_AI_TIME_LIMIT, bp)
                info = bot.player_info
                logging.info("player_info %s", info)
                query = "INSERT INTO type (class, info) VALUES (?, ?)"
                cursor.execute(query, ("CleverBot", info))
                # And fetch the type_id.
                query = """SELECT type_id FROM type
                           where class = ? AND info = ?"""
                cursor.execute(query, ("CleverBot", info))
                row = cursor.fetchone()
                type_id = row["type_id"]
                logging.info("spawning new AI %s %s", bp, type_id)
                return type_id
            else:
                query = """SELECT COUNT(*) FROM type ty, trueskill ts
                           WHERE ty.type_id = ts.type_id
                           AND ty.class = 'CleverBot'
                           AND ts.sigma > ?"""
                cursor.execute(query, (BREEDING_SIGMA_THRESHOLD,))
                young_ai_count = cursor.fetchone()[0]
                query = """SELECT COUNT(*) FROM type ty, trueskill ts
                           WHERE ty.type_id = ts.type_id
                           AND ty.class = 'CleverBot'
                           AND ts.sigma <= ?"""
                cursor.execute(query, (BREEDING_SIGMA_THRESHOLD,))
                old_ai_count = cursor.fetchone()[0]
                if young_ai_count < GENERATION_SIZE and old_ai_count >= 2:
                    # Breed a new AI, from two weighted-random low-sigma
                    # parents.
                    query = """SELECT ts.type_id, ts.mu
                               FROM type ty, trueskill ts
                               WHERE ty.type_id = ts.type_id
                               AND ty.class = 'CleverBot'
                               AND ts.sigma < ?"""
                    cursor.execute(query, (BREEDING_SIGMA_THRESHOLD,))
                    rows = cursor.fetchall()
                    possible_parents = []
                    for row in rows:
                        mu = row["mu"]
                        type_id = row["type_id"]
                        possible_parents.append((mu, type_id))
                    tup1 = Dice.weighted_random_choice(possible_parents)
                    possible_parents.remove(tup1)
                    tup2 = Dice.weighted_random_choice(possible_parents)
                    type_id1 = tup1[1]
                    info1 = self.get_player_info(type_id1)
                    bp1 = BotParams.BotParams.fromstring(info1)
                    type_id2 = tup2[1]
                    info2 = self.get_player_info(type_id2)
                    bp2 = BotParams.BotParams.fromstring(info2)
                    bp3 = bp1.cross(bp2)
                    bot = CleverBot.CleverBot("child",
                      config.DEFAULT_AI_TIME_LIMIT, bp3)
                    info = bot.player_info
                    logging.info("player_info %s", info)
                    query = "INSERT INTO type (class, info) VALUES (?, ?)"
                    cursor.execute(query, ("CleverBot", info))
                    # And fetch the type_id.
                    query = """SELECT type_id FROM type
                               where class = ? AND info = ?"""
                    cursor.execute(query, ("CleverBot", info))
                    row = cursor.fetchone()
                    type_id = row["type_id"]
                    logging.info("father %s %s", bp1, type_id)
                    logging.info("mother %s %s", bp2, type_id)
                    logging.info("baby new %s %s", bp3, type_id)
                    return type_id
                else:
                    # Pick an existing AI randomly, weighted by mu, and return
                    # its type_id.
                    query = """SELECT ts.type_id, ts.mu
                               FROM type ty, trueskill ts
                               WHERE ty.type_id = ts.type_id
                               AND ty.class = 'CleverBot'"""
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    candidates = []
                    for row in rows:
                        mu = row["mu"]
                        type_id = row["type_id"]
                        candidates.append((mu, type_id))
                    tup = Dice.weighted_random_choice(candidates)
                    type_id = tup[1]
                    logging.info("picked random AI %s", type_id)
                    return type_id
