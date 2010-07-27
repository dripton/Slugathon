#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from twisted.internet import reactor
from zope.interface import implements

from slugathon.gui import NewGame, LoadGame, WaitingForPlayers, icon
from slugathon.util.Observer import IObserver
from slugathon.game import Action
from slugathon.util import guiutils, prefs
from slugathon.util.NullUser import NullUser


class Anteroom(gtk.Window):
    """GUI for a multiplayer chat and game finding lobby."""

    implements(IObserver)

    def __init__(self, user, username, usernames, games):
        gtk.Window.__init__(self)
        self.user = user
        self.username = username
        self.usernames = usernames   # set, aliased from Client
        self.games = games           # list, aliased from Client

        self.wfps = {}               # game name : WaitingForPlayers
        self.selected_names = set()

        self.set_title("Anteroom - %s" % self.username)
        self.set_default_size(800, 600)
        self.set_icon(icon.pixbuf)

        vbox1 = gtk.VBox()
        self.add(vbox1)

        scrolled_window1 = gtk.ScrolledWindow()
        scrolled_window1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox1.pack_start(scrolled_window1)

        self.game_list = gtk.TreeView()
        self.game_list.set_enable_search(False)
        scrolled_window1.add(self.game_list)

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

        self.user_store = None       # ListStore
        self.game_store = None       # ListStore
        self._init_liststores()

        self.connect("destroy", guiutils.exit)
        self.connect("configure-event", self.cb_configure_event)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        new_game_button.connect("button-press-event",
          self.on_new_game_button_click)
        load_game_button.connect("button-press-event",
          self.on_load_game_button_click)

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


    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def _init_liststores(self):
        self.user_store = gtk.ListStore(str)
        self.update_user_store()
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.set_select_function(self.cb_user_list_select, data=None,
          full=True)
        column = gtk.TreeViewColumn("User Name", gtk.CellRendererText(),
          text=0)
        self.user_list.append_column(column)

        self.game_store = gtk.ListStore(str, str, str, str, int, int, str)
        self.update_game_store()
        self.game_list.set_model(self.game_store)
        selection = self.game_list.get_selection()
        selection.set_select_function(self.cb_game_list_select, None)
        headers = ["Game Name", "Owner", "Create Time", "Start Time",
          "Min Players", "Max Players", "Players"]
        for (ii, title) in enumerate(headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.game_list.append_column(column)
        for game in self.games:
            self.add_game(game)

    def update_user_store(self):
        sorted_usernames = sorted(self.usernames)
        leng = len(self.user_store)
        for ii, username in enumerate(sorted_usernames):
            if ii < leng:
                self.user_store[ii, 0] = (username,)
            else:
                self.user_store.append((username,))
        leng = len(sorted_usernames)
        while len(self.user_store) > leng:
            del self.user_store[leng]

    def update_game_store(self):
        leng = len(self.game_store)
        for ii, game in enumerate(self.games):
            game_gui_tuple = game.to_gui_tuple()
            if ii < leng:
                self.game_store[ii, 0] = game_gui_tuple
            else:
                self.game_store.append(game_gui_tuple)
        leng = len(self.games)
        while len(self.game_store) > leng:
            del self.game_store[leng]

    def failure(self, error):
        print "Anteroom.failure", self, error
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

    def on_new_game_button_click(self, widget, event):
        NewGame.NewGame(self.user, self.username, self)

    def on_load_game_button_click(self, widget, event):
        LoadGame.LoadGame(self.user, self.username, self)

    def receive_chat_message(self, message):
        buf = self.chat_view.get_buffer()
        message = message.strip() + "\n"
        it = buf.get_end_iter()
        buf.insert(it, message)
        self.chat_view.scroll_to_mark(buf.get_insert(), 0)

    def _add_wfp(self, game):
        wfp = self.wfps.get(game.name)
        if wfp is not None:
            if wfp.has_user_ref_count:
                # has not been destroyed
                return
            else:
                del wfp
        wfp = WaitingForPlayers.WaitingForPlayers(self.user, self.username,
          game)
        self.wfps[game.name] = wfp

    def _remove_wfp(self, game_name):
        if game_name in self.wfps:
            wfp = self.wfps[game_name]
            wfp.destroy()
            del self.wfps[game_name]

    def add_game(self, game):
        game.add_observer(self, self.username)
        self.update_game_store()
        if not game.started and self.username in game.get_playernames():
            self._add_wfp(game)

    def remove_game(self, game_name):
        self.update_game_store()
        game = self.name_to_game(game_name)
        if game:
            game.remove_observer(self)

    def joined_game(self, playername, game_name):
        self.update_game_store()

    def dropped_from_game(self, game_name, username):
        if username == self.username:
            self._remove_wfp(game_name)
        self.update_game_store()

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
        # TODO popup menu
        if not game.started:
            self._add_wfp(game)
        return False

    def update(self, observed, action):
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
        elif isinstance(action, Action.DropFromGame):
            self.dropped_from_game(action.game_name, action.username)
        elif isinstance(action, Action.AssignTower):
            if action.game_name in self.wfps:
                del self.wfps[action.game_name]


if __name__ == "__main__":
    import time
    from slugathon.game import Game

    now = time.time()
    user = NullUser()
    username = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    usernames = [username]
    games = [game]
    anteroom = Anteroom(user, username, usernames, games)
    gtk.main()
