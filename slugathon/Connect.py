#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except (ImportError, AttributeError):
    pass
from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor
import gtk
import gtk.glade
import sys
import os
import getpass
from sets import Set
import Server
import Client


class Connect:
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = gtk.glade.XML('../glade/connect.glade')
        self.widgets = ['connectWindow', 'playerNameCombo', 'passwordEntry', 
          'serverNameCombo', 'serverPortCombo', 'connectButton', 
          'startServerButton']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.glade.signal_autoconnect(self)
        self.playerNames = None
        self.serverNames = None
        self.serverPorts = None
        self.load_prefs()
        self.init_lists()
        self.connectWindow.connect("destroy", quit)
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.connectWindow.set_icon(pixbuf)
        self.connectWindow.show()

    def load_prefs(self):
        pass

    def save_prefs(self):
        pass

    def init_lists(self):
        self.init_player_names()
        self.init_server_names()
        self.init_server_ports()

    def init_player_names(self):
        if not self.playerNames:
            self.playerNames = Set()
        self.playerNames.add(getpass.getuser())
        for name in self.playerNames:
            self.playerNameCombo.insert_text(name)

    def init_server_names(self):
        if not self.serverNames:
            self.serverNames = Set()
        self.serverNames.add('localhost')
        for name in self.serverNames:
            self.serverNameCombo.insert_text(name)

    def init_server_ports(self):
        if not self.serverPorts:
            self.serverPorts = Set()
        self.serverPorts.add(Server.DEFAULT_PORT)
        for name in self.serverPorts:
            self.serverPortCombo.insert_text(str(name))

    def on_connectButton_clicked(self, *args):
        print "Connect button clicked"
        playerName = self.playerNameCombo.get_text()
        password = self.passwordEntry.get_text()
        serverName = self.serverNameCombo.get_text()
        serverPort = int(self.serverPortCombo.get_text())
        print playerName, password, serverName, serverPort
        client = Client.Client(playerName, password, serverName, serverPort)
        def1 = client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def on_startServerButton_clicked(self, *args):
        print "Start server button clicked"
        #XXX Not portable  Use reactor.spawnProcess
        os.system("python2.3 Server.py &")

    def connected(self, user):
        print "Connect.connected", user
        self.connectWindow.hide()

    def failure(self, arg):
        print "Connect.failure", arg
        quit(None)

def quit(unused):
    reactor.stop()
    sys.exit()

if __name__ == '__main__':
    connect = Connect()
    reactor.run()

    while True:
        gtk.mainiteration()

