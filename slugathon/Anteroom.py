#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import gobject
import sys


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self):
        self.glade = glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroom', 'chatEntry', 'chatView', 'gamesTree',
          'playerList']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))

        self.playerStore = gtk.ListStore(gobject.TYPE_STRING)
        players = ['dripton', 'tchula']
        for player in players:
            it = self.playerStore.append()
            self.playerStore.set(it, 0, player)
        self.playerList.set_model(self.playerStore)
        column = gtk.TreeViewColumn('Player Name', gtk.CellRendererText(),
          text=0)
        self.playerList.append_column(column)

        self.gamesStore = gtk.TreeStore(gobject.TYPE_STRING)
        games = ['Game 1', 'Game 2']
        for game in games:
            it = self.gamesStore.append(None)
            self.gamesStore.set(it, 0, game)
        self.gamesTree.set_model(self.gamesStore)
        column = gtk.TreeViewColumn('Game Name', gtk.CellRendererText(),
          text=0)
        self.gamesTree.append_column(column)

        self.anteroom.show_all()



def quit(unused):
    sys.exit()

if __name__ == '__main__':
    anteroom = Anteroom()
    anteroom.anteroom.connect("destroy", quit)
    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/creature/Colossus.gif')
    anteroom.anteroom.set_icon(pixbuf)

    while 1:
        gtk.mainiteration()
