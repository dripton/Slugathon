#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


class PickMoveType(gtk.Dialog):
    """Dialog to choose whether to teleport."""
    def __init__(self, username, legion, hexlabel, callback, parent):
        gtk.Dialog.__init__(self, "PickMoveType - %s" % username, parent)
        self.callback = callback
        self.legion = legion
        player = legion.player

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_has_separator(False)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label(
          "Pick move type for legion %s in hex %s moving to hex %s" % (
          legion.markername, legion.hexlabel, hexlabel))
        self.vbox.pack_start(legion_name)

        legion_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox)

        marker_hbox = gtk.HBox()
        legion_hbox.pack_start(marker_hbox)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, expand=False)

        chits_hbox = gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox)

        for creature in legion.sorted_creatures:
            if not creature.dead:
                chit = Chit.Chit(creature, player.color, scale=20)
                chits_hbox.pack_start(chit.event_box, expand=False)

        button_hbox = gtk.HBox(homogeneous=True)
        self.vbox.pack_start(button_hbox)

        self.teleport_button = gtk.Button("Teleport")
        self.teleport_button.connect("button-press-event", self.cb_click)
        button_hbox.pack_start(self.teleport_button)

        self.normal_move_button = gtk.Button("Move Normally")
        self.normal_move_button.connect("button-press-event", self.cb_click)
        button_hbox.pack_start(self.normal_move_button)

        self.cancel_button = gtk.Button("gtk-cancel")
        self.cancel_button.set_use_stock(True)
        self.cancel_button.connect("button-press-event", self.cb_click)
        button_hbox.pack_start(self.cancel_button)

        self.show_all()


    def cb_click(self, widget, event):
        if widget is self.teleport_button:
            self.callback(True)
        elif widget is self.normal_move_button:
            self.callback(False)
        else:
            assert widget is self.cancel_button
            self.callback(None)
        self.destroy()


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
    pickmovetype.connect("destroy", guiutils.exit)

    gtk.main()
