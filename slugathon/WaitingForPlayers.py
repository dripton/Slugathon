#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
from gtk import glade
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
        self.glade = glade.XML('../glade/waitingforplayers.glade')
        self.widgets = ['waitingForPlayersWindow', 'gameNameLabel', 
          'playerList', 'createdEntry', 'startsByEntry', 'countdownEntry',
          'joinButton', 'dropButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.playerStore = gtk.ListStore(str)
        self.updatePlayerStore()

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.waitingForPlayersWindow.set_icon(pixbuf)
        self.joinButton.connect("button-press-event", self.cb_click_join)
        self.dropButton.connect("button-press-event", self.cb_click_drop)
        self.gameNameLabel.set_text(game.name)
        self.createdEntry.set_text(format_time(game.create_time))
        self.startsByEntry.set_text(format_time(game.start_time))
        self.update_countdown()
        self.playerList.set_model(self.playerStore)
        selection = self.playerList.get_selection()
        selection.set_select_function(self.cb_playerList_select, None)
        column = gtk.TreeViewColumn('Player Name', gtk.CellRendererText(),
          text=0)
        self.playerList.append_column(column)

    def cb_click_join(self, widget, event):
        print "clicked join button"
        def1 = self.user.callRemote("join_game", self.game)
        def1.addErrback(self.failure)

    def cb_click_drop(self, widget, event):
        print "clicked drop button"
        def1 = self.user.callRemote("drop_from_game", self.game)
        def1.addErrback(self.failure)

    def cb_playerList_select(self, path, unused):
        index = path[0]
        print "playerList_select", index
        row = self.playerStore[index, 0]
        name = row[0]
        print "player name is", name
        return False

    def update_countdown(self):
        diff = int(self.game.start_time - time.time())
        s = str(max(diff, 0))
        self.countdownEntry.set_text(s)
        if diff > 0:
            reactor.callLater(1, self.update_countdown)

    def updatePlayerStore(self):
        playernames = self.game.players
        leng = len(self.playerStore)
        for ii, playername in enumerate(playernames):
            if ii < leng:
                self.playerStore[ii, 0] = (playername,)
            else:
                self.playerStore.append((playername,))
        leng = len(self.game.players)
        while len(self.playerStore) > leng:
            del self.playerStore[leng]

    def destroy(self):
        self.waitingForPlayersWindow.destroy()

    def failure(self, arg):
        print "WaitingForPlayers.failure", arg
