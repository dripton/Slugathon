try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import sys
try:
    set
except NameError:
    from sets import Set as set

from twisted.internet import reactor

import NewGame
import WaitingForPlayers
import Game


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self, user, username):
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroom_window', 'chat_entry', 'chat_view', 
          'game_list', 'user_list', 'new_game_button']
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.usernames = set()
        self.games = []
        self.game_store = []
        self.wfp = None

        self.anteroom_window.connect("destroy", quit)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.new_game_button.connect("button-press-event", self.cb_click)

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.anteroom_window.set_icon(pixbuf)
        self.anteroom_window.set_title("%s - %s" % (
          self.anteroom_window.get_title(), self.username))
        def1 = user.callRemote("get_user_names")
        def1.addCallbacks(self.got_user_names, self.failure)

    def got_user_names(self, usernames):
        self.usernames = set(usernames)
        def1 = self.user.callRemote("get_games")
        def1.addCallbacks(self.got_games, self.failure)

    def got_games(self, game_info_tuples):
        self.games = []
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
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

    def add_username(self, username):
        self.usernames.add(username)
        self.update_user_store()

    def del_username(self, username):
        self.usernames.remove(username)
        self.update_user_store()

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

    def name_to_game(self, game_name):
        for g in self.games:
            if g.name == game_name:
                return g
        raise KeyError("No game named %s found" % game_name)

    def add_game(self, game_info_tuple):
        (name, create_time, start_time, min_players, max_players,
          playernames) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players)
        for playername in playernames[1:]:
            game.add_player(playername)
        self.games.append(game)
        self.update_game_store()
        if self.username in game.get_playernames():
            if self.wfp:
                self.wfp.destroy()
            self.wfp = WaitingForPlayers.WaitingForPlayers(self.user, 
              self.username, game)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
        self.games.remove(game)
        self.update_game_store()
        if self.wfp and self.wfp.game == game:
            self.wfp.destroy()
            self.wfp = None

    def joined_game(self, playername, game_name):
        game = self.name_to_game(game_name)
        game.add_player(playername)
        self.update_game_store()
        if self.wfp and self.wfp.game == game:
            self.wfp.update_player_store()

    def dropped_from_game(self, playername, game_name):
        game = self.name_to_game(game_name)
        game.remove_player(playername)
        self.update_game_store()
        if self.wfp and self.wfp.game == game:
            self.wfp.update_player_store()

    def cb_user_list_select(self, path, unused):
        index = path[0]
        row = self.user_store[index, 0]
        name = row[0]
        return False

    def cb_game_list_select(self, path, unused):
        index = path[0]
        game = self.games[index]
        # TODO popup menu
        if self.wfp:
            self.wfp.destroy()
        self.wfp = WaitingForPlayers.WaitingForPlayers(self.user, 
          self.username, game)
        return False

def quit(unused):
    sys.exit()

