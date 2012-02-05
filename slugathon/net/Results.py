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

CREATE TABLE player_game_rank (
    player_id INTEGER REFERENCES player(player_id),
    game_id INTEGER REFERENCES game(game_id),
    rank INTEGER  -- rank in the game from 1 (winner) through 6.  Ties okay.
);

CREATE TABLE player_trueskill (
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
        exists = os.path.exists(db_path)
        self.connection = sqlite3.connect(db_path)
        self.enable_foreign_keys()
        if not exists:
            self.create_db()

    def enable_foreign_keys(self):
        with self.connection:
            cursor = self.connection.cursor()
            query = "PRAGMA foreign_keys = ON"
            cursor.execute(query)

    def create_db(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(ddl)

    def save_game(self, game):
        with self.connection:
            cursor = self.connection.cursor()
            for player in game.players:
                name = player.name
                player_type = player.player_type
                result_info = player.result_info
                query = "SELECT * FROM player WHERE name = ? AND type = ?"
                cursor.execute(query, name, player_type)
                row = cursor.fetchone()
                if row is None:
                    query = \
                      "INSERT INTO player(name, type, info) VALUES (?, ?, ?)"
                    cursor.execute(query, name, player_type, result_info)
            query = """"INSERT INTO game(name, start_time, finish_time)
                        VALUES (?, ?, ?)"""
            cursor.execute(query, game.name, game.start_time, game.finish_time)
            # TODO Add Game.finish_order
