#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

import gtk
from twisted.internet import defer

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


TELEPORT = 1
NORMAL_MOVE = 2


def new(playername, legion, hexlabel, parent):
    """Create a PickMoveType dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    pickmovetype = PickMoveType(playername, legion, hexlabel, def1, parent)
    return pickmovetype, def1


class PickMoveType(gtk.Dialog):
    """Dialog to choose whether to teleport."""
    def __init__(self, playername, legion, hexlabel, def1, parent):
        gtk.Dialog.__init__(self, "PickMoveType - %s" % playername, parent)
        self.deferred = def1
        self.legion = legion
        player = legion.player

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label(
          "Pick move type for legion %s (%s) in hex %s moving to hex %s" % (
          legion.markerid, legion.picname, legion.hexlabel, hexlabel))
        self.vbox.pack_start(legion_name)

        legion_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox)

        marker_hbox = gtk.HBox()
        legion_hbox.pack_start(marker_hbox)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, expand=False)

        chits_hbox = gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox)

        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, expand=False)

        button_hbox = gtk.HBox(homogeneous=True)
        self.vbox.pack_start(button_hbox)

        self.add_button("Teleport", TELEPORT)
        self.add_button("Move normally", NORMAL_MOVE)
        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)

        self.connect("response", self.cb_response)

        self.show_all()

    def cb_response(self, widget, response_id):
        if response_id == TELEPORT:
            self.deferred.callback(True)
        elif response_id == NORMAL_MOVE:
            self.deferred.callback(False)
        else:
            self.deferred.callback(None)
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def mycallback(teleported):
        if teleported is None:
            logging.info("canceled")
        elif teleported:
            logging.info("teleport")
        else:
            logging.info("normal move")
        guiutils.exit()

    now = time.time()
    playername = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 100
    hexlabel = 101
    masterhex = game.board.hexes[legion.hexlabel]
    mterrain = masterhex.terrain
    pickmovetype, def1 = new(playername, legion, hexlabel, None)
    pickmovetype.connect("destroy", guiutils.exit)
    def1.addCallback(mycallback)

    gtk.main()
