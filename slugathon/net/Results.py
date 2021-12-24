from __future__ import annotations

import logging
import math
import os
import sqlite3
from collections import namedtuple
from typing import Dict, List, Optional, Set, Tuple

import trueskill

from slugathon.ai import BotParams, CleverBot
from slugathon.game import Game
from slugathon.net import config
from slugathon.util import Dice, prefs

__copyright__ = "Copyright (c) 2012-2021 David Ripton"
__license__ = "GNU GPL v2"


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
    def skill(self) -> int:
        """Return an integer rating based on mu - 3 * sigma, at least 1."""
        return max(1, int(math.floor(self.mu - 3 * self.sigma)))

    def __repr__(self) -> str:
        return f"Ranking: mu={self.mu} sigma={self.sigma} skill={self.skill}"


class Results(object):

    """Game results tracking using a sqlite database."""

    def __init__(self, db_path: str = DB_PATH):
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

    def enable_foreign_keys(self) -> None:
        query = "PRAGMA foreign_keys = ON"
        self.connection.execute(query)

    def create_db(self) -> None:
        self.connection.executescript(ddl)

    def save_game(self, game: Game.Game) -> None:
        """Save a finished Game to the results database.

        XXX This involves a non-trivial amount of computation and I/O, so
        maybe it should be run from a thread to avoid blocking the reactor.
        But sqlite is not thread-safe so we can't reuse connections.
        """
        logging.info("")
        assert game.finish_time is not None
        with self.connection:
            cursor = self.connection.cursor()
            for player in game.players:
                logging.info(f"{player.player_class} {player.player_info}")

                # See if that player is already in the database
                query = """SELECT player_id FROM player
                           where name = ? AND class = ?"""
                cursor.execute(query, (player.name, player.player_class))
                row = cursor.fetchone()
                # If not, insert it.
                if row is None:
                    query = """INSERT INTO player
                               (name, class, info, mu, sigma)
                               VALUES (?, ?, ?, ?, ?)"""
                    cursor.execute(
                        query,
                        (
                            player.name,
                            player.player_class,
                            player.player_info,
                            DEFAULT_MU,
                            DEFAULT_SIGMA,
                        ),
                    )
                    # And fetch the player_id.
                    query = """SELECT player_id FROM player
                               where class = ? AND info = ?"""
                    cursor.execute(
                        query, (player.player_class, player.player_info)
                    )
                    row = cursor.fetchone()
                else:
                    player_id = row["player_id"]
                    # We may need to update info, if new fields were added.
                    query = """UPDATE player SET info = ?
                               where player_id = ?"""
                    cursor.execute(query, (player.player_info, player_id))

                player_id = row["player_id"]

            # Add the game.
            query = """INSERT INTO game (name, start_time, finish_time)
                       VALUES (?, ?, ?)"""
            cursor.execute(
                query, (game.name, int(game.start_time), int(game.finish_time))
            )
            # Find the game_id for the just-inserted game.
            query = """SELECT game_id FROM game WHERE
                       name = ? AND start_time = ? AND finish_time = ?"""
            cursor.execute(
                query, (game.name, int(game.start_time), int(game.finish_time))
            )
            row = cursor.fetchone()
            game_id = row["game_id"]
            rank = 1
            for tup in game.finish_order:
                for player in tup:
                    # Find the player_id
                    query = """SELECT player_id FROM player
                               WHERE name = ? AND class = ? AND info = ?"""
                    cursor.execute(
                        query,
                        (player.name, player.player_class, player.player_info),
                    )
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
            cursor.execute(query, (game_id,))
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
                rating_tuples.append((rating,))
            rating_tuples2 = trueskill.rate(rating_tuples, ranks)
            while player_ids:
                player_id = player_ids.pop()
                rating = rating_tuples2.pop()[0]
                mu = rating.mu
                sigma = rating.sigma
                query = """UPDATE player set mu = ?, sigma = ?
                           WHERE player_id = ?"""
                cursor.execute(query, (mu, sigma, player_id))
        logging.info("")

    def get_ranking(self, playername: str) -> Ranking:
        """Return a Ranking object for one player name.

        If the player is not found, return default values.
        """
        with self.connection:
            cursor = self.connection.cursor()
            query = "SELECT mu, sigma FROM player WHERE name = ?"
            cursor.execute(query, (playername,))
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

    def get_player_info(self, player_id: int) -> Optional[str]:
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

    def get_player_id(self, player_info: str) -> Optional[int]:
        """Return the player_id for player_info, from the database."""
        with self.connection:
            cursor = self.connection.cursor()
            # See if that player is already in the database
            query = "SELECT player_id FROM player where info = ?"
            cursor.execute(query, (player_info,))
            row = cursor.fetchone()
            if row is None:
                logging.debug("returning None")
                return None
            return row["player_id"]

    def get_player_data(self) -> List[Dict]:
        """Return a list with one dict of data per player in the database."""
        data = []
        with self.connection:
            cursor = self.connection.cursor()
            query = """SELECT player_id, name, class, info, mu, sigma
                       FROM player ORDER BY player_id"""
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

    def get_game_info_tuples(
        self, num: int = 100
    ) -> List[
        Tuple[
            str,
            float,
            float,
            int,
            int,
            List[str],
            bool,
            Optional[float],
            List[str],
            List[str],
        ]
    ]:
        """Return a list of Game.info_tuple for the most recent num games."""
        results = []
        with self.connection:
            cursor = self.connection.cursor()
            cursor2 = self.connection.cursor()
            query = """SELECT game_id, name, start_time, finish_time
                       FROM game
                       ORDER BY game_id DESC
                       LIMIT ?"""
            cursor.execute(query, (num,))
            rows = cursor.fetchall()
            for row in rows:
                game_id = row["game_id"]
                name = row["name"]
                start_time = row["start_time"]
                finish_time = row["finish_time"]
                query2 = """SELECT p.name, r.rank
                            FROM rank r, player p
                            WHERE r.game_id = ? AND r.player_id = p.player_id
                            ORDER BY r.rank"""
                cursor2.execute(query2, (game_id,))
                rows2 = cursor2.fetchall()
                num_players = 0
                winner_names = []
                loser_names = []
                for row2 in rows2:
                    num_players += 1
                    player_name = row2["name"]
                    rank = row2["rank"]
                    if rank == 1:
                        winner_names.append(player_name)
                    else:
                        loser_names.append(player_name)
                # We don't save create_time so reuse start_time.
                info_tuple = (
                    name,
                    start_time,
                    start_time,
                    num_players,
                    num_players,
                    winner_names + loser_names,
                    True,
                    finish_time,
                    winner_names,
                    loser_names,
                )
                results.append(info_tuple)
        results.reverse()
        return results

    def _spawn_new_ai(self, cursor: sqlite3.Cursor) -> int:
        """Spawn a new AI, mutated from default_bot_params, and return
        its player_id."""
        bp = BotParams.default_bot_params.mutate_all_fields()
        bot = CleverBot.CleverBot("spawn", config.DEFAULT_AI_TIME_LIMIT, bp)
        info = bot.player_info
        logging.info(f"player_info {info}")
        query = """INSERT INTO player (class, info, mu, sigma)
                   VALUES (?, ?, ?, ?)"""
        cursor.execute(query, ("CleverBot", info, DEFAULT_MU, DEFAULT_SIGMA))
        # And fetch the player_id.
        query = """SELECT player_id FROM player
                   where class = ? AND info = ?"""
        cursor.execute(query, ("CleverBot", info))
        row = cursor.fetchone()
        player_id = row["player_id"]
        # And update the name.
        name = f"ai{player_id}"
        query = """UPDATE player SET name = ?
                   WHERE player_id = ?"""
        cursor.execute(query, (name, player_id))
        logging.info(f"spawning new AI {player_id} {name} {bp}")
        return player_id

    def _breed_new_ai(
        self, cursor: sqlite3.Cursor, old_player_ids: Set[int]
    ) -> int:
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
        assert info1 is not None
        bp1 = BotParams.BotParams.fromstring(info1)
        player_id2 = tup2[1]
        info2 = self.get_player_info(player_id2)
        assert info2 is not None
        bp2 = BotParams.BotParams.fromstring(info2)
        assert bp1 is not None
        assert bp2 is not None
        bp3 = bp1.cross(bp2).mutate_random_field()
        bot = CleverBot.CleverBot("child", config.DEFAULT_AI_TIME_LIMIT, bp3)
        info = bot.player_info
        logging.info(f"player_info {info}")
        query = """INSERT INTO player (class, info, mu, sigma)
                   VALUES (?, ?, ?, ?)"""
        cursor.execute(query, ("CleverBot", info, DEFAULT_MU, DEFAULT_SIGMA))
        # And fetch the player_id.
        query = """SELECT player_id FROM player
                   where class = ? AND info = ?"""
        cursor.execute(query, ("CleverBot", info))
        row = cursor.fetchone()
        player_id = row["player_id"]
        # And update the name.
        name = f"ai{player_id}"
        query = """UPDATE player SET name = ?
                   WHERE player_id = ?"""
        cursor.execute(query, (name, player_id))
        logging.info(f"father {player_id1} {bp1}")
        logging.info(f"mother {player_id2} {bp2}")
        logging.info(f"baby {player_id} {name} {bp3}")
        return player_id

    def get_weighted_random_player_id(
        self, excludes: Set = set(), highest_mu: bool = False
    ) -> int:
        """Return a player_id.  Exclude any player_ids in excludes.

        If there are fewer than GENERATION_SIZE AI player_id in the database,
        add a new AI (by mutating the default) and return its player_id.

        If highest_mu is True, then return the eligible player_id with
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
                        logging.info(f"picked high-mu AI {player_id=}")
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
                    if (
                        player_id in young_player_ids
                        and player_id not in excludes
                    ):
                        candidates.append((1.0 / sigma, player_id))
                if candidates:
                    tup = Dice.weighted_random_choice(candidates)
                    player_id = tup[1]
                    logging.info(f"picked random AI {player_id=}")
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
