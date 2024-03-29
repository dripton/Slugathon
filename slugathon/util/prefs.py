import getpass
import os
from typing import Dict, List, Optional, Tuple

from slugathon.net import config

__copyright__ = "Copyright (c) 2008-2012 David Ripton"
__license__ = "GNU GPL v2"


"""Saving and loading preferences."""


SLUGATHON_DIR = os.path.expanduser(os.path.join("~", ".slugathon"))
PREFS_DIR = os.path.join(SLUGATHON_DIR, "prefs")
GLOBAL_PREFS_DIR = os.path.join(SLUGATHON_DIR, "globalprefs")
SAVE_DIR = os.path.join(SLUGATHON_DIR, "save")
RESULTS_DIR = os.path.join(SLUGATHON_DIR, "results")

SAVE_GLOB = "*.save"

AUTO_STRIKE_SINGLE_TARGET = "Auto strike single target"
AUTO_RANGESTRIKE_SINGLE_TARGET = "Auto rangestrike single target"
AUTO_CARRY_TO_SINGLE_TARGET = "Auto carry to single target"


def player_prefs_dir(playername: str) -> str:
    """Return the path to the player prefs directory for playername."""
    if playername is None:
        playername = getpass.getuser()
    return os.path.join(PREFS_DIR, playername)


def window_position_path(playername: str, window_name: str) -> str:
    """Return the path to the window position prefs file."""
    return os.path.join(
        player_prefs_dir(playername), window_name + "_position"
    )


def save_window_position(
    playername: str, window_name: str, x: int, y: int
) -> None:
    """Save (x, y) as a preferred window position."""
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    with open(window_position_path(playername, window_name), "w") as fil:
        fil.write(f"{x}\n")
        fil.write(f"{y}\n")


def load_window_position(
    playername: str, window_name: str
) -> Optional[Tuple[int, int]]:
    """Return a preferred window position as (x, y)."""
    try:
        with open(window_position_path(playername, window_name)) as fil:
            tokens = fil.read().split()
        x = int(tokens[0])
        y = int(tokens[1])
        return x, y
    except (OSError, IOError, ValueError):
        return None


def window_size_path(playername: str, window_name: str) -> str:
    """Return the path to the window size prefs file."""
    return os.path.join(player_prefs_dir(playername), window_name + "_size")


def save_window_size(
    playername: str, window_name: str, width: int, height: int
) -> None:
    """Save (width, height) as a preferred window size."""
    if not os.path.exists(player_prefs_dir(playername)):
        os.makedirs(player_prefs_dir(playername))
    with open(window_size_path(playername, window_name), "w") as fil:
        fil.write(f"{width}\n")
        fil.write(f"{height}\n")


def load_window_size(
    playername: str, window_name: str
) -> Optional[Tuple[int, int]]:
    """Return a preferred window size as (width, height)."""
    try:
        with open(window_size_path(playername, window_name)) as fil:
            tokens = fil.read().split()
        width = int(tokens[0])
        height = int(tokens[1])
        return width, height
    except (OSError, IOError, ValueError):
        return None


def global_window_position_path(window_name: str) -> str:
    """Return the path to the window position prefs file."""
    return os.path.join(GLOBAL_PREFS_DIR, window_name + "_position")


def save_global_window_position(window_name: str, x: int, y: int) -> None:
    """Save (x, y) as a preferred window position."""
    if not os.path.exists(GLOBAL_PREFS_DIR):
        os.makedirs(GLOBAL_PREFS_DIR)
    with open(global_window_position_path(window_name), "w") as fil:
        fil.write(f"{x}\n")
        fil.write(f"{y}\n")


def load_global_window_position(window_name: str) -> Optional[Tuple[int, int]]:
    """Return a preferred window position as (x, y)."""
    try:
        with open(global_window_position_path(window_name)) as fil:
            tokens = fil.read().split()
        x = int(tokens[0])
        y = int(tokens[1])
        return x, y
    except (OSError, IOError, ValueError):
        return None


