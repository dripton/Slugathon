try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import sys
from sets import Set
from twisted.internet import reactor
import NewGame
import WaitingForPlayers


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
        self.usernames = Set()
        self.games = []
        self.wfp = None

        self.anteroom_window.connect("destroy", quit)
        self.chat_entry.connect("key-press-event", self.cb_keypress)
        self.new_game_button.connect("button-press-event", self.cb_click)

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.anteroom_window.set_icon(pixbuf)
        def1 = user.callRemote("get_user_names")
        def1.addCallbacks(self.got_user_names, self.failure)

    def got_user_names(self, usernames):
        self.usernames = Set(usernames)
        def1 = self.user.callRemote("get_games")
        def1.addCallbacks(self.got_games, self.failure)

    def got_games(self, games):
        self.games = games
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
            game_tuple = game.to_tuple()
            if ii < leng:
                self.game_store[ii, 0] = game_tuple
            else:
                self.game_store.append(game_tuple)
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
        NewGame.NewGame(self.user)

    def receive_chat_message(self, message):
        buffer = self.chatView.get_buffer()
        message = message.strip() + "\n"
        it = buffer.get_end_iter()
        buffer.insert(it, message)
        self.chatView.scroll_to_mark(buffer.get_insert(), 0)

    def add_game(self, game):
        self.games.append(game)
        self.update_game_store()
        if self.username in game.get_playernames():
            if self.wfp:
                self.wfp.destroy()
            self.wfp = WaitingForPlayers.WaitingForPlayers(self.user, game)

    def remove_game(self, game):
        self.games.remove(game)
        self.update_game_store()
        if self.wfp and self.wfp.game == game:
            self.wfp.destroy()
            self.wfp = None

    # XXX The need to substitute references is ugly.  Use Cacheable?
    def change_game(self, game):
        for (ii, g) in enumerate(self.games):
            if g == game:              # Same name
                self.games[ii] = game  # update to latest values
                break
        self.update_game_store()
        if self.wfp:
            if self.wfp.game == game:  # Same name
                self.wfp.game = game
                self.wfp.updatePlayerStore()

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
        self.wfp = WaitingForPlayers.WaitingForPlayers(self.user, game)
        return False

def quit(unused):
    sys.exit()

