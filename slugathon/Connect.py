#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import sys
import os


class Connect:
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = glade.XML('../glade/connect.glade')
        self.widgets = ['connect', 'chooseServer', 'connectButton', 
          'startServerButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.glade.signal_autoconnect(self)
        self.connect.show()

    def on_connectButton_clicked(self, *args):
        button = args[0]
        print "Connect button clicked", button

    def on_startServerButton_clicked(self, *args):
        button = args[0]
        print "Start server button clicked", button
        # XXX Not portable
        os.system("python2.3 Server.py &")


def quit(unused):
    sys.exit()

if __name__ == '__main__':
    connect = Connect()
    connect.connect.connect("destroy", quit)
    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/creature/Colossus.gif')
    connect.connect.set_icon(pixbuf)

    while 1:
        gtk.mainiteration()

