#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


import time

import gtk
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implementer

from slugathon.gui import NewGame, LoadGame, WaitingForPlayers, icon
from slugathon.util.Observer import IObserver
from slugathon.game import Action
from slugathon.util import guiutils, prefs
from slugathon.util.NullUser import NullUser
from slugathon.net import Results


@implementer(IObserver)
class Anteroom(gtk.Window):
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self, user, username, usernames, games):
        gtk.Window.__init__(self)
        self.initialized = False
        self.user = user
        self.username = username
        self.usernames = usernames   # set, aliased from Client
        self.games = games           # list, aliased from Client

        self.wfps = {}               # game name : WaitingForPlayers
        self.selected_names = set()
        self.results = Results.Results()

        self.set_title("Anteroom - %s" % self.username)
        self.set_default_size(800, 600)
        self.set_icon(icon.pixbuf)

        vbox1 = gtk.VBox()
        self.add(vbox1)

        label5 = gtk.Label("New Games")
        vbox1.pack_start(label5, expand=False)
        scrolled_window1 = gtk.ScrolledWindow()
        scrolled_window1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1.pack_start(scrolled_window1)
        label6 = gtk.Label("Current Games")
        vbox1.pack_start(label6, expand=False)
        scrolled_window4 = gtk.ScrolledWindow()
        scrolled_window4.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1.pack_start(scrolled_window4)
        label7 = gtk.Label("Old Games")
        vbox1.pack_start(label7, expand=False)
        scrolled_window5 = gtk.ScrolledWindow()
        scrolled_window5.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1.pack_start(scrolled_window5)

        self.new_game_list = gtk.TreeView()
        self.new_game_list.set_enable_search(False)
        self.current_game_list = gtk.TreeView()
        self.current_game_list.set_enable_search(False)
        self.old_game_list = gtk.TreeView()
        self.old_game_list.set_enable_search(False)
        scrolled_window1.add(self.new_game_list)
        scrolled_window4.add(self.current_game_list)
        scrolled_window5.add(self.old_game_list)

        hbox1 = gtk.HBox(spacing=10)
        vbox1.pack_start(hbox1, expand=False)

        new_game_button = gtk.Button()
        hbox1.pack_start(new_game_button, expand=False)
        alignment1 = gtk.Alignment()
        new_game_button.add(alignment1)
        hbox2 = gtk.HBox(spacing=2)
        alignment1.add(hbox2)
        image1 = gtk.Image()
        image1.set_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_BUTTON)
        hbox2.pack_start(image1, expand=False)
        label1 = gtk.Label("Start new game")
        hbox2.pack_start(label1, expand=False)

        load_game_button = gtk.Button()
        hbox1.pack_start(load_game_button, expand=False)
        alignment2 = gtk.Alignment()
        load_game_button.add(alignment2)
        hbox3 = gtk.HBox(spacing=2)
        alignment2.add(hbox3)
        image2 = gtk.Image()
        image2.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        hbox3.pack_start(image2, expand=False)
        label2 = gtk.Label("Load saved game")
        hbox3.pack_start(label2, expand=False)

        hbox4 = gtk.HBox()
        vbox1.pack_start(hbox4)

        vbox2 = gtk.VBox()
        hbox4.pack_start(vbox2)

        label3 = gtk.Label("Chat messages")
        vbox2.pack_start(label3, expand=False)

        scrolled_window2 = gtk.ScrolledWindow()
        scrolled_window2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox2.pack_start(scrolled_window2)

        self.chat_view = gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_cursor_visible(False)
        self.chat_view.set_wrap_mode(gtk.WRAP_WORD)
        scrolled_window2.add(self.chat_view)

        label4 = gtk.Label("Chat entry")
        vbox2.pack_start(label4, expand=False)

        self.chat_entry = gtk.Entry(max=80)
        self.chat_entry.set_width_chars(80)
        vbox2.pack_start(self.chat_entry, expand=False)

        scrolled_window3 = gtk.ScrolledWindow()
        scrolled_window3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox4.pack_start(scrolled_window3)

        self.user_list = gtk.TreeView()
        self.user_list.set_enable_search(False)
        scrolled_window3.add(self.user_list)

        self.user_store = None          # ListStore
        self.new_game_store = None      # ListStore
        self.current_game_store = None  # ListStore
        self.old_game_store = None      # ListStore
        self._init_liststores()

        self.connect("destroy", guiutils.exit)
        self.connect("configure-event", self.cb_configure_event)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        new_game_button.connect("button-press-event",
          self.cb_new_game_button_click)
        load_game_button.connect("button-press-event",
          self.cb_load_game_button_click)

        if self.username:
            tup = prefs.load_window_position(self.username,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(self.username,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.resize(width, height)

        self.show_all()
        self.initialized = True

    def name_to_game(self, game_name):
        """Return the Game with game_name, or None."""
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def _init_liststores(self):
        self.user_store = gtk.ListStore(str, int)
        self.update_user_store()
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.set_select_function(self.cb_user_list_select, data=None,
          full=True)
        headers = ["User Name", "Skill"]
        for (ii, title) in enumerate(headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.user_list.append_column(column)

        self.new_game_store = gtk.ListStore(str, str, str, str, int, int, str)
        self.current_game_store = gtk.ListStore(str, str, str, str)
        self.old_game_store = gtk.ListStore(str, str, str, str, str)
        self.update_game_stores()
        self.new_game_list.set_model(self.new_game_store)
        self.current_game_list.set_model(self.current_game_store)
        self.old_game_list.set_model(self.old_game_store)
        selection = self.new_game_list.get_selection()
        selection.set_select_function(self.cb_game_list_select, None)

        new_headers = ["Game Name", "Owner", "Create Time", "Start Time",
          "Min Players", "Max Players", "Players"]
        for (ii, title) in enumerate(new_headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.new_game_list.append_column(column)
        current_headers = ["Game Name", "Start Time", "Living Players",
          "Dead Players"]
        for (ii, title) in enumerate(current_headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.current_game_list.append_column(column)
        old_headers = ["Game Name", "Start Time", "Finish Time", "Winners",
          "Losers"]
        for (ii, title) in enumerate(old_headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.old_game_list.append_column(column)

        for game in self.games:
            self.add_game(game)

    def update_user_store(self):
        sorted_usernames = sorted(self.usernames)
        leng = len(self.user_store)
        for ii, username in enumerate(sorted_usernames):
            ranking = self.results.get_ranking(username)
            skill = ranking.skill
            if ii < leng:
                self.user_store[ii, 0] = (username, skill)
            else:
                self.user_store.append((username, skill))
        leng = len(sorted_usernames)
        while len(self.user_store) > leng:
            del self.user_store[leng]

    def update_game_stores(self):
        self.update_new_game_store()
        self.update_current_game_store()
        self.update_old_game_store()

    def update_new_game_store(self):
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
                players = ", ".join(playername for playername in
                  game.playernames)
                tup = (name, owner, create_time, start_time, min_players,
                  max_players, players)
                if ii < length:
                    self.new_game_store[ii, 0] = tup
                else:
                    self.new_game_store.append(tup)
        length = ii + 1
        while len(self.new_game_store) > length:
            del self.new_game_store[length]

    def update_current_game_store(self):
        length = len(self.current_game_store)
        ii = -1
        for game in self.games:
            if game.started and not game.over:
                ii += 1
                name = game.name
                start_time = time.ctime(game.start_time)
                living_players = ", ".join(playername for playername in
                  game.living_playernames)
                dead_players = ", ".join(playername for playername in
                  game.dead_playernames)
                tup = (name, start_time, living_players, dead_players)
                if ii < length:
                    self.current_game_store[ii, 0] = tup
                else:
                    self.current_game_store.append(tup)
        length = ii + 1
        while len(self.current_game_store) > length:
            del self.current_game_store[length]

    def update_old_game_store(self):
        length = len(self.old_game_store)
        ii = -1
        for game in self.games:
            if game.started and game.over:
                ii += 1
                name = game.name
                start_time = time.ctime(game.start_time)
                finish_time = time.ctime(game.finish_time)
                living_players = ", ".join(playername for playername in
                  game.living_playernames)
                dead_players = ", ".join(playername for playername in
                  game.dead_playernames)
                tup = (name, start_time, finish_time, living_players,
                  dead_players)
                if ii < length:
                    self.old_game_store[ii, 0] = tup
                else:
                    self.old_game_store.append(tup)
        length = ii + 1
        while len(self.old_game_store) > length:
            del self.old_game_store[length]

    def failure(self, error):
        log.err(error)
        reactor.stop()

    def cb_configure_event(self, event, unused):
        if self.username:
            x, y = self.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.username, self.__class__.__name__,
              width, height)
        return False

    def cb_keypress(self, entry, event):
        if event.keyval == gtk.keysyms.Return:
            text = self.chat_entry.get_text()
            if text:
                if not self.selected_names:
                    dest = None
                else:
                    dest = self.selected_names
                def1 = self.user.callRemote("send_chat_message", dest, text)
                def1.addErrback(self.failure)
                self.chat_entry.set_text("")

    def cb_new_game_button_click(self, widget, event):
        NewGame.NewGame(self.user, self.username, self)

    def cb_load_game_button_click(self, widget, event):
        LoadGame.LoadGame(self.user, self.username, self)

    def _add_wfp(self, game):
        wfp = self.wfps.get(game.name)
        if wfp is not None:
            if wfp.has_user_ref_count:
                # has not been destroyed
                return
            else:
                del wfp
        wfp = WaitingForPlayers.WaitingForPlayers(self.user, self.username,
          game, self)
        self.wfps[game.name] = wfp

    def _remove_wfp(self, game_name):
        if game_name in self.wfps:
            wfp = self.wfps[game_name]
            wfp.destroy()
            del self.wfps[game_name]

    def add_game(self, game):
        game.add_observer(self, self.username)
        self.update_game_stores()
        if not game.started and self.username in game.playernames:
            self._add_wfp(game)

    def remove_game(self, game_name):
        self.update_game_stores()
        game = self.name_to_game(game_name)
        if game:
            game.remove_observer(self)

    def joined_game(self, playername, game_name):
        self.update_game_stores()

    def withdrew_from_game(self, game_name, username):
        if username == self.username:
            self._remove_wfp(game_name)
        self.update_game_stores()

    def cb_user_list_select(self, selection, model, path, is_selected, unused):
        index = path[0]
        row = self.user_store[index, 0]
        name = row[0]
        if is_selected:
            self.selected_names.remove(name)
        else:
            self.selected_names.add(name)
        return True

    def cb_game_list_select(self, path, unused):
        index = path[0]
        game = self.games[index]
        if not game.started and self.initialized:
            # We get a spurious call to this method during initialization,
            # so don't add a WaitingForPlayers until fully initialized.
            self._add_wfp(game)
        return False

    def update(self, observed, action, names):
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
            self.joined_game(action.username, action.game_name)
        elif isinstance(action, Action.Withdraw):
            self.withdrew_from_game(action.game_name, action.playername)
        elif isinstance(action, Action.AssignTower):
            if action.game_name in self.wfps:
                del self.wfps[action.game_name]
        elif isinstance(action, Action.AssignedAllTowers):
            self.update_game_stores()
        elif isinstance(action, Action.GameOver):
            self.update_game_stores()
        elif isinstance(action, Action.EliminatePlayer):
            self.update_game_stores()
        elif isinstance(action, Action.ChatMessage):
            buf = self.chat_view.get_buffer()
            message = action.message.strip() + "\n"
            it = buf.get_end_iter()
            buf.insert(it, message)
            self.chat_view.scroll_to_mark(buf.get_insert(), 0)


if __name__ == "__main__":
    from slugathon.game import Game

    now = time.time()
    user = NullUser()
    username = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    usernames = [username]
    games = [game]
    anteroom = Anteroom(user, username, usernames, games)
    gtk.main()
