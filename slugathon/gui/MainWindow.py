#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, Optional

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log

from slugathon.gui import (
    ConfirmDialog,
    GUIBattleMap,
    GUIMasterBoard,
    Lobby,
    icon,
)
from slugathon.util import prefs


__copyright__ = "Copyright (c) 2012-2021 David Ripton"
__license__ = "GNU GPL v2"


def modify_fg_all_states(widget: Gtk.Widget, color_name: str) -> None:
    color = Gdk.color_parse(color_name)
    for state in [
        Gtk.StateType.NORMAL,
        Gtk.StateType.ACTIVE,
        Gtk.StateType.PRELIGHT,
        Gtk.StateType.SELECTED,
        Gtk.StateType.INSENSITIVE,
    ]:
        widget.modify_fg(state, color)


class MainWindow(Gtk.Window):

    """Main GUI window."""

    def __init__(self, playername: str = None, scale: int = None):
        GObject.GObject.__init__(self)

        self.playername = playername
        self.game = None
        self.lobby = None  # type: Optional[Lobby.Lobby]
        self.guiboard = None  # type: Optional[GUIMasterBoard.GUIMasterBoard]
        self.guimap = None  # type: Optional[GUIBattleMap.GUIBattleMap]
        self.accel_group = None

        self.set_icon(icon.pixbuf)
        self.set_title(f"Slugathon - {self.playername}")
        self.connect("delete-event", self.cb_delete_event)
        self.connect("destroy", self.cb_destroy)
        self.connect("configure-event", self.cb_configure_event)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        # TODO
        self.set_default_size(1024, 768)

        if self.playername:
            tup = prefs.load_window_position(
                self.playername, self.__class__.__name__
            )
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(
                self.playername, self.__class__.__name__
            )
            if tup:
                width, height = tup
                self.resize(width, height)

        self.notebook = Gtk.Notebook()
        self.notebook.connect("switch-page", self.cb_switch_page)
        self.add(self.notebook)
        self.notebook.set_tab_pos(Gtk.PositionType.BOTTOM)
        self.show_all()

    def replace_accel_group(self, accel_group: Gtk.AccelGroup) -> None:
        if self.accel_group is not None:
            self.remove_accel_group(self.accel_group)
        self.accel_group = accel_group
        if accel_group is not None:
            self.add_accel_group(accel_group)

    def add_lobby(self, lobby: Lobby.Lobby) -> None:
        self.lobby = lobby
        label = Gtk.Label(label="Lobby")
        self.notebook.prepend_page(lobby, label)
        self.show_all()

    def add_guiboard(self, guiboard: GUIMasterBoard.GUIMasterBoard) -> None:
        self.guiboard = guiboard
        label = Gtk.Label(label="MasterBoard")
        modify_fg_all_states(label, "Red")
        self.notebook.append_page(guiboard, label)
        self.show_all()

    def remove_guiboard(self) -> None:
        if self.guiboard:
            page_num = self.notebook.page_num(self.guiboard)
            self.notebook.remove_page(page_num)
            self.guiboard = None

    def add_guimap(self, guimap: GUIBattleMap.GUIBattleMap) -> None:
        self.guimap = guimap
        label = Gtk.Label(label="BattleMap")
        modify_fg_all_states(label, "Red")
        self.notebook.append_page(guimap, label)
        self.show_all()

    def remove_guimap(self) -> None:
        if self.guimap:
            accel_group = self.guimap.ui.get_accel_group()
            self.remove_accel_group(accel_group)
            page_num = self.notebook.page_num(self.guimap)
            self.notebook.remove_page(page_num)
            self.guimap = None

    def highlight_lobby_label(self) -> None:
        if self.lobby:
            label = self.notebook.get_tab_label(self.lobby)
            modify_fg_all_states(label, "Red")

    def cb_delete_event(self, widget: Gtk.Widget, event: Gdk.Event) -> bool:
        if self.game is None or self.game.over:
            self.cb_destroy(True)
        else:
            confirm_dialog, def1 = ConfirmDialog.new(
                self, "Confirm", "Are you sure you want to quit?"
            )
            def1.addCallback(self.cb_destroy)
            def1.addErrback(self.failure)
        return True

    def cb_destroy(self, confirmed: bool) -> None:
        """Withdraw from the game, and destroy the window."""
        if confirmed:
            self.destroyed = True
            if self.game:
                def1 = self.user.callRemote("withdraw", self.game.name)
                def1.addErrback(self.failure)
            self.destroy()

    def cb_configure_event(
        self, event: MainWindow, unused: Gdk.EventConfigure
    ) -> bool:
        if self.playername:
            x, y = self.get_position()
            prefs.save_window_position(
                self.playername, self.__class__.__name__, x, y
            )
            width, height = self.get_size()
            prefs.save_window_size(
                self.playername, self.__class__.__name__, width, height
            )
        return False

    def cb_switch_page(
        self, widget: Gtk.Widget, dummy: Gtk.EventBox, page_num: int
    ) -> None:
        logging.debug(f"{dummy=}")
        page_widget = widget.get_nth_page(page_num)
        if hasattr(page_widget, "ui") and hasattr(
            page_widget.ui, "get_accel_group"
        ):
            self.replace_accel_group(page_widget.ui.get_accel_group())
        else:
            self.replace_accel_group(None)
        label = self.notebook.get_tab_label(page_widget)
        modify_fg_all_states(label, "Black")

    def compute_scale(self) -> int:
        """Return the approximate maximum scale that let the board fit on
        the screen."""
        # TODO
        return 15

    def failure(self, arg: Any) -> None:
        log.err(arg)  # type: ignore


if __name__ == "__main__":
    import time
    from slugathon.game import Game
    from slugathon.util.NullUser import NullUser

    now = time.time()
    user = NullUser()
    playername = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    playernames = {playername}
    games = [game]
    main_window = MainWindow()
    lobby = Lobby.Lobby(user, playername, playernames, games, main_window)
    main_window.add_lobby(lobby)

    reactor.run()  # type: ignore[attr-defined]
