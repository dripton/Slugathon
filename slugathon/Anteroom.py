__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"

import gtk.glade
from twisted.internet import reactor
from zope.interface import implements

import NewGame
import LoadGame
import WaitingForPlayers
from Observer import IObserver
import Action
import icon
import guiutils
import prefs


class Anteroom(object):
    """GUI for a multiplayer chat and game finding lobby."""

    implements(IObserver)

    def __init__(self, user, username, usernames, games):
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML("../glade/anteroom.glade")
        self.widget_names = ["anteroom_window", "chat_entry", "chat_view",
          "game_list", "user_list", "new_game_button", "load_game_button"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.usernames = usernames   # set, aliased from Client
        self.games = games           # list, aliased from Client
        self.wfps = {}               # game name : WaitingForPlayers
        self.selected_names = set()

        self.user_store = None       # ListStore
        self.game_store = None       # ListStore
        self._init_liststores()

        self.anteroom_window.connect("destroy", guiutils.exit)
        self.anteroom_window.connect("configure-event",
          self.cb_configure_event)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.new_game_button.connect("button-press-event",
          self.on_new_game_button_click)
        self.load_game_button.connect("button-press-event",
          self.on_load_game_button_click)

        self.anteroom_window.set_icon(icon.pixbuf)
        self.anteroom_window.set_title("%s - %s" % (
          self.anteroom_window.get_title(), self.username))

        if self.username:
            tup = prefs.load_window_position(self.username,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.anteroom_window.move(x, y)
            tup = prefs.load_window_size(self.username,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.anteroom_window.resize(width, height)

        self.anteroom_window.show_all()


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
            x, y = self.anteroom_window.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.anteroom_window.get_size()
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
        NewGame.NewGame(self.user, self.username, self.anteroom_window)

    def on_load_game_button_click(self, widget, event):
        LoadGame.Loadgame(self.user, self.username, self.anteroom_window)

    def receive_chat_message(self, message):
        buf = self.chat_view.get_buffer()
        message = message.strip() + "\n"
        it = buf.get_end_iter()
        buf.insert(it, message)
        self.chat_view.scroll_to_mark(buf.get_insert(), 0)

    def _add_wfp(self, game):
        wfp = self.wfps.get(game.name)
        if wfp is not None:
            if wfp.waiting_for_players_window.has_user_ref_count:
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
