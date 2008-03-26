#!/usr/bin/env python

import os

import gtk
from twisted.internet import defer

import icon
import guiutils


class LoadGame(object):
    """Load saved game dialog."""
    def __init__(self, user, username, parent):
        self.name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.username = username
        title = "Load Saved Game - %s" % self.username
        self.load_game_dialog = gtk.FileChooserDialog(title, parent, 
          gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, 
          gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.load_game_dialog.set_icon(icon.pixbuf)
        # TODO Hoist constants somewhere
        savedir = os.path.expanduser("~/.slugathon/save")
        self.load_game_dialog.set_current_folder(savedir)
        file_filter = gtk.FileFilter()
        # TODO Hoist constants somewhere
        file_filter.add_pattern("*.save")
        self.load_game_dialog.set_filter(file_filter)

        response = self.load_game_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.ok()
        else:
            self.cancel()

    def ok(self): 
        filename = self.load_game_dialog.get_filename()
        def1 = self.user.callRemote("load_game", filename)
        def1.addErrback(self.failure)
        self.load_game_dialog.destroy()

    def cancel(self): 
        self.load_game_dialog.destroy()

    def failure(self, error): 
        print "LoadGame", error


if __name__ == "__main__":
    class NullUser(object):
        def callRemote(*args):
            return defer.Deferred()

    user = NullUser()
    username = "test user"
    loadgame = LoadGame(user, username, None)
    loadgame.load_game_dialog.connect("destroy", guiutils.exit)
    gtk.main()
