"""Saving and loading preferences."""

__copyright__ = "Copyright (c) 2008 David Ripton"
__license__ = "GNU GPL v2"


import os


SLUGATHON_DIR = os.path.expanduser("~/.slugathon/")
PREFS_DIR = os.path.join(SLUGATHON_DIR, "prefs")
SAVE_DIR = os.path.join(SLUGATHON_DIR, "save")


def player_prefs_dir(playername):
    return os.path.join(PREFS_DIR, playername)

def window_position_path(playername, window_name):
    return os.path.join(player_prefs_dir(playername), window_name +
      "_position")

def save_window_position(playername, window_name, x, y):
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    fil = open(window_position_path(playername, window_name), "w")
    fil.write("%d\n" % x)
    fil.write("%d\n" % y)
    fil.close()

def load_window_position(playername, window_name):
    try:
        fil = open(window_position_path(playername, window_name))
        tokens = fil.read().split()
        fil.close()
        x = int(tokens[0])
        y = int(tokens[1])
        return x, y
    except (OSError, ValueError):
        return None

def window_size_path(playername, window_name):
    return os.path.join(player_prefs_dir(playername), window_name + "_size")

def save_window_size(playername, window_name, x, y):
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    fil = open(window_size_path(playername, window_name), "w")
    fil.write("%d\n" % x)
    fil.write("%d\n" % y)
    fil.close()

def load_window_size(playername, window_name):
    try:
        fil = open(window_size_path(playername, window_name))
        tokens = fil.read().split()
        fil.close()
        x = int(tokens[0])
        y = int(tokens[1])
        return x, y
    except (OSError, ValueError):
        return None
