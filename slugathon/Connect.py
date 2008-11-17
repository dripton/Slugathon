#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor
from twisted.internet import utils
import gtk.glade
import gobject

import Client
import icon
import guiutils
import prefs


class Connect(object):
    """GUI for connecting to a server."""
    def __init__(self):
        self.glade = gtk.glade.XML("../glade/connect.glade")
        self.widget_names = ["connect_window", "playername_comboboxentry",
          "password_entry", "server_name_comboboxentry",
          "server_port_comboboxentry", "connect_button",
          "start_server_button", "status_textview"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.glade.signal_autoconnect(self)
        self.playernames = set()
        self.server_names = set()
        self.server_ports = set()
        self._init_playernames()
        self._init_server_names_and_ports()
        self.connect_window.connect("destroy", guiutils.exit)
        self.connect_window.set_icon(icon.pixbuf)
        self.connect_window.show()

    def _init_playernames(self):
        self.playernames.update(prefs.load_playernames())
        store = gtk.ListStore(gobject.TYPE_STRING)
        for name in sorted(self.playernames):
            store.append([name])
        self.playername_comboboxentry.set_model(store)
        self.playername_comboboxentry.set_text_column(0)
        self.playername_comboboxentry.set_active(0)

    def _init_server_names_and_ports(self):
        server_entries = prefs.load_servers()
        for name, port in server_entries:
            self.server_names.add(name)
            self.server_ports.add(port)

        namestore = gtk.ListStore(gobject.TYPE_STRING)
        for name in sorted(self.server_names):
            namestore.append([name])
        self.server_name_comboboxentry.set_model(namestore)
        self.server_name_comboboxentry.set_text_column(0)
        self.server_name_comboboxentry.set_active(0)

        portstore = gtk.ListStore(gobject.TYPE_STRING)
        for port in sorted(self.server_ports):
            portstore.append([str(port)])
        self.server_port_comboboxentry.set_model(portstore)
        self.server_port_comboboxentry.set_text_column(0)
        self.server_port_comboboxentry.set_active(0)

    def on_connect_button_clicked(self, *args):
        playername = self.playername_comboboxentry.child.get_text()
        password = self.password_entry.get_text()
        server_name = self.server_name_comboboxentry.child.get_text()
        server_port = int(self.server_port_comboboxentry.child.get_text())
        prefs.save_server(server_name, server_port)
        client = Client.Client(playername, password, server_name, server_port)
        def1 = client.connect()
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def on_start_server_button_clicked(self, *args):
        utils.getProcessValue("python", ["Server.py"])

    def connected(self, user):
        self.connect_window.hide()

    def connection_failed(self, arg):
        self.status_textview.modify_text(gtk.STATE_NORMAL,
          gtk.gdk.color_parse("red"))
        self.status_textview.get_buffer().set_text("Login failed")


if __name__ == "__main__":
    connect = Connect()
    reactor.run()
