#!/usr/bin/env python

try:
    import pygtk
    pygtk.require("2.0")
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
import Server
import Client


class Connect(object):
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = gtk.glade.XML("../glade/connect.glade")
        self.widgets = ["connect_window", "playername_combo", 
          "password_entry", "server_name_combo", "server_port_combo", 
          "connect_button", "start_server_button"]
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.glade.signal_autoconnect(self)
        self.playernames = None
        self.server_names = None
        self.server_ports = None
        self.init_lists()
        self.connect_window.connect("destroy", quit)
        pixbuf = gtk.gdk.pixbuf_new_from_file(
          "../images/creature/Colossus.png")
        self.connect_window.set_icon(pixbuf)
        self.connect_window.show()

    def init_lists(self):
        self.init_playernames()
        self.init_server_names()
        self.init_server_ports()

    def init_playernames(self):
        if not self.playernames:
            self.playernames = set()
        self.playernames.add(getpass.getuser())
        for name in self.playernames:
            self.playername_combo.insert_text(name)

    def init_server_names(self):
        if not self.server_names:
            self.server_names = set()
        self.server_names.add("localhost")
        for name in self.server_names:
            self.server_name_combo.insert_text(name)

    def init_server_ports(self):
        if not self.server_ports:
            self.server_ports = set()
        self.server_ports.add(Server.DEFAULT_PORT)
        for name in self.server_ports:
            self.server_port_combo.insert_text(str(name))

    def on_connect_button_clicked(self, *args):
        print "Connect button clicked"
        playername = self.playername_combo.get_text()
        password = self.password_entry.get_text()
        server_name = self.server_name_combo.get_text()
        server_port = int(self.server_port_combo.get_text())
        print playername, password, server_name, server_port
        client = Client.Client(playername, password, server_name, server_port)
        def1 = client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def on_start_server_button_clicked(self, *args):
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

if __name__ == "__main__":
    connect = Connect()
    reactor.run()

    while True:
        gtk.main_iteration()

