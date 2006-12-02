#!/usr/bin/env python

import time

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import zope.interface

import icon
import guiutils
from Observer import IObserver
import Game
import Player


class StatusScreen(gtk.Window):
    """Game status window."""

    zope.interface.implements(IObserver)

    def __init__(self, game, user, username):
        gtk.Window.__init__(self)

        self.game = game
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML("../glade/statusscreen.glade")
        self.widgets = ["status_screen_window", "turn_table", "player_table",
          "game_turn_label", "game_player_label", "game_phase_label",
          "battle_turn_label", "battle_player_label", "battle_phase_label",
        ]
        num_players = len(self.game.players)
        for num in xrange(num_players):
            self.widgets.append("name%d_label" % num)
            self.widgets.append("tower%d_label" % num)
            self.widgets.append("color%d_label" % num)
            self.widgets.append("legions%d_label" % num)
            self.widgets.append("markers%d_label" % num)
            self.widgets.append("creatures%d_label" % num)
            self.widgets.append("titansize%d_label" % num)
            self.widgets.append("eliminated%d_label" % num)
            self.widgets.append("score%d_label" % num)
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        self.status_screen_window.set_icon(icon.pixbuf)
        self.status_screen_window.set_title("%s - %s" % (
          self.status_screen_window.get_title(), self.username))
        self.status_screen_window.show()

    def update(self, observed, action):
        print "StatusScreen.update", self, observed, action

if __name__ == "__main__":
    now = time.time()
    user = None
    username = "test user"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, "g1", 0)
    player.color = "Red"
    status_screen = StatusScreen(game, user, username)
    status_screen.status_screen_window.connect("destroy", guiutils.die)
    gtk.main()

