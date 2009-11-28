#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2009 David Ripton"
__license__ = "GNU GPL v2"


from optparse import OptionParser

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor
from twisted.internet import utils
import gtk
import gobject

from slugathon.gui import Client, icon
from slugathon.util import guiutils, prefs


class Connect(object):
    """GUI for connecting to a server."""
    def __init__(self, playername, password, server_name, server_port):
        self.builder = gtk.Builder()
        self.builder.add_from_file(guiutils.basedir("ui/connect.ui"))
        self.widget_names = ["connect_window", "playername_comboboxentry",
          "password_entry", "server_name_comboboxentry",
          "server_port_comboboxentry", "connect_button",
          "start_server_button", "status_textview"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))
        self.builder.connect_signals(self)
        self.playernames = set()
        self.server_names = set()
        self.server_ports = set()
        self._init_playernames(playername)
        self._init_password(password)
        self._init_server_names_and_ports(server_name, server_port)
        self.connect_window.connect("destroy", guiutils.exit)
        self.connect_window.set_icon(icon.pixbuf)
        self.connect_window.show()

    def _init_playernames(self, playername):
        self.playernames.update(prefs.load_playernames())
        if playername:
            self.playernames.add(playername)
        else:
            playername = prefs.last_playername()
        store = gtk.ListStore(gobject.TYPE_STRING)
        active_index = 0
        for index, name in enumerate(sorted(self.playernames)):
            store.append([name])
            if name == playername:
                active_index = index
        self.playername_comboboxentry.set_model(store)
        self.playername_comboboxentry.set_text_column(0)
        self.playername_comboboxentry.set_active(active_index)

    def _init_password(self, password):
        if password:
            self.password_entry.set_text(password)

    def _init_server_names_and_ports(self, server_name, server_port):
        last_server_name, last_server_port = prefs.load_last_server()
        server_entries = prefs.load_servers()
        for name, port in server_entries:
            self.server_names.add(name)
            self.server_ports.add(port)
        if server_name:
            self.server_names.add(server_name)
        else:
            server_name = last_server_name
        if server_port:
            self.server_ports.add(server_port)
        else:
            server_port = last_server_port

        namestore = gtk.ListStore(gobject.TYPE_STRING)
        active_index = 0
        for index, name in enumerate(sorted(self.server_names)):
            namestore.append([name])
            if name == server_name:
                active_index = index
        self.server_name_comboboxentry.set_model(namestore)
        self.server_name_comboboxentry.set_text_column(0)
        self.server_name_comboboxentry.set_active(active_index)

        active_index = 0
        portstore = gtk.ListStore(gobject.TYPE_STRING)
        for index, port in enumerate(sorted(self.server_ports)):
            portstore.append([str(port)])
            if port == server_port:
                active_index = index
        self.server_port_comboboxentry.set_model(portstore)
        self.server_port_comboboxentry.set_text_column(0)
        self.server_port_comboboxentry.set_active(active_index)

    def on_connect_button_clicked(self, *args):
        playername = self.playername_comboboxentry.child.get_text()
        password = self.password_entry.get_text()
        server_name = self.server_name_comboboxentry.child.get_text()
        server_port = int(self.server_port_comboboxentry.child.get_text())
        prefs.save_server(server_name, server_port)
        prefs.save_last_playername(playername)
        client = Client.Client(playername, password, server_name, server_port)
        def1 = client.connect()
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def on_start_server_button_clicked(self, *args):
        utils.getProcessValue("python", ["slugathon-server"])

    def connected(self, user):
        self.connect_window.hide()

    def connection_failed(self, arg):
        self.status_textview.modify_text(gtk.STATE_NORMAL,
          gtk.gdk.color_parse("red"))
        self.status_textview.get_buffer().set_text("Login failed")


def main():
    op = OptionParser()
    op.add_option("-n", "--playername", action="store", type="str")
    op.add_option("-a", "--password", action="store", type="str")
    op.add_option("-s", "--server", action="store", type="str")
    op.add_option("-p", "--port", action="store", type="int")
    opts, args = op.parse_args()
    if args:
        op.error("got illegal argument")
    connect = Connect(opts.playername, opts.password, opts.server, opts.port)
    reactor.run()

if __name__ == "__main__":
    main()
