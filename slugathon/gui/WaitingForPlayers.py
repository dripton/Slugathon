#!/usr/bin/env python3

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Union

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
from zope.interface import implementer

from slugathon.game import Action, Game
from slugathon.gui import icon
from slugathon.net import User
from slugathon.util.NullUser import NullUser
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2004-2021 David Ripton"
__license__ = "GNU GPL v2"


def format_time(secs: float) -> str:
    tup = time.localtime(secs)
    return time.strftime("%H:%M:%S", tup)


@implementer(IObserver)
class WaitingForPlayers(Gtk.Dialog):

    """Waiting for players to start game dialog."""

    def __init__(
        self,
        user: User.User,
        playername: str,
        game: Game.Game,
        parent: Gtk.Window,
    ):
        GObject.GObject.__init__(
            self, title=f"Waiting for Players - {playername}", parent=parent
        )
        self.user = user
        self.playername = playername
        self.game = game
        self.game.add_observer(self)
        self.started = False

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_default_size(-1, 300)

        label1 = Gtk.Label(label=game.name)
        self.vbox.pack_start(label1, False, True, 0)

        scrolled_window1 = Gtk.ScrolledWindow()
        scrolled_window1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.vbox.pack_start(scrolled_window1, True, True, 0)

        self.player_list = Gtk.TreeView()
        scrolled_window1.add(self.player_list)

        hbox1 = Gtk.HBox()
        self.vbox.pack_start(hbox1, False, True, 0)

        vbox2 = Gtk.VBox()
        hbox1.pack_start(vbox2, True, True, 0)
        label2 = Gtk.Label(label="Created at")
        vbox2.pack_start(label2, False, True, 0)
        scrolled_window2 = Gtk.ScrolledWindow()
        scrolled_window2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        vbox2.pack_start(scrolled_window2, True, True, 0)
        viewport1 = Gtk.Viewport()
        scrolled_window2.add(viewport1)
        created_entry = Gtk.Entry()
        created_entry.set_max_length(8)
        created_entry.set_editable(False)
        created_entry.set_text(format_time(game.create_time))
        viewport1.add(created_entry)

        vbox3 = Gtk.VBox()
        hbox1.pack_start(vbox3, True, True, 0)
        label3 = Gtk.Label(label="Starts by")
        vbox3.pack_start(label3, False, True, 0)
        scrolled_window3 = Gtk.ScrolledWindow()
        scrolled_window3.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        vbox3.pack_start(scrolled_window3, True, True, 0)
        viewport2 = Gtk.Viewport()
        scrolled_window3.add(viewport2)
        starts_by_entry = Gtk.Entry()
        starts_by_entry.set_max_length(8)
        starts_by_entry.set_editable(False)
        starts_by_entry.set_text(format_time(game.start_time))
        viewport2.add(starts_by_entry)

        vbox4 = Gtk.VBox()
        hbox1.pack_start(vbox4, True, True, 0)
        label4 = Gtk.Label(label="Time Left")
        vbox4.pack_start(label4, False, True, 0)
        scrolled_window4 = Gtk.ScrolledWindow()
        scrolled_window4.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        vbox4.pack_start(scrolled_window4, True, True, 0)
        viewport3 = Gtk.Viewport()
        scrolled_window4.add(viewport3)
        self.countdown_entry = Gtk.Entry()
        self.countdown_entry.set_max_length(8)
        self.countdown_entry.set_editable(False)
        viewport3.add(self.countdown_entry)

        join_button = Gtk.Button(label="Join Game")
        self.vbox.pack_start(join_button, False, True, 0)
        join_button.connect("button-press-event", self.cb_click_join)

        drop_button = Gtk.Button(label="Drop out of Game")
        self.vbox.pack_start(drop_button, False, True, 0)
        drop_button.connect("button-press-event", self.cb_click_drop)

        self.start_button = Gtk.Button(label="Start Game Now")
        self.vbox.pack_start(self.start_button, False, True, 0)
        self.start_button.connect("button-press-event", self.cb_click_start)
        self.start_button.set_sensitive(
            self.playername == self.game.owner.name
        )

        self.connect("destroy", self.cb_destroy)

        self.player_store = Gtk.ListStore(str, int)
        self.update_player_store()

        self.update_countdown()
        self.player_list.set_model(self.player_store)
        selection = self.player_list.get_selection()
        selection.set_select_function(self.cb_player_list_select, None)
        headers = ["Player Name", "Skill"]
        for (ii, title) in enumerate(headers):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=ii)
            self.player_list.append_column(column)

        self.show_all()

    def cb_click_join(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        def1 = self.user.callRemote("join_game", self.game.name, "Human", "")  # type: ignore
        def1.addErrback(self.failure)

    def cb_destroy(self, unused: WaitingForPlayers) -> None:
        if self.game and not self.game.started:
            def1 = self.user.callRemote("withdraw", self.game.name)  # type: ignore
            def1.addErrback(self.failure)

    def cb_click_drop(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        def1 = self.user.callRemote("withdraw", self.game.name)  # type: ignore
        def1.addErrback(self.failure)
        self.destroy()

    def cb_click_start(
        self, widget: Gtk.Widget, event: Gdk.EventButton
    ) -> None:
        self.start_game()

    def start_game(self) -> None:
        if not self.started:
            self.started = True
            def1 = self.user.callRemote("start_game", self.game.name)  # type: ignore
            def1.addErrback(self.failure)

    # TODO Save the selection and do something useful with it.
    def cb_player_list_select(self, path: List[int], unused: Any) -> bool:
        index = path[0]
        self.player_store[index, 0]
        return False

    def update_countdown(self) -> None:
        diff = int(self.game.start_time - time.time())
        label = str(max(diff, 0))
        self.countdown_entry.set_text(label)
        if diff > 0:
            if self.game.num_players >= self.game.max_players:
                self.start_game()
            else:
                reactor.callLater(1, self.update_countdown)  # type: ignore
        else:
            if self.game.num_players >= self.game.min_players:
                self.start_game()

    def update_player_store(self) -> None:
        def1 = self.user.callRemote("get_player_data")  # type: ignore
        def1.addCallback(self._got_player_data)
        def1.addErrback(self.failure)

    def _got_player_data(
        self, player_data: List[Dict[str, Union[str, float]]]
    ) -> None:
        playername_to_data = {}
        if player_data:
            for dct in player_data:
                playername_to_data[dct["name"]] = dct
        length = len(self.player_store)
        for ii, playername in enumerate(self.game.playernames):
            if playername in playername_to_data:
                dct = playername_to_data[playername]
                skill = dct["skill"]
            else:
                # TODO unhardcode
                skill = 1
            if ii < length:
                self.player_store[(ii, 0)] = (playername, skill)
            else:
                self.player_store.append((playername, skill))
        length = len(self.game.playernames)
        while len(self.player_store) > length:
            del self.player_store[length]
        self.start_button.set_sensitive(
            self.playername == self.game.owner.name
        )

    def failure(self, arg: Any) -> None:
        log.err(arg)  # type: ignore

    def shutdown(self) -> None:
        self.game.remove_observer(self)
        self.destroy()

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        if isinstance(action, Action.RemoveGame):
            if action.game_name == self.game.name:
                self.shutdown()
        elif isinstance(action, Action.JoinGame):
            self.update_player_store()
        elif isinstance(action, Action.Withdraw):
            self.update_player_store()
        elif isinstance(action, Action.AssignTower):
            if action.game_name == self.game.name:
                self.shutdown()


if __name__ == "__main__":
    now = time.time()
    user = NullUser()
    playername = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    wfp = WaitingForPlayers(user, playername, game, None)
    wfp.connect("destroy", lambda x: reactor.stop())  # type: ignore
    reactor.run()  # type: ignore
