#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Optional, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import defer

from slugathon.game import Creature, Game, Legion, Player
from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


TELEPORT = 1
NORMAL_MOVE = 2


def new(
    playername: str,
    legion: Legion.Legion,
    hexlabel: int,
    parent: Optional[Gtk.Window],
) -> Tuple[PickMoveType, defer.Deferred]:
    """Create a PickMoveType dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pickmovetype = PickMoveType(playername, legion, hexlabel, def1, parent)
    return pickmovetype, def1


class PickMoveType(Gtk.Dialog):

    """Dialog to choose whether to teleport."""

    def __init__(
        self,
        playername: str,
        legion: Legion.Legion,
        hexlabel: int,
        def1: defer.Deferred,
        parent: Optional[Gtk.Window],
    ):
        GObject.GObject.__init__(
            self, title=f"PickMoveType - {playername}", parent=parent
        )
        self.deferred = def1
        self.legion = legion
        player = legion.player

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = Gtk.Label(
            label=f"Pick move type for legion {legion.markerid} "
            f"({legion.picname}) "
            f"in hex {legion.hexlabel} "
            f"moving to hex {hexlabel}"
        )
        self.vbox.pack_start(legion_name, True, True, 0)

        legion_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox, True, True, 0)

        marker_hbox = Gtk.HBox()
        legion_hbox.pack_start(marker_hbox, True, True, 0)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, False, True, 0)

        chits_hbox = Gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox, True, True, 0)

        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, False, True, 0)

        button_hbox = Gtk.HBox(homogeneous=True)
        self.vbox.pack_start(button_hbox, True, True, 0)

        self.add_button("Teleport", TELEPORT)
        self.add_button("Move normally", NORMAL_MOVE)
        self.add_button("gtk-cancel", Gtk.ResponseType.CANCEL)

        self.connect("response", self.cb_response)

        self.show_all()

    def cb_response(self, widget: Gtk.Widget, response_id: int) -> None:
        if response_id == TELEPORT:
            self.deferred.callback(True)
        elif response_id == NORMAL_MOVE:
            self.deferred.callback(False)
        else:
            self.deferred.callback(None)
        self.destroy()


if __name__ == "__main__":
    import time

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def mycallback(teleported: bool) -> None:
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

    Gtk.main()
