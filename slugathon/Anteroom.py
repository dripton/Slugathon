import sys

try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
from twisted.internet import reactor
import zope.interface

import NewGame
import WaitingForPlayers
from Observer import IObserver
import Action


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""

    zope.interface.implements(IObserver)

    def __init__(self, user, username):
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroom_window', 'chat_entry', 'chat_view', 
          'game_list', 'user_list', 'new_game_button']
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.usernames = None   # set, aliased from Client
        self.games = None       # list, aliased from Client
        self.game_store = []
        self.wfps = {}          # game name : WaitingForPlayers

        self.anteroom_window.connect("destroy", quit)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.new_game_button.connect("button-press-event", self.cb_click)

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.anteroom_window.set_icon(pixbuf)
        self.anteroom_window.set_title("%s - %s" % (
          self.anteroom_window.get_title(), self.username))

    def set_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        self.usernames = usernames

    def name_to_game(self, game_name):
        for g in self.games:
            if g.name == game_name:
                return g
        return None

    def set_games(self, games):
        """Only called when the client first connects to the server."""
        self.games = games
        for game in self.games:
            self.add_game(game)
        self.user_store = gtk.ListStore(str)
        self.update_user_store()
        self.user_list.set_model(self.user_store)
        selection = self.user_list.get_selection()
        selection.set_select_function(self.cb_user_list_select, None)
        column = gtk.TreeViewColumn('User Name', gtk.CellRendererText(),
          text=0)
        self.user_list.append_column(column)

        self.game_store = gtk.ListStore(str, str, str, str, int, int, str)
        self.update_game_store()
        self.game_list.set_model(self.game_store)
        selection = self.game_list.get_selection()
        selection.set_select_function(self.cb_game_list_select, None)
        headers = ['Game Name', 'Owner', 'Create Time', 'Start Time',
          'Min Players', 'Max Players', 'Players']
        for (ii, title) in enumerate(headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.game_list.append_column(column)
        self.anteroom_window.show_all()

    def update_user_store(self):
        sorted_usernames = list(self.usernames)
        sorted_usernames.sort()
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

    def cb_keypress(self, entry, event):
        ENTER_KEY = 65293  # XXX Find a cleaner way to do this.
        if event.keyval == ENTER_KEY:
            text = self.chat_entry.get_text()
            if text:
                def1 = self.user.callRemote("send_chat_message", text)
                def1.addErrback(self.failure)
                self.chat_entry.set_text("")

    def cb_click(self, widget, event):
        NewGame.NewGame(self.user, self.username)

    def receive_chat_message(self, message):
        buf = self.chat_view.get_buffer()
        message = message.strip() + "\n"
        it = buf.get_end_iter()
        buf.insert(it, message)
        self.chat_view.scroll_to_mark(buf.get_insert(), 0)

    def _add_or_replace_wfp(self, game):
        if game.name in self.wfps:
            self.wfps[game.name].remove_game()
        wfp = WaitingForPlayers.WaitingForPlayers(self.user,
          self.username, game)
        self.wfps[game.name] = wfp

    def add_game(self, game):
        print "Anteroom.add_game", game.name
        game.attach(self)
        self.update_game_store()
        if self.username in game.get_playernames():
            self._add_or_replace_wfp(game)

    def remove_game(self, game_name):
        self.update_game_store()
        game = self.name_to_game(game_name)
        if game:
            game.detach(self)

    def joined_game(self, playername, game_name):
        print "Anteroom.joined_game", playername, game_name
        self.update_game_store()

    def dropped_from_game(self, game_name):
        self.update_game_store()

    # TODO Actually saved marked user for private chats, user info, etc.
    def cb_user_list_select(self, path, unused):
        index = path[0]
        row = self.user_store[index, 0]
        name = row[0]
        return False

    def cb_game_list_select(self, path, unused):
        print "Anteroom.cb_game_list_select"
        index = path[0]
        game = self.games[index]
        # TODO popup menu
        self._add_or_replace_wfp(game)
        return False

    def update(self, observed, action):
        print "Anteroom.update", self, observed, action

        if isinstance(action, Action.AddUsername):
            self.update_user_store()
        elif isinstance(action, Action.DelUsername):
            self.update_user_store()
        elif isinstance(action, Action.FormGame):
            game = self.name_to_game(action.game_name)
            self.add_game(game)
        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)
        elif isinstance(action, Action.JoinGame):
            self.joined_game(action.username, action.game_name)
        elif isinstance(action, Action.DropFromGame):
            self.dropped_from_game(action.game_name)
        elif isinstance(action, Action.AssignTower):
            if action.game_name in self.wfps:
                del self.wfps[action.game_name]


def quit(unused):
    sys.exit()

