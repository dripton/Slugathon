#!/usr/bin/env python3


import logging
import time
from typing import Any, Dict, List, Optional, Set, Union

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implementer

from slugathon.game import Action, Game
from slugathon.gui import LoadGame, NewGame, WaitingForPlayers
from slugathon.net import User
from slugathon.util import guiutils
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class Lobby(Gtk.EventBox):

    """GUI for a multiplayer chat and game finding lobby."""

    def __init__(
        self,
        user: User.User,
        playername: str,
        playernames: Set[str],
        games: List[Game.Game],
        parent_window: Gtk.Window,
    ):
        GObject.GObject.__init__(self)
        self.initialized = False
        self.user = user
        self.playername = playername
        # aliased from Client
        self.playernames = playernames  # type: Set[str]
        # aliased from Client
        self.games = games  # type: List[Game.Game]
        self.parent_window = parent_window

        self.wfps = {}  # type: Dict[str, WaitingForPlayers.WaitingForPlayers]
        self.selected_names = set()  # type: Set[str]

        vbox1 = Gtk.VBox()
        self.add(vbox1)

        label5 = Gtk.Label(label="New Games")
        vbox1.pack_start(label5, False, True, 0)
        scrolled_window1 = Gtk.ScrolledWindow()
        scrolled_window1.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        vbox1.pack_start(scrolled_window1, True, True, 0)
        label6 = Gtk.Label(label="Current Games")
        vbox1.pack_start(label6, False, True, 0)
        scrolled_window4 = Gtk.ScrolledWindow()
        scrolled_window4.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        vbox1.pack_start(scrolled_window4, True, True, 0)
        label7 = Gtk.Label(label="Old Games")
        vbox1.pack_start(label7, False, True, 0)
        scrolled_window5 = Gtk.ScrolledWindow()
        scrolled_window5.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        vbox1.pack_start(scrolled_window5, True, True, 0)

        self.new_game_list = Gtk.TreeView()
        self.new_game_list.set_enable_search(False)
        self.current_game_list = Gtk.TreeView()
        self.current_game_list.set_enable_search(False)
        self.old_game_list = Gtk.TreeView()
        self.old_game_list.set_enable_search(False)
        scrolled_window1.add(self.new_game_list)
        scrolled_window4.add(self.current_game_list)
        scrolled_window5.add(self.old_game_list)

        hbox1 = Gtk.HBox(spacing=10)
        vbox1.pack_start(hbox1, False, True, 0)

        new_game_button = Gtk.Button()
        hbox1.pack_start(new_game_button, False, True, 0)
        hbox2 = Gtk.HBox(spacing=2)
        new_game_button.add(hbox2)
        image1 = Gtk.Image()
        image1.set_from_stock(Gtk.STOCK_NEW, Gtk.IconSize.BUTTON)
        hbox2.pack_start(image1, False, True, 0)
        label1 = Gtk.Label(label="Start new game")
        hbox2.pack_start(label1, False, True, 0)

        load_game_button = Gtk.Button()
        # Disable it until loading games works.
        load_game_button.set_sensitive(False)
        hbox1.pack_start(load_game_button, False, True, 0)
        hbox3 = Gtk.HBox(spacing=2)
        load_game_button.add(hbox3)
        image2 = Gtk.Image()
        image2.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.BUTTON)
        hbox3.pack_start(image2, False, True, 0)
        label2 = Gtk.Label(label="Load saved game")
        hbox3.pack_start(label2, False, True, 0)

        hbox4 = Gtk.HBox()
        vbox1.pack_start(hbox4, True, True, 0)

        vbox2 = Gtk.VBox()
        hbox4.pack_start(vbox2, True, True, 0)

        label3 = Gtk.Label(label="Chat messages")
        vbox2.pack_start(label3, False, True, 0)

        scrolled_window2 = Gtk.ScrolledWindow()
        scrolled_window2.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        vbox2.pack_start(scrolled_window2, True, True, 0)

        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_cursor_visible(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window2.add(self.chat_view)

        label4 = Gtk.Label(label="Chat entry")
        vbox2.pack_start(label4, False, True, 0)

        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_max_length(80)
        self.chat_entry.set_width_chars(80)
        vbox2.pack_start(self.chat_entry, False, True, 0)

        scrolled_window3 = Gtk.ScrolledWindow()
        scrolled_window3.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        hbox4.pack_start(scrolled_window3, True, True, 0)

        self.user_list = Gtk.TreeView()
        self.user_list.set_enable_search(False)
        scrolled_window3.add(self.user_list)

        self.user_store = None  # type: Optional[Gtk.ListStore]
        self.new_game_store = None  # type: Optional[Gtk.ListStore]
        self.current_game_store = None  # type: Optional[Gtk.ListStore]
        self.old_game_store = None  # type: Optional[Gtk.ListStore]
        self._init_liststores()

        self.connect("destroy", guiutils.exit)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        new_game_button.connect(
            "button-press-event", self.cb_new_game_button_click
        )
        load_game_button.connect(
            "button-press-event", self.cb_load_game_button_click
        )

        self.show_all()
        self.initialized = True

    def name_to_game(self, game_name: str) -> Optional[Game.Game]:
        """Return the Game with game_name, or None."""
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def _init_liststores(self) -> None:
        self.user_store = Gtk.ListStore(str, int)
        self.update_user_store()
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.set_select_function(self.cb_user_list_select, data=None)
        headers = ["User Name", "Skill"]
        for (ii, title) in enumerate(headers):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=ii)
            self.user_list.append_column(column)

        self.new_game_store = Gtk.ListStore(str, str, str, str, int, int, str)
        self.current_game_store = Gtk.ListStore(str, str, str, str)
        self.old_game_store = Gtk.ListStore(str, str, str, str, str)
        self.update_game_stores()
        self.new_game_list.set_model(self.new_game_store)
        self.current_game_list.set_model(self.current_game_store)
        self.old_game_list.set_model(self.old_game_store)
        selection = self.new_game_list.get_selection()
        selection.set_select_function(self.cb_game_list_select, None)

        new_headers = [
            "Game Name",
            "Owner",
            "Create Time",
            "Start Time",
            "Min Players",
            "Max Players",
            "Players",
        ]
        for (ii, title) in enumerate(new_headers):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=ii)
            self.new_game_list.append_column(column)
        current_headers = [
            "Game Name",
            "Start Time",
            "Living Players",
            "Dead Players",
        ]
        for (ii, title) in enumerate(current_headers):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=ii)
            self.current_game_list.append_column(column)
        old_headers = [
            "Game Name",
            "Start Time",
            "Finish Time",
            "Winners",
            "Losers",
        ]
        for (ii, title) in enumerate(old_headers):
            column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=ii)
            self.old_game_list.append_column(column)

        for game in self.games:
            self.add_game(game)

    def update_user_store(self) -> None:
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
        sorted_playernames = sorted(self.playernames)
        assert self.user_store is not None
        leng = len(self.user_store)
        for ii, playername in enumerate(sorted_playernames):
            dct = playername_to_data.get(playername)
            if dct:
                skill = dct["skill"]
            else:
                # TODO unhardcode
                skill = 1
            if ii < leng:
                self.user_store[ii, 0] = (playername, skill)
            else:
                self.user_store.append((playername, skill))
        leng = len(sorted_playernames)
        while len(self.user_store) > leng:
            del self.user_store[leng]

    def update_game_stores(self) -> None:
        self.update_new_game_store()
        self.update_current_game_store()
        self.update_old_game_store()

    def update_new_game_store(self) -> None:
        assert self.new_game_store is not None
        length = len(self.new_game_store)
        ii = -1
        for game in self.games:
            if not game.started:
                ii += 1
                name = game.name
                owner = game.owner.name
                create_time = time.ctime(game.create_time)
                start_time = time.ctime(game.start_time)
                min_players = game.min_players
                max_players = game.max_players
                players = ", ".join(game.playernames)
                tup = (
                    name,
                    owner,
                    create_time,
                    start_time,
                    min_players,
                    max_players,
                    players,
                )
                if ii < length:
                    self.new_game_store[ii, 0] = tup
                else:
                    self.new_game_store.append(tup)
        length = ii + 1
        while len(self.new_game_store) > length:
            del self.new_game_store[length]

    def update_current_game_store(self) -> None:
        assert self.current_game_store is not None
        length = len(self.current_game_store)
        ii = -1
        for game in self.games:
            if game.started and not game.over:
                ii += 1
                name = game.name
                start_time = time.ctime(game.start_time)
                living_players = ", ".join(game.living_playernames)
                dead_players = ", ".join(game.dead_playernames)
                tup = (name, start_time, living_players, dead_players)
                if ii < length:
                    self.current_game_store[ii, 0] = tup
                else:
                    self.current_game_store.append(tup)
        length = ii + 1
        while len(self.current_game_store) > length:
            del self.current_game_store[length]

    def update_old_game_store(self) -> None:
        assert self.old_game_store is not None
        length = len(self.old_game_store)
        ii = -1
        for game in self.games:
            if game.started and game.over:
                ii += 1
                name = game.name
                start_time = time.ctime(game.start_time)
                finish_time = time.ctime(game.finish_time)
                winners = ", ".join(game.winner_names)
                losers = ", ".join(game.loser_names)
                tup = (name, start_time, finish_time, winners, losers)
                if ii < length:
                    self.old_game_store[ii, 0] = tup
                else:
                    self.old_game_store.append(tup)
        length = ii + 1
        while len(self.old_game_store) > length:
            del self.old_game_store[length]

    def failure(self, error: Any) -> None:
        log.err(error)  # type: ignore
        reactor.stop()  # type: ignore

    def cb_keypress(self, entry: Gtk.Entry, event: Any) -> None:
        logging.debug(f"{event=}")
        if event.keyval == Gdk.KEY_Return:
            text = self.chat_entry.get_text()
            if text:
                if not self.selected_names:
                    dest = None
                else:
                    dest = self.selected_names
                def1 = self.user.callRemote("send_chat_message", dest, text)  # type: ignore
                def1.addErrback(self.failure)
                self.chat_entry.set_text("")

    def cb_new_game_button_click(
        self, widget: Gtk.Widget, event: Gdk.EventButton
    ) -> None:
        NewGame.NewGame(self.user, self.playername, self.parent_window)

    def cb_load_game_button_click(
        self, widget: Gtk.Widget, event: Any
    ) -> None:
        logging.debug(f"{event=}")
        LoadGame.LoadGame(self.user, self.playername, self.parent_window)

    def _add_wfp(self, game: Game.Game) -> None:
        wfp = self.wfps.get(game.name)
        if wfp is not None:
            if wfp.has_user_ref_count:
                # has not been destroyed
                return
            else:
                del wfp
        wfp = WaitingForPlayers.WaitingForPlayers(
            self.user, self.playername, game, self.parent_window
        )
        self.wfps[game.name] = wfp

    def _remove_wfp(self, game_name: str) -> None:
        if game_name in self.wfps:
            wfp = self.wfps[game_name]
            wfp.destroy()
            del self.wfps[game_name]

    def add_game(self, game: Game.Game) -> None:
        self.update_game_stores()
        if not game.started and self.playername in game.playernames:
            self._add_wfp(game)

    def remove_game(self, game_name: str) -> None:
        self.update_game_stores()
        game = self.name_to_game(game_name)
        if game:
            game.remove_observer(self)

    def joined_game(self, playername: str, game_name: str) -> None:
        self.update_game_stores()

    def withdrew_from_game(self, game_name: str, playername: str) -> None:
        if playername == self.playername:
            self._remove_wfp(game_name)
        self.update_game_stores()

    def cb_user_list_select(
        self,
        selection: Gtk.TreeSelection,
        model: Gtk.ListStore,
        path: List[int],
        is_selected: bool,
        unused: Any,
    ) -> None:
        logging.debug(f"{unused=}")
        index = path[0]
        assert self.user_store is not None
        row = self.user_store[index, 0]
        name = row[0]
        if is_selected:
            self.selected_names.remove(name)
        else:
            self.selected_names.add(name)
        return True

    def cb_game_list_select(self, path: List[int], unused: Any) -> None:
        logging.debug(f"{unused=}")
        index = path[0]
        assert self.new_game_store is not None
        tup = self.new_game_store[index, 0]
        name = tup[0]
        game = self.name_to_game(name)
        if not game.started and self.initialized:
            # We get a spurious call to this method during initialization,
            # so don't add a WaitingForPlayers until fully initialized.
            self._add_wfp(game)
        return False

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        if isinstance(action, Action.AddUsername):
            self.update_user_store()
        elif isinstance(action, Action.DelUsername):
            self.update_user_store()
        elif isinstance(action, Action.FormGame):
            game = self.name_to_game(action.game_name)
            if game:
                self.add_game(game)
        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)
        elif isinstance(action, Action.JoinGame):
            self.joined_game(action.playername, action.game_name)
        elif isinstance(action, Action.Withdraw):
            self.withdrew_from_game(action.game_name, action.playername)
        elif isinstance(action, Action.AssignTower):
            if action.game_name in self.wfps:
                del self.wfps[action.game_name]
        elif isinstance(action, Action.AssignedAllTowers):
            reactor.callLater(0, self.update_game_stores)  # type: ignore
        elif isinstance(action, Action.GameOver):
            reactor.callLater(0, self.update_game_stores)  # type: ignore
            reactor.callLater(0, self.update_user_store)  # type: ignore
        elif isinstance(action, Action.EliminatePlayer):
            reactor.callLater(0, self.update_game_stores)  # type: ignore
        elif isinstance(action, Action.ChatMessage):
            buf = self.chat_view.get_buffer()
            message = action.message.strip() + "\n"
            it = buf.get_end_iter()
            buf.insert(it, message)
            self.chat_view.scroll_to_mark(buf.get_insert(), 0, False, 0.5, 0.5)
            if action.source_playername != self.playername:
                self.parent_window.highlight_lobby_label()


if __name__ == "__main__":
    from slugathon.util.NullUser import NullUser

    now = time.time()
    user = NullUser()
    playername = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    playernames = {playername}
    games = [game]
    window = Gtk.Window()
    window.set_default_size(1024, 768)
    lobby = Lobby(user, playername, playernames, games, window)
    window.add(lobby)
    window.show_all()
    Gtk.main()
