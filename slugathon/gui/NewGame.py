#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from twisted.python import log

from slugathon.gui import icon, InfoDialog
from slugathon.util.NullUser import NullUser
from slugathon.net import config


class NewGame(gtk.Dialog):
    """Form new game dialog."""
    def __init__(self, user, playername, parent_window):
        gtk.Dialog.__init__(self, "Form New Game - %s" % playername,
          parent_window)
        self.game_name = None
        self.min_players = None
        self.max_players = None
        self.user = user
        self.playername = playername
        self.parent_window = parent_window

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent_window)
        self.set_destroy_with_parent(True)

        hbox1 = gtk.HBox()
        self.vbox.pack_start(hbox1)
        label1 = gtk.Label("Name of game")
        hbox1.pack_start(label1, expand=False)
        self.name_entry = gtk.Entry(max=40)
        self.name_entry.set_width_chars(40)
        hbox1.pack_start(self.name_entry, expand=False)

        min_adjustment = gtk.Adjustment(2, 2, 6, 1, 0, 0)
        max_adjustment = gtk.Adjustment(6, 2, 6, 1, 0, 0)
        ai_time_limit_adjustment = gtk.Adjustment(config.DEFAULT_AI_TIME_LIMIT,
          1, 99, 1, 0, 0)
        player_time_limit_adjustment = gtk.Adjustment(
          config.DEFAULT_PLAYER_TIME_LIMIT, 1, 999, 1, 100, 0)

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
        label4 = gtk.Label("AI time limit")
        hbox2.pack_start(label4, expand=False)
        self.ai_time_limit_spin = gtk.SpinButton(
          adjustment=ai_time_limit_adjustment,
          climb_rate=1, digits=0)
        self.ai_time_limit_spin.set_numeric(True)
        self.ai_time_limit_spin.set_update_policy(gtk.UPDATE_IF_VALID)
        hbox2.pack_start(self.ai_time_limit_spin, expand=False)
        label5 = gtk.Label("Player time limit")
        hbox2.pack_start(label5, expand=False)
        self.player_time_limit_spin = gtk.SpinButton(
          adjustment=player_time_limit_adjustment,
          climb_rate=1, digits=0)
        self.player_time_limit_spin.set_numeric(True)
        self.player_time_limit_spin.set_update_policy(gtk.UPDATE_IF_VALID)
        hbox2.pack_start(self.player_time_limit_spin, expand=False)

        self.cancel_button = self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.cancel_button.connect("button-press-event", self.cancel)
        self.ok_button = self.add_button("gtk-ok", gtk.RESPONSE_OK)
        self.ok_button.connect("button-press-event", self.ok)

        self.show_all()

    def ok(self, widget, event):
        if self.name_entry.get_text():
            self.game_name = self.name_entry.get_text()
            self.min_players = self.min_players_spin.get_value_as_int()
            self.max_players = self.max_players_spin.get_value_as_int()
            self.ai_time_limit = self.ai_time_limit_spin.get_value_as_int()
            self.player_time_limit = \
              self.player_time_limit_spin.get_value_as_int()
            def1 = self.user.callRemote("form_game", self.game_name,
              self.min_players, self.max_players, self.ai_time_limit,
              self.player_time_limit, "Human", "")
            def1.addCallback(self.got_information)
            def1.addErrback(self.failure)
            self.destroy()

    def cancel(self, widget, event):
        self.destroy()

    def failure(self, error):
        log.err(error)

    def got_information(self, information):
        if information:
            InfoDialog.InfoDialog(self.parent_window, "Info", str(information))


if __name__ == "__main__":
    from slugathon.util import guiutils

    user = NullUser()
    playername = "test user"
    newgame = NewGame(user, playername, None)
    newgame.connect("destroy", guiutils.exit)
    gtk.main()
