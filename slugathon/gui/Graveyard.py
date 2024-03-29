#!/usr/bin/env python3

import logging
import time
from typing import Any

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk

from slugathon.game import Creature, Game, Legion
from slugathon.gui import Chit, Marker


__copyright__ = "Copyright (c) 2012-2021 David Ripton"
__license__ = "GNU GPL v2"


class Graveyard(Gtk.EventBox):

    """Show a legion's dead creatures."""

    def __init__(self, legion: Legion.Legion):
        GObject.GObject.__init__(self)

        self.legion = legion

        hbox = Gtk.HBox(spacing=3)
        self.add(hbox)

        self.marker_hbox = Gtk.HBox(spacing=3)
        hbox.pack_start(self.marker_hbox, False, True, 0)
        self.marker = Marker.Marker(legion, True, scale=15)
        self.marker_hbox.pack_start(self.marker.event_box, False, True, 0)

        self.chits_hbox = Gtk.HBox(spacing=3)
        hbox.pack_start(self.chits_hbox, True, True, 0)
        gtkcolor = Gdk.color_parse("white")
        self.modify_bg(Gtk.StateType.NORMAL, gtkcolor)

        self.show_all()

    def update_gui(self) -> None:
        for chit in self.chits_hbox.get_children():
            self.chits_hbox.remove(chit)

        playercolor = self.legion.player.color
        for creature in self.legion.dead_creatures:
            chit = Chit.Chit(creature, playercolor, scale=15)
            self.chits_hbox.pack_start(chit.event_box, False, True, 0)

        self.show_all()


if __name__ == "__main__":
    import random
    from slugathon.data import creaturedata, playercolordata
    from slugathon.game import Player
    from slugathon.util import guiutils

    def cb_click(self, widget: Gtk.Widget, event: Any) -> None:  # type: ignore
        logging.debug(f"{event=}")
        if self.legion.living_creatures:
            random.choice(self.legion.living_creatures).kill()
            graveyard.update_gui()

    creatures = [
        Creature.Creature(name)
        for name in creaturedata.starting_creature_names
    ]

    playername = "test"
    now = time.time()
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 1)
    player.color = random.choice(playercolordata.colors)
    abbrev = player.color_abbrev
    index = random.randrange(1, 12 + 1)
    legion = Legion.Legion(player, f"{abbrev}{index:02d}", creatures, 1)
    graveyard = Graveyard(legion)
    graveyard.connect("destroy", guiutils.exit)
    graveyard.connect("button-press-event", cb_click, graveyard)

    window = Gtk.Window()
    window.add(graveyard)
    window.show_all()

    Gtk.main()
