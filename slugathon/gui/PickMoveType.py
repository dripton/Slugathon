#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


NORMAL_MOVE = 0
TELEPORT = 1


class PickMoveType(object):
    """Dialog to choose whether to teleport."""
    def __init__(self, username, legion, hexlabel, callback, parent):
        self.callback = callback
        self.builder = gtk.Builder()
        self.builder.add_from_file(guiutils.basedir("ui/pickmovetype.ui"))
        self.widget_names = ["pick_move_type_dialog", "marker_hbox",
          "chits_hbox", "legion_name", "teleport_button", "normal_move_button",
          "cancel_button"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.pick_move_type_dialog.set_icon(icon.pixbuf)
        self.pick_move_type_dialog.set_title("PickMoveType - %s" % (username))
        self.pick_move_type_dialog.set_transient_for(parent)

        self.legion_name.set_text(
          "Pick move type for legion %s in hex %s moving to hex %s" % (
          legion.markername, legion.hexlabel, hexlabel))

        self.legion = legion
        player = legion.player

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False,
          fill=False)
        self.marker.show()

        for creature in legion.sorted_creatures:
            if not creature.dead:
                chit = Chit.Chit(creature, player.color, scale=20)
                chit.show()
                self.chits_hbox.pack_start(chit.event_box, expand=False,
                  fill=False)

        self.pick_move_type_dialog.connect("response", self.cb_response)
        self.pick_move_type_dialog.show()


    def cb_response(self, dialog, response_id):
        if response_id == TELEPORT:
            self.callback(True)
        elif response_id == NORMAL_MOVE:
            self.callback(False)
        else:
            assert response_id == gtk.RESPONSE_CANCEL
            self.callback(None)
        self.pick_move_type_dialog.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def mycallback(teleported):
        if teleported is None:
            print "canceled"
        elif teleported:
            print "teleport"
        else:
            print "normal move"
        guiutils.exit()

    now = time.time()
    username = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 100
    hexlabel = 101
    masterhex = game.board.hexes[legion.hexlabel]
    mterrain = masterhex.terrain
    pickmovetype = PickMoveType(username, legion, hexlabel, mycallback, None)
    pickmovetype.pick_move_type_dialog.connect("destroy", guiutils.exit)

    gtk.main()
