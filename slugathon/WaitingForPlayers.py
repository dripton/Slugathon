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
    # TODO Pull game info from server side rather than passing?
    def __init__(self, user, gameName, min_players, max_players):
        self.user = user
        self.glade = glade.XML('../glade/waitingforplayers.glade')
        self.widgets = ['waitingForPlayersWindow', 'gameNameLabel', 
          'playerList', 'createdEntry', 'startsByEntry', 'countdownEntry',
          'dropButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.waitingForPlayersWindow.set_icon(pixbuf)
        self.dropButton.connect("button-press-event", self.cb_click)
        self.gameNameLabel.set_text(gameName)

    def cb_click(self, widget, event):
        print "clicked drop button"
        # TODO
