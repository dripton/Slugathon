#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor
from twisted.internet import utils
import gtk
import gtk.glade
import gobject

import getpass
import Server
import Client
import icon
import guiutils


class Connect(object):
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = gtk.glade.XML("../glade/connect.glade")
        self.widget_names = ["connect_window", "playername_comboboxentry",
          "password_entry", "server_name_comboboxentry",
          "server_port_comboboxentry", "connect_button", "start_server_button"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.glade.signal_autoconnect(self)
        self.playernames = None
        self.server_names = None
        self.server_ports = None
        self.init_lists()
        self.connect_window.connect("destroy", guiutils.exit)
        self.connect_window.set_icon(icon.pixbuf)
        self.connect_window.show()

    def init_lists(self):
        self.init_playernames()
        self.init_server_names()
        self.init_server_ports()

    def init_playernames(self):
        if not self.playernames:
            self.playernames = set()
        self.playernames.add(getpass.getuser())
        store = gtk.ListStore(gobject.TYPE_STRING)
        for name in self.playernames:
            store.append([name])
        self.playername_comboboxentry.set_model(store)
        self.playername_comboboxentry.set_text_column(0)
        self.playername_comboboxentry.set_active(0)

    def init_server_names(self):
        if not self.server_names:
            self.server_names = set()
        self.server_names.add("localhost")
        store = gtk.ListStore(gobject.TYPE_STRING)
        for name in self.server_names:
            store.append([name])
        self.server_name_comboboxentry.set_model(store)
        self.server_name_comboboxentry.set_text_column(0)
        self.server_name_comboboxentry.set_active(0)

    def init_server_ports(self):
        if not self.server_ports:
            self.server_ports = set()
        self.server_ports.add(Server.DEFAULT_PORT)
        store = gtk.ListStore(gobject.TYPE_STRING)
        for name in self.server_ports:
            store.append([str(name)])
        self.server_port_comboboxentry.set_model(store)
        self.server_port_comboboxentry.set_text_column(0)
        self.server_port_comboboxentry.set_active(0)

    def on_connect_button_clicked(self, *args):
        playername = self.playername_comboboxentry.child.get_text()
        password = self.password_entry.get_text()
        server_name = self.server_name_comboboxentry.child.get_text()
        server_port = int(self.server_port_comboboxentry.child.get_text())
        client = Client.Client(playername, password, server_name, server_port)
        def1 = client.connect()
        def1.addCallback(self.connected)
        def1.addErrback(self.failure)

    def on_start_server_button_clicked(self, *args):
        utils.getProcessValue("python", ["Server.py"])

    def connected(self, user):
        self.connect_window.hide()

    def failure(self, arg):
        print "Connect.failure", arg
        guiutils.exit(None)


if __name__ == "__main__":
    connect = Connect()
    reactor.run()
