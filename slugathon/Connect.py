#!/usr/bin/env python

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
        self.widgets = ['connect_window', 'player_name_combo', 
          'password_entry', 'server_name_combo', 'server_port_combo', 
          'connect_button', 'start_server_button']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        self.glade.signal_autoconnect(self)
        self.playerNames = None
        self.serverNames = None
        self.serverPorts = None
        self.init_lists()
        self.connect_window.connect("destroy", quit)
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          '../images/creature/Colossus.gif')
        self.connect_window.set_icon(pixbuf)
        self.connect_window.show()

    def init_lists(self):
        self.init_player_names()
        self.init_server_names()
        self.init_server_ports()

    def init_player_names(self):
        if not self.playerNames:
            self.playerNames = Set()
        self.playerNames.add(getpass.getuser())
        for name in self.playerNames:
            self.player_name_combo.insert_text(name)

    def init_server_names(self):
        if not self.serverNames:
            self.serverNames = Set()
        self.serverNames.add('localhost')
        for name in self.serverNames:
            self.server_name_combo.insert_text(name)

    def init_server_ports(self):
        if not self.serverPorts:
            self.serverPorts = Set()
        self.serverPorts.add(Server.DEFAULT_PORT)
        for name in self.serverPorts:
            self.server_port_combo.insert_text(str(name))

    def on_connectButton_clicked(self, *args):
        print "Connect button clicked"
        playerName = self.player_name_combo.get_text()
        password = self.password_entry.get_text()
        serverName = self.server_name_combo.get_text()
        serverPort = int(self.server_port_combo.get_text())
        print playerName, password, serverName, serverPort
        client = Client.Client(playerName, password, serverName, serverPort)
        def1 = client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def on_startServerButton_clicked(self, *args):
        print "Start server button clicked"
        #XXX Not portable  Use reactor.spawnProcess
        os.system("python Server.py &")

    def connected(self, user):
        print "Connect.connected", user
        self.connect_window.hide()

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