def global_window_size_path(window_name: str) -> str:
    """Return the path to the window size prefs file."""
    return os.path.join(GLOBAL_PREFS_DIR, window_name + "_size")


def save_global_window_size(window_name: str, width: int, height: int) -> None:
    """Save (width, height) as a preferred window size."""
    if not os.path.exists(GLOBAL_PREFS_DIR):
        os.makedirs(GLOBAL_PREFS_DIR)
    with open(global_window_size_path(window_name), "w") as fil:
        fil.write(f"{width}\n")
        fil.write(f"{height}\n")


def load_global_window_size(window_name: str) -> Optional[Tuple[int, int]]:
    """Return a preferred window size as (width, height)."""
    try:
        with open(global_window_size_path(window_name)) as fil:
            tokens = fil.read().split()
        width = int(tokens[0])
        height = int(tokens[1])
        return width, height
    except (OSError, IOError, ValueError):
        return None


def option_path(playername: str, option: str) -> str:
    return os.path.join(player_prefs_dir(playername), option)


def save_bool_option(playername: str, option: str, value: str) -> None:
    with open(option_path(playername, option), "w") as fil:
        fil.write(f"{value}\n")


def load_bool_option(playername: str, option: str) -> Optional[bool]:
    try:
        with open(option_path(playername, option)) as fil:
            tokens = fil.read().split()
            value = bool(tokens[0])
            return value
    except (OSError, IOError, ValueError, AttributeError):
        return None


def server_path() -> str:
    """Return the path to the file that holds known servers and ports.."""
    return os.path.join(GLOBAL_PREFS_DIR, "servers")


def last_server_path() -> str:
    """Return the path to the file that holds the last used server:port."""
    return os.path.join(GLOBAL_PREFS_DIR, "last_server")


def passwd_path() -> str:
    """Return the path to the file that holds playernames and passwords.."""
    return os.path.join(GLOBAL_PREFS_DIR, "passwd")


def load_servers() -> List[Tuple[str, int]]:
    """Return a list of (str server_name, int server_port) tuples."""
    server_entries = set()
    server_entries.add(("localhost", config.DEFAULT_PORT))
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


def load_last_server() -> Tuple[str, int]:
    """Return the last (str server_name, int server_port) used, or
    the default if there are none."""
    if os.path.exists(last_server_path()):
        with open(last_server_path()) as fil:
            for line in fil:
                line = line.strip()
                if line:
                    host, port = line.split(":")
                    return (host, int(port))
    return ("localhost", config.DEFAULT_PORT)


def save_server(server_name: str, server_port: int) -> None:
    """Add server_name and server_port to the list of known servers,
    and save it as the last server used."""
    if not os.path.exists(GLOBAL_PREFS_DIR):
        os.makedirs(GLOBAL_PREFS_DIR)
    server_entries = set(load_servers())
    server_entries.add((server_name, int(server_port)))
    with open(server_path(), "w") as fil:
        for host, port in sorted(server_entries):
            fil.write(f"{host}:{port}\n")
    with open(last_server_path(), "w") as fil:
        fil.write(f"{server_name}:{int(server_port)}\n")


def load_playernames() -> List[str]:
    """Return a sorted list of known player names."""
    playernames = set()
    playernames.add(getpass.getuser())
    if os.path.exists(PREFS_DIR):
        for fn in os.listdir(PREFS_DIR):
            path = os.path.join(PREFS_DIR, fn)
            if os.path.isdir(path):
                playernames.add(fn)
    return sorted(playernames)


def last_playername_path() -> str:
    """Return the path to the file that holds the last playername."""
    return os.path.join(GLOBAL_PREFS_DIR, "last_player")


def last_playername() -> str:
    """Return the last player name used, or "" if none."""
    if os.path.exists(last_playername_path()):
        with open(last_playername_path()) as fil:
            line = fil.read().strip()
            return line
    return ""


def save_last_playername(playername: str) -> None:
    if not os.path.exists(GLOBAL_PREFS_DIR):
        os.makedirs(GLOBAL_PREFS_DIR)
    with open(last_playername_path(), "w") as fil:
        fil.write(f"{playername}\n")
