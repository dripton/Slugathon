#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
import gtk
from gtk import glade
import sys


class WaitingForPlayers:
    """Waiting for players to start game dialog."""
    def __init__(self, user):
        self.user = user
        self.glade = glade.XML('../glade/waitingforplayers.glade')
        self.widgets = ['waitingForPlayersWindow', 'gameNameLabel', 
          'playerList', 'createdEntry', 'startsByEntry', 'countdownEntry',
          'dropButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.newgameDialog.set_icon(pixbuf)
        self.dropButton.connect("clicked", cb_click)

    def cb_click(self, widget, event):
        print "clicked drop button"
        # TODO
