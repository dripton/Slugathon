#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, List, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import defer, reactor

from slugathon.game import Legion
from slugathon.gui import Chit, Marker, icon
from slugathon.util.bag import bag


__copyright__ = "Copyright (c) 2006-2021 David Ripton"
__license__ = "GNU GPL v2"


ACCEPT = 0
REJECT = 1
FIGHT = 2


def new(
    playername: str,
    attacker_legion: Legion.Legion,
    attacker_creature_names: List[str],
    defender_legion: Legion.Legion,
    defender_creature_names: List[str],
    parent: Gtk.Window,
) -> Tuple[Proposal, defer.Deferred]:
    """Create a Proposal dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    proposal = Proposal(
        playername,
        attacker_legion,
        attacker_creature_names,
        defender_legion,
        defender_creature_names,
        def1,
        parent,
    )
    return proposal, def1


class Proposal(Gtk.Dialog):

    """Dialog to choose whether to accept an opponent's proposal."""

    def __init__(
        self,
        playername: str,
        attacker_legion: Legion.Legion,
        attacker_creature_names: List[str],
        defender_legion: Legion.Legion,
        defender_creature_names: List[str],
        def1: defer.Deferred,
        parent: Gtk.Window,
    ):
        GObject.GObject.__init__(
            self, title=f"Proposal - {playername}", parent=parent
        )
        self.attacker_legion = attacker_legion
        self.attacker_creature_names = attacker_creature_names
        self.defender_legion = defender_legion
        self.defender_creature_names = defender_creature_names
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = Gtk.Label(
            label=f"Legion {attacker_legion.markerid} "
            f"({attacker_legion.picname}) negotiates with "
            f"{defender_legion.markerid} ({defender_legion.picname}) "
            f"in hex {defender_legion.hexlabel}"
        )
        self.vbox.pack_start(legion_name, True, True, 0)

        attacker_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(attacker_hbox, True, True, 0)
        attacker_marker_hbox = Gtk.HBox()
        attacker_hbox.pack_start(attacker_marker_hbox, False, True, 0)
        attacker_chits_hbox = Gtk.HBox(spacing=3)
        attacker_hbox.pack_start(attacker_chits_hbox, True, True, 0)

        attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        attacker_marker_hbox.pack_start(
            attacker_marker.event_box, False, False, 0
        )

        defender_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(defender_hbox, True, True, 0)
        defender_marker_hbox = Gtk.HBox()
        defender_hbox.pack_start(defender_marker_hbox, False, True, 0)
        defender_chits_hbox = Gtk.HBox(spacing=3)
        defender_hbox.pack_start(defender_chits_hbox, True, True, 0)

        defender_marker = Marker.Marker(defender_legion, True, scale=20)
        defender_marker_hbox.pack_start(
            defender_marker.event_box, False, False, 0
        )

        attacker_chits = []

        surviving_attackers = bag(attacker_creature_names)  # type: bag[str]
        surviving_defenders = bag(defender_creature_names)  # type: bag[str]
        assert attacker_legion.player is not None
        assert attacker_legion.player.color is not None

        for creature in attacker_legion.sorted_creatures:
            name = creature.name
            if name in surviving_attackers:
                surviving_attackers.remove(name)
                dead = False
            else:
                dead = True
            chit = Chit.Chit(
                creature, attacker_legion.player.color, scale=20, dead=dead
            )
            attacker_chits_hbox.pack_start(chit.event_box, False, True, 0)
            attacker_chits.append(chit)

        defender_chits = []

        assert defender_legion.player is not None
        assert defender_legion.player.color is not None
        for creature in defender_legion.sorted_creatures:
            name = creature.name
            if name in surviving_defenders:
                surviving_defenders.remove(name)
                dead = False
            else:
                dead = True
            chit = Chit.Chit(
                creature, defender_legion.player.color, scale=20, dead=dead
            )
            defender_chits_hbox.pack_start(chit.event_box, False, True, 0)
            defender_chits.append(chit)

        self.add_button("Accept", ACCEPT)
        self.add_button("Reject", REJECT)
        self.add_button("Fight", FIGHT)
        self.connect("response", self.cb_response)

        self.show_all()

    def cb_response(self, widget: Gtk.Widget, response_id: int) -> None:
        """Fires the Deferred with the attacker, the defender, and
        the response_id."""
        self.destroy()
        self.deferred.callback(
            (
                self.attacker_legion,
                self.attacker_creature_names,
                self.defender_legion,
                self.defender_creature_names,
                response_id,
            )
        )


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Player, Game

    now = time.time()
    game_name = "Game1"
    attacker_playername = "Roar!"
    game = Game.Game("g1", attacker_playername, now, now, 2, 6)
    attacker_player = Player.Player(attacker_playername, game, 0)
    attacker_player.color = "Black"
    attacker_creature_names = [
        "Titan",
        "Colossus",
        "Serpent",
        "Hydra",
        "Archangel",
        "Angel",
        "Unicorn",
    ]
    attacker_survivor_names = [
        "Titan",
        "Colossus",
        "Serpent",
        "Hydra",
        "Archangel",
        "Angel",
    ]
    attacker_creatures = Creature.n2c(attacker_creature_names)
    attacker_legion = Legion.Legion(
        attacker_player, "Bk01", attacker_creatures, 1
    )

    defender_playername = "Eek!"
    defender_player = Player.Player(defender_playername, game, 0)
    defender_player.color = "Gold"
    defender_creature_names = ["Ogre", "Centaur", "Gargoyle"]
    defender_survivor_names: List[str] = []
    defender_creatures = Creature.n2c(defender_creature_names)
    defender_legion = Legion.Legion(
        defender_player, "Rd01", defender_creatures, 1
    )

    def my_callback(*args: Any) -> None:
        logging.info(f"my_callback {args}")
        reactor.stop()  # type: ignore

    _, def1 = new(
        defender_playername,
        attacker_legion,
        attacker_survivor_names,
        defender_legion,
        defender_survivor_names,
        None,
    )
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]
