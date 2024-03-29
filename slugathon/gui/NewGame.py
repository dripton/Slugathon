#!/usr/bin/env python3

import logging
from typing import Any, Optional

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from twisted.python import log

from slugathon.gui import InfoDialog, icon
from slugathon.net import User, config
from slugathon.util.NullUser import NullUser


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


class NewGame(Gtk.Dialog):

    """Form new game dialog."""

    def __init__(
        self,
        user: User.User,
        playername: str,
        parent_window: Optional[Gtk.Window],
    ):
        GObject.GObject.__init__(
            self, title=f"Form New Game - {playername}", parent=parent_window
        )
        self.game_name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.playername = playername
        self.parent_window = parent_window

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent_window)
        self.set_destroy_with_parent(True)

        hbox1 = Gtk.HBox()
        self.vbox.pack_start(hbox1, True, True, 0)
        label1 = Gtk.Label(label="Name of game")
        hbox1.pack_start(label1, False, True, 0)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_width_chars(40)
        hbox1.pack_start(self.name_entry, False, True, 0)

        min_adjustment = Gtk.Adjustment(
            value=2,
            lower=2,
            upper=6,
            step_increment=1,
            page_increment=0,
            page_size=0,
        )
        max_adjustment = Gtk.Adjustment(
            value=6,
            lower=2,
            upper=6,
            step_increment=1,
            page_increment=0,
            page_size=0,
        )
        ai_time_limit_adjustment = Gtk.Adjustment(
            value=config.DEFAULT_AI_TIME_LIMIT,
            lower=0.1,
            upper=99.0,
            step_increment=0.1,
            page_increment=1,
            page_size=0,
        )
        player_time_limit_adjustment = Gtk.Adjustment(
            value=config.DEFAULT_PLAYER_TIME_LIMIT,
            lower=1.0,
            upper=999.0,
            step_increment=1,
            page_increment=100,
            page_size=0,
        )

        hbox2 = Gtk.HBox()
        self.vbox.pack_start(hbox2, True, True, 0)
        label2 = Gtk.Label(label="Min players")
        hbox2.pack_start(label2, False, True, 0)
        self.min_players_spin = Gtk.SpinButton(
            adjustment=min_adjustment, climb_rate=1, digits=0
        )
        self.min_players_spin.set_numeric(True)
        self.min_players_spin.set_value(2)
        hbox2.pack_start(self.min_players_spin, False, True, 0)
        label3 = Gtk.Label(label="Max players")
        hbox2.pack_start(label3, False, True, 0)
        self.max_players_spin = Gtk.SpinButton(
            adjustment=max_adjustment, climb_rate=1, digits=0
        )
        self.max_players_spin.set_numeric(True)
        self.max_players_spin.set_value(6)
        hbox2.pack_start(self.max_players_spin, False, True, 0)
        label4 = Gtk.Label(label="AI time limit")
        hbox2.pack_start(label4, False, True, 0)
        self.ai_time_limit_spin = Gtk.SpinButton(
            adjustment=ai_time_limit_adjustment, climb_rate=1, digits=1
        )
        self.ai_time_limit_spin.set_numeric(True)
        hbox2.pack_start(self.ai_time_limit_spin, False, True, 0)
        label5 = Gtk.Label(label="Player time limit")
        hbox2.pack_start(label5, False, True, 0)
        self.player_time_limit_spin = Gtk.SpinButton(
            adjustment=player_time_limit_adjustment, climb_rate=1, digits=1
        )
        self.player_time_limit_spin.set_numeric(True)
        hbox2.pack_start(self.player_time_limit_spin, False, True, 0)

        self.cancel_button = self.add_button(
            "gtk-cancel", Gtk.ResponseType.CANCEL
        )
        self.cancel_button.connect("button-press-event", self.cancel)
        self.ok_button = self.add_button("gtk-ok", Gtk.ResponseType.OK)
        self.ok_button.connect("button-press-event", self.ok)

        self.show_all()

    def ok(self, widget: Gtk.Widget, event: Gdk.EventButton) -> None:
        if self.name_entry.get_text():
            self.game_name = self.name_entry.get_text()
            self.min_players = self.min_players_spin.get_value_as_int()
            self.max_players = self.max_players_spin.get_value_as_int()
            self.ai_time_limit = self.ai_time_limit_spin.get_value()
            self.player_time_limit = self.player_time_limit_spin.get_value()
            def1 = self.user.callRemote(  # type: ignore
                "form_game",
                self.game_name,
                self.min_players,
                self.max_players,
                self.ai_time_limit,
                self.player_time_limit,
                "Human",
                "",
            )
            def1.addCallback(self.got_information)
            def1.addErrback(self.failure)
            self.destroy()

    def cancel(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        self.destroy()

    def failure(self, error: Any) -> None:
        log.err(error)  # type: ignore

    def got_information(self, information: Optional[str]) -> None:
        if information:
            InfoDialog.InfoDialog(self.parent_window, "Info", str(information))


if __name__ == "__main__":
    from slugathon.util import guiutils

    user = NullUser()
    playername = "test user"
    newgame = NewGame(user, playername, None)
    newgame.connect("destroy", guiutils.exit)
    Gtk.main()
