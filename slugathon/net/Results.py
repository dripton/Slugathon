__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import os
import sqlite3
import math
from collections import namedtuple
import logging

import trueskill

from slugathon.util import prefs, Dice
from slugathon.ai import BotParams, CleverBot
from slugathon.net import config


DB_PATH = os.path.join(prefs.RESULTS_DIR, "slugathon.db")

GENERATION_SIZE = 10
BREEDING_SIGMA_THRESHOLD = 1.0
DEFAULT_MU = 25.0
DEFAULT_SIGMA = 25.0 / 3.0


ddl = """
CREATE TABLE game (
    game_id INTEGER PRIMARY KEY ASC,
    name TEXT,
    start_time INTEGER,
    finish_time INTEGER
);

CREATE TABLE player (
    player_id INTEGER PRIMARY KEY ASC,
    name TEXT,  -- must be unique, but this is not enforced
    class TEXT, -- "Human" or "CleverBot"
    info TEXT,  -- name for humans; any info that distinguishes AIs
    mu REAL,    -- skill level
    sigma REAL  -- certainty of skill level
);

CREATE TABLE rank (
    player_id INTEGER REFERENCES player(player_id),
    game_id INTEGER REFERENCES game(game_id),
    rank INTEGER  -- rank in the game from 1 (winner) through 6.  Ties okay.
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

                # See if that player is already in the database
                query = """SELECT player_id FROM player
                           where name = ? AND class = ? AND info = ?"""
                cursor.execute(query, (player.name, player.player_class,
                  player.player_info))
                row = cursor.fetchone()
                # If not, insert it.
                if row is None:
                    query = """INSERT INTO player
                               (name, class, info, mu, sigma)
                               VALUES (?, ?, ?, ?, ?)"""
                    cursor.execute(query, (player.name, player.player_class,
                      player.player_info, DEFAULT_MU, DEFAULT_SIGMA))
                    # And fetch the player_id.
                    query = """SELECT player_id FROM player
                               where class = ? AND info = ?"""
                    cursor.execute(query, (player.player_class,
                      player.player_info))
                    row = cursor.fetchone()

                player_id = row["player_id"]

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
                    query = """SELECT player_id FROM player
                               WHERE name = ? AND class = ? AND info = ?"""
                    cursor.execute(query, (player.name, player.player_class,
                      player.player_info))
                    row = cursor.fetchone()
                    player_id = row["player_id"]
                    # Add to rank.
                    query = """INSERT INTO rank(player_id, game_id, rank)
                               VALUES (?, ?, ?)"""
                    cursor.execute(query, (player_id, game_id, rank))
                rank += len(tup)

            # Update trueskill values
            # There is a slight bias when there are ties, so we process tied
            # players in random order.
            query = """SELECT p.player_id, p.mu, p.sigma, r.rank
                       FROM player p, rank r
                       WHERE p.player_id = r.player_id AND r.game_id = ?
                       ORDER BY r.rank, RANDOM()"""
            cursor.execute(query, (game_id, ))
            rows = cursor.fetchall()
            player_ids = []
            rating_tuples = []
            ranks = []
            for row in rows:
                player_id = row["player_id"]
                player_ids.append(player_id)
                rank = row["rank"]
                ranks.append(rank)
                mu = row["mu"]
                sigma = row["sigma"]
                rating = trueskill.Rating(mu=mu, sigma=sigma)
                rating_tuples.append((rating, ))
            rating_tuples2 = trueskill.transform_ratings(rating_tuples, ranks)
            while player_ids:
                player_id = player_ids.pop()
                rating = rating_tuples2.pop()[0]
                mu = rating.mu
                sigma = rating.sigma
                query = """UPDATE player set mu = ?, sigma = ?
                           WHERE player_id = ?"""
                cursor.execute(query, (mu, sigma, player_id))
        logging.info("")

    def get_ranking(self, playername):
        """Return a Ranking object for one player name.

        If the player is not found, return default values.
        """
        with self.connection:
            cursor = self.connection.cursor()
            query = "SELECT mu, sigma FROM player WHERE name = ?"
            cursor.execute(query, (playername, ))
            rows = cursor.fetchall()
            if rows:
                row = rows[0]
                mu = row["mu"]
                sigma = row["sigma"]
                if mu is None or sigma is None:
                    rating = trueskill.Rating()
                    mu = rating.mu
                    sigma = rating.sigma
            else:
                rating = trueskill.Rating()
                mu = rating.mu
                sigma = rating.sigma
            ranking = Ranking(mu, sigma)
            return ranking

    def get_player_info(self, player_id):
        """Return the player_info string for player_id, from the database."""
        with self.connection:
            cursor = self.connection.cursor()
            # See if that player is already in the database
            query = "SELECT info FROM player where player_id = ?"
            cursor.execute(query, (player_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return row["info"]

    def get_player_id(self, player_info):
        """Return the player_id for player_info, from the database."""
        logging.info(player_info)
        with self.connection:
            cursor = self.connection.cursor()
            # See if that player is already in the database
            query = "SELECT player_id FROM player where info = ?"
            cursor.execute(query, (player_info,))
            row = cursor.fetchone()
            if row is None:
                return None
            return row["player_id"]

    def get_player_data(self):
        """Return a list with one dict of data per player in the database."""
        data = []
        with self.connection:
            cursor = self.connection.cursor()
            query = """SELECT player_id, name, class, info, mu, sigma
                       FROM player order by player_id"""
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                player_id = row["player_id"]
                name = row["name"]
                player_class = row["class"]
                info = row["info"]
                mu = row["mu"]
                sigma = row["sigma"]
                ranking = Ranking(mu, sigma)
                skill = ranking.skill
                # TODO Maybe use a namedtuple instead
                player_data = {
                    "player_id": player_id,
                    "name": name,
                    "class": player_class,
                    "info": info,
                    "mu": mu,
                    "sigma": sigma,
                    "skill": skill,
                }
                data.append(player_data)
        return data

    def _spawn_new_ai(self, cursor):
        """Spawn a new AI, mutated from default_bot_params, and return
        its player_id."""
        bp = BotParams.default_bot_params.mutate_all_fields()
        bot = CleverBot.CleverBot("spawn", config.DEFAULT_AI_TIME_LIMIT, bp)
        info = bot.player_info
        logging.info("player_info %s", info)
        query = """INSERT INTO player (class, info, mu, sigma)
                   VALUES (?, ?, ?, ?)"""
        cursor.execute(query, ("CleverBot", info, DEFAULT_MU,
          DEFAULT_SIGMA))
        # And fetch the player_id.
        query = """SELECT player_id FROM player
                   where class = ? AND info = ?"""
        cursor.execute(query, ("CleverBot", info))
        row = cursor.fetchone()
        player_id = row["player_id"]
        # And update the name.
        name = "ai%d" % player_id
        query = """UPDATE player SET name = ?
                   WHERE player_id = ?"""
        cursor.execute(query, (name, player_id))
        logging.info("spawning new AI %s %s %s", player_id, name, bp)
        return player_id

    def _breed_new_ai(self, cursor, old_player_ids):
        """Breed a new AI, from two weighted-random experienced parents."""
        query = """SELECT p.player_id, p.mu FROM player p
                   WHERE p.class = 'CleverBot'"""
        cursor.execute(query)
        rows = cursor.fetchall()
        possible_parents = []
        for row in rows:
            mu = row["mu"]
            player_id = row["player_id"]
            if player_id in old_player_ids:
                possible_parents.append((mu, player_id))
        tup1 = Dice.weighted_random_choice(possible_parents)
        possible_parents.remove(tup1)
        tup2 = Dice.weighted_random_choice(possible_parents)
        player_id1 = tup1[1]
        info1 = self.get_player_info(player_id1)
        bp1 = BotParams.BotParams.fromstring(info1)
        player_id2 = tup2[1]
        info2 = self.get_player_info(player_id2)
        bp2 = BotParams.BotParams.fromstring(info2)
        bp3 = bp1.cross(bp2)
        bot = CleverBot.CleverBot("child",
          config.DEFAULT_AI_TIME_LIMIT, bp3)
        info = bot.player_info
        logging.info("player_info %s", info)
        query = """INSERT INTO player (class, info, mu, sigma)
                   VALUES (?, ?, ?, ?)"""
        cursor.execute(query, ("CleverBot", info, DEFAULT_MU,
          DEFAULT_SIGMA))
        # And fetch the player_id.
        query = """SELECT player_id FROM player
                   where class = ? AND info = ?"""
        cursor.execute(query, ("CleverBot", info))
        row = cursor.fetchone()
        player_id = row["player_id"]
        # And update the name.
        name = "ai%d" % player_id
        query = """UPDATE player SET name = ?
                   WHERE player_id = ?"""
        cursor.execute(query, (name, player_id))
        logging.info("father %s %s", player_id1, bp1)
        logging.info("mother %s %s", player_id2, bp2)
        logging.info("baby %s %s %s", player_id, name, bp3)
        return player_id

    def get_weighted_random_player_id(self, excludes=(), highest_mu=False):
        """Return a player_id.  Exclude any player_ids in excludes.

        If there are fewer than GENERATION_SIZE AI player_id in the database,
        add a new AI (by mutating the default) and return its player_id.

        If highest_mu is not None, then return the eligible player_id with
        the highest mu.

        If there are fewer than GENERATION_SIZE AI player_ids in the database
        with sigma <= BREEDING_SIGMA_THRESHOLD, breed a new AI (by
        crossing two parent AIs with sigma <= BREEDING_SIGMA_THRESHOLD,
        chosen randomly weighted by mu), and return its player_id.

        Otherwise, choose an existing player_id randomly, weighted by low
        sigma, and return it.
        """
        with self.connection:
            cursor = self.connection.cursor()
            total_ai_count = 0

            query = """SELECT player_id, mu, sigma FROM player p
                       WHERE p.class='CleverBot'"""
            cursor.execute(query)
            rows = cursor.fetchall()
            young_player_ids = set()
            old_player_ids = set()
            for row in rows:
                player_id = row["player_id"]
                sigma = row["sigma"]
                if sigma <= BREEDING_SIGMA_THRESHOLD:
                    old_player_ids.add(player_id)
                else:
                    young_player_ids.add(player_id)
            young_ai_count = len(young_player_ids)
            old_ai_count = len(old_player_ids)
            total_ai_count = young_ai_count + old_ai_count

            if highest_mu:
                # Pick the eligible AI with the highest mu and return its
                # player_id.
                query = """SELECT player_id, mu FROM player
                           WHERE class = 'CleverBot'
                           ORDER BY mu DESC"""
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    player_id = row["player_id"]
                    if player_id not in excludes:
                        logging.info("picked high-mu AI %s", player_id)
                        return player_id

            if young_ai_count < GENERATION_SIZE and old_ai_count >= 2:
                # Not enough young AIs, so breed one.
                return self._breed_new_ai(cursor, old_player_ids)

            else:
                candidates = []
                # Pick an existing young AI randomly, weighted by low sigma,
                # and return its player_id.
                query = """SELECT player_id, sigma FROM player
                           WHERE class = 'CleverBot'"""
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    player_id = row["player_id"]
                    sigma = row["sigma"]
                    if (player_id in young_player_ids and player_id not in
                      excludes):
                        candidates.append((1.0 / sigma, player_id))
                if candidates:
                    tup = Dice.weighted_random_choice(candidates)
                    player_id = tup[1]
                    logging.info("picked random AI %s", player_id)
                    return player_id
                else:
                    # No eligible AIs available, so either breed or spawn
                    # a new one.
                    if total_ai_count < GENERATION_SIZE:
                        return self._spawn_new_ai(cursor)
                    elif old_ai_count >= 2:
                        return self._breed_new_ai(cursor, old_player_ids)
                    else:
                        return self._spawn_new_ai(cursor)
