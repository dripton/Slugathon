#!/usr/bin/env python3

__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


import argparse
import os
import tempfile
import sys
import time
import logging

import gi

gi.require_version("Gtk", "3.0")
from twisted.internet import gtk3reactor

gtk3reactor.install()
from twisted.internet import reactor, utils, defer
from twisted.python import log
from gi.repository import GObject, Gtk, Gdk

from slugathon.gui import Client, icon
from slugathon.util import guiutils, prefs


defer.setDebugging(True)


class Connect(Gtk.Window):

    """GUI for connecting to a server."""

    def __init__(
        self,
        playername,
        password,
        server_name,
        server_port,
        connect_now,
        log_path,
    ):
        GObject.GObject.__init__(self)

        self.playernames = set()
        self.server_names = set()
        self.server_ports = set()

        self.set_title("Slugathon - Connect")
        self.set_default_size(400, -1)

        vbox1 = Gtk.VBox()
        self.add(vbox1)

        hbox1 = Gtk.HBox(homogeneous=True)
        vbox1.pack_start(hbox1, False, True, 0)
        label1 = Gtk.Label(label="Player name")
        hbox1.pack_start(label1, False, True, 0)
        self.playername_comboboxentry = Gtk.ComboBox().new_with_entry()
        hbox1.pack_start(self.playername_comboboxentry, False, True, 0)

        hbox2 = Gtk.HBox(homogeneous=True)
        vbox1.pack_start(hbox2, False, True, 0)
        label2 = Gtk.Label(label="Password")
        hbox2.pack_start(label2, False, True, 0)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        hbox2.pack_start(self.password_entry, False, True, 0)

        hbox3 = Gtk.HBox(homogeneous=True)
        vbox1.pack_start(hbox3, False, True, 0)
        label3 = Gtk.Label(label="Server name")
        hbox3.pack_start(label3, False, True, 0)
        self.server_name_comboboxentry = Gtk.ComboBox().new_with_entry()
        hbox3.pack_start(self.server_name_comboboxentry, False, True, 0)

        hbox4 = Gtk.HBox(homogeneous=True)
        vbox1.pack_start(hbox4, False, True, 0)
        label4 = Gtk.Label(label="Server port")
        hbox4.pack_start(label4, False, True, 0)
        self.server_port_comboboxentry = Gtk.ComboBox().new_with_entry()
        hbox4.pack_start(self.server_port_comboboxentry, False, True, 0)

        connect_button = Gtk.Button(label="Connect to server")
        connect_button.connect(
            "button-press-event", self.cb_connect_button_clicked
        )
        vbox1.pack_start(connect_button, False, True, 0)

        hseparator1 = Gtk.HSeparator()
        vbox1.pack_start(hseparator1, False, True, 0)

        start_server_button = Gtk.Button(label="Start local server")
        start_server_button.connect(
            "button-press-event", self.cb_start_server_button_clicked
        )
        vbox1.pack_start(start_server_button, False, True, 0)

        hseparator2 = Gtk.HSeparator()
        vbox1.pack_start(hseparator2, False, True, 0)

        self.status_textview = Gtk.TextView()
        vbox1.pack_start(self.status_textview, False, True, 0)

        self._init_playernames(playername)
        self._init_password(password)
        self._init_server_names_and_ports(server_name, server_port)

        self.connect("destroy", guiutils.exit)
        self.connect("configure-event", self.cb_configure_event)
        self.set_icon(icon.pixbuf)

        tup = prefs.load_global_window_position(self.__class__.__name__)
        if tup:
            x, y = tup
            self.move(x, y)
        tup = prefs.load_global_window_size(self.__class__.__name__)
        if tup:
            width, height = tup
            self.resize(width, height)

        self.show_all()

        self._setup_logging(log_path)

        if connect_now:
            reactor.callWhenRunning(self.cb_connect_button_clicked)

    def _setup_logging(self, log_path):
        log_observer = log.PythonLoggingObserver()
        log_observer.start()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d "
            "%(message)s"
        )
        if log_path:
            file_handler = logging.FileHandler(filename=log_path)
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def _init_playernames(self, playername):
        self.playernames.update(prefs.load_playernames())
        if not playername:
            playername = prefs.last_playername()
        self.playernames.add(playername)
        store = Gtk.ListStore(GObject.TYPE_STRING)
        active_index = 0
        for index, name in enumerate(sorted(self.playernames)):
            store.append([name])
            if name == playername:
                active_index = index
        self.playername_comboboxentry.set_model(store)
        self.playername_comboboxentry.set_entry_text_column(0)
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

        namestore = Gtk.ListStore(GObject.TYPE_STRING)
        active_index = 0
        for index, name in enumerate(sorted(self.server_names)):
            namestore.append([name])
            if name == server_name:
                active_index = index
        self.server_name_comboboxentry.set_model(namestore)
        self.server_name_comboboxentry.set_entry_text_column(0)
        self.server_name_comboboxentry.set_active(active_index)

        active_index = 0
        portstore = Gtk.ListStore(GObject.TYPE_STRING)
        for index, port in enumerate(sorted(self.server_ports)):
            portstore.append([str(port)])
            if port == server_port:
                active_index = index
        self.server_port_comboboxentry.set_model(portstore)
        self.server_port_comboboxentry.set_entry_text_column(0)
        self.server_port_comboboxentry.set_active(active_index)

    def cb_connect_button_clicked(self, *args):
        playername = self.playername_comboboxentry.get_child().get_text()
        password = self.password_entry.get_text()
        server_name = self.server_name_comboboxentry.get_child().get_text()
        server_port = int(
            self.server_port_comboboxentry.get_child().get_text()
        )
        prefs.save_server(server_name, server_port)
        prefs.save_last_playername(playername)
        self.save_window_position()
        client = Client.Client(playername, password, server_name, server_port)
        def1 = client.connect()
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def cb_start_server_button_clicked(self, *args):
        if hasattr(sys, "frozen"):
            # TODO Find the absolute path.
            def1 = utils.getProcessValue(
                "slugathon.exe", ["server", "-n"], env=os.environ
            )
        else:
            def1 = utils.getProcessValue(
                sys.executable,
                ["-m", "slugathon.net.Server", "-n"],
                env=os.environ,
            )
        def1.addCallback(self.server_exited)
        def1.addErrback(self.server_failed)

    def server_exited(self, returncode):
        logging.info("server exited with returncode %d" % returncode)

    def save_window_position(self):
        x, y = self.get_position()
        prefs.save_global_window_position(self.__class__.__name__, x, y)
        width, height = self.get_size()
        prefs.save_global_window_size(self.__class__.__name__, width, height)

    def cb_configure_event(self, event, unused):
        self.save_window_position()
        return False

    def connected(self, user):
        self.hide()

    def connection_failed(self, arg):
        self.status_textview.modify_text(
            Gtk.StateType.NORMAL, Gdk.color_parse("red")
        )
        self.status_textview.get_buffer().set_text("Login failed")

    def server_failed(self, arg):
        self.status_textview.modify_text(
            Gtk.StateType.NORMAL, Gdk.color_parse("red")
        )
        self.status_textview.get_buffer().set_text(
            "Server failed %s" % str(arg)
        )


def add_arguments(parser):
    tempdir = tempfile.gettempdir()
    logdir = os.path.join(tempdir, "slugathon")
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    parser.add_argument("-n", "--playername", action="store", type=str)
    parser.add_argument("-a", "--password", action="store", type=str)
    parser.add_argument("-s", "--server", action="store", type=str)
    parser.add_argument("-p", "--port", action="store", type=int)
    parser.add_argument("-c", "--connect", action="store_true")
    parser.add_argument(
        "-l",
        "--log-path",
        action="store",
        type=str,
        default=os.path.join(
            logdir, "slugathon-client-%d.log" % int(time.time())
        ),
        help="path to logfile",
    )


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args, extras = parser.parse_known_args()
    Connect(
        args.playername,
        args.password,
        args.server,
        args.port,
        args.connect,
        args.log_path,
    )
    reactor.run()


if __name__ == "__main__":
    main()
