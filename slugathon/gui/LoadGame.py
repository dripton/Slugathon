#!/usr/bin/env python

__copyright__ = "Copyright (c) 2008-2012 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
import gtk

from slugathon.gui import icon
from slugathon.util import prefs
from slugathon.util.NullUser import NullUser


class LoadGame(gtk.FileChooserDialog):
    """Load saved game dialog."""
    def __init__(self, user, playername, parent):
        title = "Load Saved Game - %s" % playername
        gtk.FileChooserDialog.__init__(self, title, parent,
          gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,
          gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.user = user
        self.playername = playername
        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_current_folder(prefs.SAVE_DIR)
        file_filter = gtk.FileFilter()
        file_filter.add_pattern(prefs.SAVE_GLOB)
        self.set_filter(file_filter)

        response = self.run()
        if response == gtk.RESPONSE_OK:
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
    user = NullUser()
    playername = "test user"
    loadgame = LoadGame(user, playername, None)
    loadgame.connect("destroy", lambda x: reactor.stop())
    reactor.run()
