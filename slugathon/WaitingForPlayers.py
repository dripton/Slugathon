try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import time
from twisted.internet import reactor


def format_time(secs):
    tup = time.localtime(secs)
    return time.strftime("%H:%M:%S", tup)
    

class WaitingForPlayers:
    """Waiting for players to start game dialog."""
    def __init__(self, user, game):
        self.user = user
        self.game = game
        self.glade = gtk.glade.XML('../glade/waitingforplayers.glade')
        self.widgets = ['waiting_for_players_window', 'game_name_label', 
          'player_list', 'created_entry', 'starts_by_entry', 'countdown_entry',
          'join_button', 'drop_button', 'start_button']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.player_store = gtk.ListStore(str)
        self.update_player_store()

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.waiting_for_players_window.set_icon(pixbuf)
        self.join_button.connect("button-press-event", self.cb_click_join)
        self.drop_button.connect("button-press-event", self.cb_click_drop)
        self.start_button.connect("button-press-event", self.cb_click_start)
        # XXX Start button should only be enabled for forming player
        # TODO Start button should automatically be triggered when max
        # players have joined, or min players have joined and time is up.
        self.game_name_label.set_text(game.name)
        self.created_entry.set_text(format_time(game.create_time))
        self.starts_by_entry.set_text(format_time(game.start_time))
        self.update_countdown()
        self.player_list.set_model(self.player_store)
        selection = self.player_list.get_selection()
        selection.set_select_function(self.cb_player_list_select, None)
        column = gtk.TreeViewColumn('Player Name', gtk.CellRendererText(),
          text=0)
        self.player_list.append_column(column)

    def cb_click_join(self, widget, event):
        def1 = self.user.callRemote("join_game", self.game.name)
        def1.addErrback(self.failure)

    def cb_click_drop(self, widget, event):
        def1 = self.user.callRemote("drop_from_game", self.game.name)
        def1.addErrback(self.failure)

    def cb_click_start(self, widget, event):
        def1 = self.user.callRemote("start_game", self.game.name)
        def1.addErrback(self.failure)

    def cb_player_list_select(self, path, unused):
        index = path[0]
        row = self.player_store[index, 0]
        name = row[0]
        return False

    def update_countdown(self):
        diff = int(self.game.start_time - time.time())
        s = str(max(diff, 0))
        self.countdown_entry.set_text(s)
        if diff > 0:
            reactor.callLater(1, self.update_countdown)

    def update_player_store(self):
        playernames = self.game.get_playernames()
        leng = len(self.player_store)
        for ii, playername in enumerate(playernames):
            if ii < leng:
                self.player_store[ii, 0] = (playername,)
            else:
                self.player_store.append((playername,))
        leng = len(self.game.get_playernames())
        while len(self.player_store) > leng:
            del self.player_store[leng]

    def destroy(self):
        self.waiting_for_players_window.destroy()

    def failure(self, arg):
        print "WaitingForPlayers.failure", arg
