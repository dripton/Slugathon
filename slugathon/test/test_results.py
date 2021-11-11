__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import tempfile
import os
import time
import sqlite3

from slugathon.net import Results
from slugathon.game import Game


def test_db_creation():
    with tempfile.NamedTemporaryFile(prefix="slugathon", suffix=".db",
                                     delete=True) as tmp_file:
        db_path = tmp_file.name
        Results.Results(db_path=db_path)
        assert os.path.getsize(db_path) > 0


def test_save_game_and_get_ranking():
    with tempfile.NamedTemporaryFile(prefix="slugathon", suffix=".db",
                                     delete=True) as tmp_file:
        db_path = tmp_file.name
        results = Results.Results(db_path=db_path)
        now = time.time()
        game = Game.Game("g1", "p1", now, now, 2, 6)
        game.add_player("p2")
        player0 = game.players[0]
        player1 = game.players[1]
        game.finish_time = game.start_time + 5
        game.finish_order = [(player0, ), (player1, )]
        results.save_game(game)
        assert os.path.getsize(db_path) > 0

        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = "SELECT * FROM game"
        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row["name"] == game.name
        assert row["start_time"] == int(game.start_time)
        assert row["finish_time"] == int(game.finish_time)

        query = """SELECT * FROM player ORDER BY name"""
        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 2
        row = rows[0]
        assert row["name"] == "p1"
        assert row["class"] == "Human"
        assert row["info"] == "p1"
        row = rows[1]
        assert row["name"] == "p2"
        assert row["class"] == "Human"
        assert row["info"] == "p2"

        query = """SELECT g.name as gname, p.name as pname, rank
                   FROM game g, player p, rank r
                   WHERE g.game_id = r.game_id
                   AND p.player_id = r.player_id
                   ORDER BY r.rank"""
        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 2
        row = rows[0]
        assert row["pname"] == "p1"
        assert row["rank"] == 1
        row = rows[1]
        assert row["pname"] == "p2"
        assert row["rank"] == 2

        ranking1 = results.get_ranking("p1")
        ranking2 = results.get_ranking("p2")
        print(ranking1)
        print(ranking2)
        assert ranking1.mu > 25. > ranking2.mu
        assert ranking1.sigma < 25. / 3
        assert ranking2.sigma < 25. / 3
        assert ranking1.skill > ranking2.skill > 0

        player_data = results.get_player_data()
        assert len(player_data) == 2
        pd1 = player_data[0]
        assert pd1["player_id"] == 1
        assert pd1["name"] == "p1"
        assert pd1["class"] == "Human"
        assert pd1["info"] == "p1"
        assert 29 < pd1["mu"] < 30
        assert 7 < pd1["sigma"] < 8
        assert pd1["skill"] == 7
        pd2 = player_data[1]
        assert pd2["player_id"] == 2
        assert pd2["name"] == "p2"
        assert pd2["class"] == "Human"
        assert pd2["info"] == "p2"
        assert 20 < pd2["mu"] < 21
        assert 7 < pd2["sigma"] < 8
        assert pd2["skill"] == 1
