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
from sets import Set
import Server


class Connect:
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = glade.XML('../glade/connect.glade')
        self.widgets = ['connectWindow', 'playerNameCombo', 'passwordEntry', 
          'serverNameCombo', 'serverPortCombo', 'connectButton', 
          'startServerButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.glade.signal_autoconnect(self)
        self.playerNames = None
        self.serverNames = None
        self.serverPorts = None
        self.init_lists()
        self.connectWindow.show()

    def init_lists(self):
        self.load_prefs()
        self.init_player_names()
        self.init_server_names()
        self.init_server_ports()

    def load_prefs(self):
        pass

    def save_prefs(self):
        pass

    def init_player_names(self):
        if not self.playerNames:
            self.playerNames = Set()
        # XXX Not portable
        self.playerNames.add(os.getenv('USER'))

    def init_server_names(self):
        if not self.serverNames:
            self.serverNames = Set()
        self.serverNames.add('localhost')

    def init_server_ports(self):
        if not self.serverPorts:
            self.serverPorts = Set()
        self.serverPorts.add(Server.DEFAULT_PORT)

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
    connect.connectWindow.connect("destroy", quit)
    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/creature/Colossus.gif')
    connect.connectWindow.set_icon(pixbuf)

    while 1:
        gtk.mainiteration()

