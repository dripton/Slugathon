#!/usr/bin/env python

import gtk
import gtk.glade
from twisted.internet import defer

import icon
import guiutils


class NewGame(object):
    """Form new game dialog."""
    def __init__(self, user, username, parent):
        self.name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML("../glade/newgame.glade")
        self.widget_names = ["new_game_dialog", "name_entry",
          "min_players_spin", "max_players_spin"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.new_game_dialog.set_icon(icon.pixbuf)
        self.new_game_dialog.set_title("%s - %s" % (
          self.new_game_dialog.get_title(), self.username))
        self.new_game_dialog.set_transient_for(parent)

        response = self.new_game_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.ok()
        else:
            self.cancel()

    def ok(self):
        self.name = self.name_entry.get_text()
        self.min_players = self.min_players_spin.get_value_as_int()
        self.max_players = self.max_players_spin.get_value_as_int()
        def1 = self.user.callRemote("form_game", self.name, self.min_players,
          self.max_players)
        def1.addErrback(self.failure)
        self.new_game_dialog.destroy()

    def cancel(self):
        self.new_game_dialog.destroy()

    def failure(self, error):
        print "NewGame", error


if __name__ == "__main__":
    class NullUser(object):
        def callRemote(*args):
            return defer.Deferred()

    user = NullUser()
    username = "test user"
    newgame = NewGame(user, username, None)
    newgame.new_game_dialog.connect("destroy", guiutils.exit)
    gtk.main()
