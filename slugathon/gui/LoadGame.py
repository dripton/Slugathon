#!/usr/bin/env python3

__copyright__ = "Copyright (c) 2008-2021 David Ripton"
__license__ = "GNU GPL v2"


import gi

gi.require_version("Gtk", "3.0")
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
from gi.repository import Gtk

from slugathon.gui import icon
from slugathon.util import prefs
from slugathon.util.NullUser import NullUser


class LoadGame(Gtk.FileChooserDialog):

    """Load saved game dialog."""

    def __init__(self, user, playername, parent):
        title = f"Load Saved Game - {playername}"
        Gtk.FileChooserDialog.__init__(
            self, title=title, parent=parent, action=Gtk.FileChooserAction.OPEN
        )
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        self.user = user
        self.playername = playername
        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_current_folder(prefs.SAVE_DIR)
        file_filter = Gtk.FileFilter()
        file_filter.add_pattern(prefs.SAVE_GLOB)
        self.set_filter(file_filter)

        response = self.run()
        if response == Gtk.ResponseType.OK:
            self.ok()
        else:
            self.cancel()

    def ok(self):
        filename = self.get_filename()
        def1 = self.user.callRemote("load_game", filename)
        def1.addErrback(self.failure)
        self.destroy()

    def cancel(self):
        self.destroy()

    def failure(self, error):
        log.err(error)


if __name__ == "__main__":

    def my_callback(*args):
        reactor.stop()

    user = NullUser()
    playername = "test user"
    window = Gtk.Window()
    window.connect("destroy", my_callback)
    loadgame = LoadGame(user, playername, window)
    reactor.run()  # type: ignore[attr-defined]
