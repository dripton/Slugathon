#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import icon
from slugathon.util.NullUser import NullUser
from slugathon.util.log import log


class NewGame(gtk.Dialog):
    """Form new game dialog."""
    def __init__(self, user, username, parent):
        gtk.Dialog.__init__(self, "Form New Game - %s" % username, parent)
        self.game_name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.username = username

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)

        hbox1 = gtk.HBox()
        self.vbox.pack_start(hbox1)
        label1 = gtk.Label("Name of game")
        hbox1.pack_start(label1, expand=False)
        self.name_entry = gtk.Entry(max=40)
        self.name_entry.set_width_chars(40)
        hbox1.pack_start(self.name_entry, expand=False)

        min_adjustment = gtk.Adjustment(2, 2, 6, 1, 0, 0)
        max_adjustment = gtk.Adjustment(6, 2, 6, 1, 0, 0)

        hbox2 = gtk.HBox()
        self.vbox.pack_start(hbox2)
        label2 = gtk.Label("Min players")
        hbox2.pack_start(label2, expand=False)
        self.min_players_spin = gtk.SpinButton(adjustment=min_adjustment,
          climb_rate=1, digits=0)
        self.min_players_spin.set_numeric(True)
        self.min_players_spin.set_update_policy(gtk.UPDATE_IF_VALID)
        self.min_players_spin.set_value(2)
        hbox2.pack_start(self.min_players_spin, expand=False)
        label3 = gtk.Label("Max players")
        hbox2.pack_start(label3, expand=False)
        self.max_players_spin = gtk.SpinButton(adjustment=max_adjustment,
          climb_rate=1, digits=0)
        self.max_players_spin.set_numeric(True)
        self.max_players_spin.set_update_policy(gtk.UPDATE_IF_VALID)
        self.max_players_spin.set_value(6)
        hbox2.pack_start(self.max_players_spin, expand=False)

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.add_button("gtk-ok", gtk.RESPONSE_OK)

        self.show_all()

        response = self.run()
        if response == gtk.RESPONSE_OK:
            self.ok()
        else:
            self.cancel()

    def ok(self):
        self.game_name = self.name_entry.get_text()
        self.min_players = self.min_players_spin.get_value_as_int()
        self.max_players = self.max_players_spin.get_value_as_int()
        def1 = self.user.callRemote("form_game", self.game_name,
          self.min_players, self.max_players)
        def1.addErrback(self.failure)
        self.destroy()

    def cancel(self):
        self.destroy()

    def failure(self, error):
        log(error)


if __name__ == "__main__":
    from slugathon.util import guiutils

    user = NullUser()
    username = "test user"
    newgame = NewGame(user, username, None)
    newgame.connect("destroy", guiutils.exit)
    gtk.main()
