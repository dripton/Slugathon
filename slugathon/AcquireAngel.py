#!/usr/bin/env python

__copyright__ = "Copyright (c) 2007-2008 David Ripton"
__license__ = "GNU GPL v2"


import time

import gtk
import gtk.glade

import Chit
import Marker
import Creature
import Legion
import Player
import icon
import guiutils
import Game


class AcquireAngel(object):
    """Dialog to acquire an angel."""
    def __init__(self, username, player, legion, available_angels,
      callback, parent):
        self.callback = callback
        self.glade = gtk.glade.XML("../glade/acquireangel.glade")
        self.widget_names = ["acquire_angel_dialog", "marker_hbox",
          "chits_hbox", "angels_hbox", "legion_name"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.acquire_angel_dialog.set_icon(icon.pixbuf)
        self.acquire_angel_dialog.set_title("AcquireAngel - %s" % (username))
        self.acquire_angel_dialog.set_transient_for(parent)

        self.legion_name.set_text("Acquire angel for legion %s in hex %s" % (
          legion.markername, legion.hexlabel))

        self.player = player
        self.legion = legion

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False,
          fill=False)
        self.marker.show()

        for creature in legion.sorted_creatures():
            chit = Chit.Chit(creature, player.color, scale=20)
            chit.show()
            self.chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)

        angels = Creature.n2c(available_angels)
        for angel in angels:
            chit = Chit.Chit(angel, player.color, scale=20)
            chit.show()
            self.angels_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button_press_event", self.cb_click)

        self.acquire_angel_dialog.connect("response", self.cb_response)
        self.acquire_angel_dialog.show()


    def cb_click(self, widget, event):
        """Acquire an angel."""
        eventbox = widget
        if eventbox in self.angels_hbox.get_children():
            chit = eventbox.chit
            self.callback(self.legion, chit.creature)
            self.acquire_angel_dialog.destroy()

    def cb_response(self, dialog, response_id):
        """The cancel button was pressed, so exit"""
        self.acquire_angel_dialog.destroy()


if __name__ == "__main__":
    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def callback(legion, creature):
        print legion, "acquired", creature
        guiutils.exit

    now = time.time()
    username = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    available_angels = ["Archangel", "Angel"]
    acquireangel = AcquireAngel(username, player, legion, available_angels,
      callback, None)
    acquireangel.acquire_angel_dialog.connect("destroy", guiutils.exit)

    gtk.main()
