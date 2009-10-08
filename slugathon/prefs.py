"""Saving and loading preferences."""

__copyright__ = "Copyright (c) 2008 David Ripton"
__license__ = "GNU GPL v2"


import os
import getpass

import Server


SLUGATHON_DIR = os.path.expanduser("~/.slugathon/")
PREFS_DIR = os.path.join(SLUGATHON_DIR, "prefs")
GLOBAL_PREFS_DIR = os.path.join(SLUGATHON_DIR, "globalprefs")
SAVE_DIR = os.path.join(SLUGATHON_DIR, "save")


def player_prefs_dir(playername):
    """Return the path to the player prefs directory for playername."""
    return os.path.join(PREFS_DIR, playername)

def window_position_path(playername, window_name):
    """Return the path to the window position prefs file."""
    return os.path.join(player_prefs_dir(playername), window_name +
      "_position")

def save_window_position(playername, window_name, x, y):
    """Save (x, y) as a preferred window position."""
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    with open(window_position_path(playername, window_name), "w") as fil:
        fil.write("%d\n" % x)
        fil.write("%d\n" % y)

def load_window_position(playername, window_name):
    """Return a preferred window position as (x, y)."""
    try:
        with open(window_position_path(playername, window_name)) as fil:
            tokens = fil.read().split()
        x = int(tokens[0])
        y = int(tokens[1])
        return x, y
    except (OSError, IOError, ValueError):
        return None

def window_size_path(playername, window_name):
    """Return the path to the window size prefs file."""
    return os.path.join(player_prefs_dir(playername), window_name + "_size")

def save_window_size(playername, window_name, width, height):
    """Save (width, height) as a preferred window size."""
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    with open(window_size_path(playername, window_name), "w") as fil:
        fil.write("%d\n" % width)
        fil.write("%d\n" % height)

def load_window_size(playername, window_name):
    """Return a preferred window size as (width, height)."""
    try:
        with open(window_size_path(playername, window_name)) as fil:
            tokens = fil.read().split()
        width = int(tokens[0])
        height = int(tokens[1])
        return width, height
    except (OSError, IOError, ValueError):
        return None

def server_path():
    """Return the path to the file that holds known servers and ports.."""
    return os.path.join(GLOBAL_PREFS_DIR, "servers")

def load_servers():
    """Return a list of (str server_name, int server_port) tuples."""
    server_entries = set()
    server_entries.add(("localhost", Server.DEFAULT_PORT))
    if not os.path.exists(server_path()):
        return sorted(server_entries)
    with open(server_path()) as fil:
        st = fil.read()
    lines = st.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line:
            host, port = line.split(":")
            server_entries.add((host, int(port)))
    return sorted(server_entries)

def save_server(server_name, server_port):
    """Add server_name and server_port to the list of known servers."""
    if not os.path.exists(GLOBAL_PREFS_DIR):
        os.makedirs(GLOBAL_PREFS_DIR)
    server_entries = set(load_servers())
    server_entries.add((server_name, int(server_port)))
    with open(server_path(), "w") as fil:
        for host, port in sorted(server_entries):
            fil.write("%s:%d\n" % (host, port))

def load_playernames():
    """Return a sorted list of known player names."""
    playernames = set()
    playernames.add(getpass.getuser())
    if os.path.exists(PREFS_DIR):
        for fn in os.listdir(PREFS_DIR):
            path = os.path.join(PREFS_DIR, fn)
            if os.path.isdir(path):
                playernames.add(fn)
    return sorted(playernames)
