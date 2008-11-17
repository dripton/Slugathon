import shutil
import getpass

import prefs
import Dice
import Server

playername = "unittest"
window_name = "GUIMasterBoard"

def test_save_load_window_position():
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_window_position(playername, window_name, x1, y1)
    x2, y2 = prefs.load_window_position(playername, window_name)
    assert x2 == x1
    assert y2 == y1

def test_save_load_window_size():
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_window_size(playername, window_name, x1, y1)
    x2, y2 = prefs.load_window_size(playername, window_name)
    assert x2 == x1
    assert y2 == y1

def test_save_server():
    prefs.save_server("localhost", Server.DEFAULT_PORT)
    assert ("localhost", Server.DEFAULT_PORT) in prefs.load_servers()

def test_load_servers():
    entries = prefs.load_servers()
    assert entries
    for entry in entries:
        server, port = entry
        assert type(server) == str
        assert type(port) == int
    assert ("localhost", Server.DEFAULT_PORT) in entries

def test_load_playernames():
    playernames = prefs.load_playernames()
    assert playername in playernames
    assert getpass.getuser() in playernames

def teardown_module(module):
    shutil.rmtree(prefs.player_prefs_dir(playername))
