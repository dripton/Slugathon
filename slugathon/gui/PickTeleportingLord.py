#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import defer

from slugathon.game import Creature, Game, Legion, Player
from slugathon.gui import Chit, Marker, icon


__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    playername: str, legion: Legion.Legion, parent: Optional[Gtk.Window]
) -> Tuple[PickTeleportingLord, defer.Deferred]:
    """Create a PickTeleportingLord dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pick_teleporting_lord = PickTeleportingLord(
        playername, legion, def1, parent
    )
    return pick_teleporting_lord, def1


class PickTeleportingLord(Gtk.Dialog):

    """Dialog to pick a lord to reveal for tower teleport."""

    def __init__(
        self,
        playername: str,
        legion: Legion.Legion,
        def1: defer.Deferred,
        parent: Optional[Gtk.Window],
    ):
        GObject.GObject.__init__(
            self, title=f"PickTeleportingLord - {playername}", parent=parent
        )
        self.legion = legion
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        top_label = Gtk.Label(label="Revealing a lord to tower teleport")
        self.vbox.pack_start(top_label, True, True, 0)

        bottom_label = Gtk.Label(
            label="Click on a lord (red outline) to reveal it."
        )
        self.vbox.pack_start(bottom_label, True, True, 0)

        hbox = Gtk.HBox(spacing=3)
        self.vbox.pack_start(hbox, True, True, 0)
        marker = Marker.Marker(legion, False, scale=20)
        hbox.pack_start(marker.event_box, False, True, 0)
        player = self.legion.player
        for creature in legion.sorted_creatures:
            chit = Chit.Chit(
                creature, player.color, scale=20, outlined=creature.is_lord
            )
            hbox.pack_start(chit.event_box, False, True, 0)
            if creature.is_lord:
                chit.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", Gtk.ResponseType.CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        eventbox = widget
        chit = eventbox.chit
        creature = chit.creature
        self.deferred.callback(creature.name)
        self.destroy()

    def cb_cancel(self, widget: Gtk.Widget, response_id: int) -> None:
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils

    now = time.time()
    playername = "test"
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    creatures1 = [
        Creature.Creature(name)
        for name in ["Titan", "Archangel", "Angel", "Ogre", "Troll", "Ranger"]
    ]
    legion = Legion.Legion(player, "Rd01", creatures1, 1)
    player.markerid_to_legion[legion.markerid] = legion

    def my_callback(creature_name: str) -> None:
        logging.info(f"Picked {creature_name}")
        guiutils.exit()

    pick_teleporting_lord, def1 = new(playername, legion, None)
    pick_teleporting_lord.connect("destroy", guiutils.exit)
    def1.addCallback(my_callback)

    Gtk.main()
