#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


class PickTeleportingLord(gtk.Dialog):
    """Dialog to pick a lord to reveal for tower teleport."""
    def __init__(self, username, legion, callback, parent):
        gtk.Dialog.__init__(self, "PickTeleportingLord - %s" % username,
          parent)
        self.legion = legion
        self.callback = callback

        self.widget_names = ["top_label",
          "bottom_label", "vbox1"]

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_has_separator(False)
        self.vbox.set_spacing(9)

        top_label = gtk.Label("Revealing a lord to tower teleport")
        self.vbox.pack_start(top_label)

        bottom_label = gtk.Label("Click on a lord (red outline) to reveal it.")
        self.vbox.pack_start(bottom_label)

        hbox = gtk.HBox(spacing=3)
        self.vbox.pack_start(hbox)
        marker = Marker.Marker(legion, False, scale=20)
        hbox.pack_start(marker.event_box, expand=False)
        player = self.legion.player
        for creature in legion.sorted_creatures:
            chit = Chit.Chit(creature, player.color, scale=20,
              outlined=creature.is_lord)
            hbox.pack_start(chit.event_box, expand=False)
            if creature.is_lord:
                chit.connect("button-press-event", self.cb_click)

        self.cancel_button = gtk.Button("gtk-cancel")
        self.vbox.pack_start(self.cancel_button)
        self.cancel_button.connect("button-press-event", self.cb_click)
        self.cancel_button.set_use_stock(True)

        self.show_all()


    def cb_click(self, widget, event):
        if widget is not self.cancel_button:
            eventbox = widget
            chit = eventbox.chit
            creature = chit.creature
            self.callback(creature)
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game

    now = time.time()
    username = "test"
    game = Game.Game("g1", username, now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    creatures1 = [Creature.Creature(name) for name in
      ["Titan", "Archangel", "Angel", "Ogre", "Troll", "Ranger"]]
    legion = Legion.Legion(player, "Rd01", creatures1, 1)
    player.legions[legion.markername] = legion

    def my_callback(creature):
        print "Picked", creature
        guiutils.exit()

    pick_teleporting_lord = PickTeleportingLord(username, legion, my_callback,
      None)
    pick_teleporting_lord.connect("destroy",
      guiutils.exit)

    gtk.main()
