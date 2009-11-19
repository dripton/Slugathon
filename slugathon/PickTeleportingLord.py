#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"


import time

import gtk

import Chit
import Marker
import Creature
import Legion
import Player
import icon
import guiutils
import Game


class PickTeleportingLord(object):
    """Dialog to pick a lord to reveal for tower teleport."""
    def __init__(self, username, legion, callback, parent):
        self.legion = legion
        self.callback = callback
        self.builder = gtk.Builder()

        self.builder.add_from_file("../ui/pickteleportinglord.ui")
        self.widget_names = ["pick_teleporting_lord_dialog", "top_label",
          "bottom_label", "vbox1"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.pick_teleporting_lord_dialog.set_icon(icon.pixbuf)
        self.pick_teleporting_lord_dialog.set_title(
          "PickTeleportingLord - %s" % username)
        self.pick_teleporting_lord_dialog.set_transient_for(parent)

        self.top_label.set_text("Pick teleporting lord for legion %s"
          % legion.markername)

        hbox = gtk.HBox(spacing=3)
        hbox.show()
        self.vbox1.pack_start(hbox)
        marker = Marker.Marker(legion, False, scale=20)
        hbox.pack_start(marker.event_box, expand=False, fill=False)
        marker.show()
        player = self.legion.player
        for creature in legion.sorted_creatures():
            chit = Chit.Chit(creature, player.color, scale=20,
              outlined=creature.is_lord)
            chit.show()
            hbox.pack_start(chit.event_box, expand=False, fill=False)
            if creature.is_lord:
                chit.connect("button-press-event", self.cb_click)

        self.pick_teleporting_lord_dialog.connect("response", self.cb_response)
        self.pick_teleporting_lord_dialog.show()

    def cb_click(self, widget, event):
        eventbox = widget
        chit = eventbox.chit
        creature = chit.creature
        self.callback(self.legion, creature)
        self.pick_teleporting_lord_dialog.destroy()

    def cb_response(self, widget, response_id):
        """Player hit cancel"""
        self.callback(self.legion, None)
        self.pick_teleporting_lord_dialog.destroy()


if __name__ == "__main__":
    now = time.time()
    username = "test"
    game = Game.Game("g1", username, now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    creatures1 = [Creature.Creature(name) for name in
      ["Titan", "Archangel", "Angel", "Ogre", "Troll", "Ranger"]]
    legion = Legion.Legion(player, "Rd01", creatures1, 1)
    player.legions[legion.markername] = legion

    def my_callback(legion, creature):
        print "Picked", creature
        guiutils.exit()

    pick_teleporting_lord = PickTeleportingLord(username, legion, my_callback,
      None)
    pick_teleporting_lord.pick_teleporting_lord_dialog.connect("destroy",
      guiutils.exit)

    gtk.main()
