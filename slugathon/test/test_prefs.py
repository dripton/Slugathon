import getpass
import os
import shutil
from typing import Any

from slugathon.net import config
from slugathon.util import Dice, prefs

__copyright__ = "Copyright (c) 2009-2011 David Ripton"
__license__ = "GNU GPL v2"


playername = "unittest"
window_name = "GUIMasterBoard"


def test_save_load_window_position() -> None:
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_window_position(playername, window_name, x1, y1)
    tup = prefs.load_window_position(playername, window_name)
    assert tup is not None
    x2, y2 = tup
    assert x2 == x1
    assert y2 == y1


def test_save_load_window_size() -> None:
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_window_size(playername, window_name, x1, y1)
    tup = prefs.load_window_size(playername, window_name)
    assert tup is not None
    x2, y2 = tup
    assert x2 == x1
    assert y2 == y1


def test_save_load_global_window_position() -> None:
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_global_window_position(window_name, x1, y1)
    tup = prefs.load_global_window_position(window_name)
    assert tup is not None
    x2, y2 = tup
    assert x2 == x1
    assert y2 == y1


def test_save_load_global_window_size() -> None:
    x1 = Dice.roll()[0]
    y1 = Dice.roll()[0]
    prefs.save_global_window_size(window_name, x1, y1)
    tup = prefs.load_global_window_size(window_name)
    assert tup is not None
    x2, y2 = tup
    assert x2 == x1
    assert y2 == y1


def test_save_server() -> None:
    prefs.save_server("localhost", config.DEFAULT_PORT)
    assert ("localhost", config.DEFAULT_PORT) in prefs.load_servers()


def test_load_servers() -> None:
    entries = prefs.load_servers()
    assert entries
    for entry in entries:
        server, port = entry
        assert type(server) == str
        assert type(port) == int
    assert ("localhost", config.DEFAULT_PORT) in entries


def test_load_playernames() -> None:
    playernames = prefs.load_playernames()
    assert playername in playernames
    assert getpass.getuser() in playernames


def test_passwd_path() -> None:
    assert prefs.passwd_path() == os.path.expanduser(
        "~/.slugathon/globalprefs/passwd"
    )


def teardown_module(module: Any) -> None:
    shutil.rmtree(prefs.player_prefs_dir(playername))
