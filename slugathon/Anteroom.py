#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import sys


class Anteroom:
    """GUI for a multiplayer chat and game finding lobby."""
    def __init__(self):
        self.glade = glade.XML('../glade/anteroom.glade')
        self.widgets = ['anteroom', 'chatEntry', 'chatView', 'gamesTree',
          'playerList']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.anteroom.show()


def quit(unused):
    sys.exit()

if __name__ == '__main__':
    anteroom = Anteroom()
    anteroom.anteroom.connect("destroy", quit)
    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/creature/Colossus.gif')
    anteroom.anteroom.set_icon(pixbuf)

    while 1:
        gtk.mainiteration()
