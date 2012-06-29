#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

import gtk
from twisted.internet import defer

from slugathon.gui import Chit, Marker, icon


def new(playername, legion, parent):
    """Create a PickTeleportingLord dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    pick_teleporting_lord = PickTeleportingLord(playername, legion, def1,
      parent)
    return pick_teleporting_lord, def1


class PickTeleportingLord(gtk.Dialog):
    """Dialog to pick a lord to reveal for tower teleport."""
    def __init__(self, playername, legion, def1, parent):
        gtk.Dialog.__init__(self, "PickTeleportingLord - %s" % playername,
          parent)
        self.legion = legion
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
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

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()

    def cb_click(self, widget, event):
        eventbox = widget
        chit = eventbox.chit
        creature = chit.creature
        self.deferred.callback(creature.name)
        self.destroy()

    def cb_cancel(self, widget, response_id):
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game
    from slugathon.util import guiutils

    now = time.time()
    playername = "test"
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    creatures1 = [Creature.Creature(name) for name in
      ["Titan", "Archangel", "Angel", "Ogre", "Troll", "Ranger"]]
    legion = Legion.Legion(player, "Rd01", creatures1, 1)
    player.markerid_to_legion[legion.markerid] = legion

    def my_callback(creature_name):
        logging.info("Picked %s", creature_name)
        guiutils.exit()

    pick_teleporting_lord, def1 = new(playername, legion, None)
    pick_teleporting_lord.connect("destroy", guiutils.exit)
    def1.addCallback(my_callback)

    gtk.main()
