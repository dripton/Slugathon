#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import sys


class Connect:
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = glade.XML('../glade/connect.glade')
        self.widgets = ['connect', 'chooseServer', 'connectButton', 
          'startServerButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.connect.show()

def quit(unused):
    sys.exit()

if __name__ == '__main__':
    connect = Connect()
    connect.connect.connect("destroy", quit)
    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/creature/Colossus.gif')
    connect.connect.set_icon(pixbuf)

    while 1:
        gtk.mainiteration()

