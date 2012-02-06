__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import os
import sqlite3

from slugathon.util import prefs


DB_PATH = os.path.join(prefs.RESULTS_DIR, "slugathon.db")


ddl = """
CREATE TABLE game (
    game_id INTEGER PRIMARY KEY ASC,
    name TEXT,
    start_time INTEGER,
    finish_time INTEGER
);

CREATE TABLE player (
    player_id INTEGER PRIMARY KEY ASC,
    name TEXT,    -- only used for Human
    type TEXT,    -- "Human", "CleverBot", etc.
    info TEXT     -- any info that distinguishes AIs of the same type
);

CREATE TABLE rank (
    player_id INTEGER REFERENCES player(player_id),
    game_id INTEGER REFERENCES game(game_id),
    rank INTEGER  -- rank in the game from 1 (winner) through 6.  Ties okay.
);

CREATE TABLE trueskill (
    player_id INTEGER REFERENCES player(player_id),
    mu REAL,
    sigma REAL,
    trueskill REAL,
    through_game_id INTEGER REFERENCES game(game_id)
);
"""


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

        TODO This involves a non-trivial amount of computation and I/O, so
        perhaps it should be run from a thread.
        """
        with self.connection:
            cursor = self.connection.cursor()
            for player in game.players:
                # See if that player is already in the database
                #name = player.name if player.player_type == "Human" else ""
                # XXX Temporarily use name for AI, to avoid duplicates.
                name = player.name
                query = """SELECT player_id FROM player
                           WHERE name = ? AND type = ? AND info = ?"""
                cursor.execute(query, (name, player.player_type,
                  player.result_info))
                row = cursor.fetchone()
                # If not, insert it.
                if row is None:
                    query = \
                      "INSERT INTO player (name, type, info) VALUES (?, ?, ?)"
                    cursor.execute(query, (name, player.player_type,
                      player.result_info))
            # Add the game.
            query = """INSERT INTO game (name, start_time, finish_time)
                       VALUES (?, ?, ?)"""
            cursor.execute(query, (game.name, int(game.start_time),
              int(game.finish_time)))
            # XXX It should not be needed to commit halfway through like this.
            self.connection.commit()
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
                               WHERE name = ? AND type = ? AND info = ?"""
                    # XXX Temporarily use name for AI, to avoid duplicates.
                    name = player.name
                    cursor.execute(query, (name, player.player_type,
                      player.result_info))
                    row = cursor.fetchone()
                    player_id = row["player_id"]
                    # Add to rank.
                    query = \
                      """INSERT INTO rank(player_id, game_id, rank)
                         VALUES (?, ?, ?)"""
                    cursor.execute(query, (player_id, game_id, rank))
                rank += len(tup)
