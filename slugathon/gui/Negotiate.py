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


__copyright__ = "Copyright (c) 2006-2021 David Ripton"
__license__ = "GNU GPL v2"


CONCEDE = 0
MAKE_PROPOSAL = 1
DONE_PROPOSING = 2
FIGHT = 3


def new(
    playername: str,
    attacker_legion: Legion.Legion,
    defender_legion: Legion.Legion,
    parent: Gtk.Window,
) -> Tuple[Negotiate, defer.Deferred]:
    """Create a Negotiate dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    negotiate = Negotiate(
        playername, attacker_legion, defender_legion, def1, parent
    )
    return negotiate, def1


class Negotiate(Gtk.Dialog):

    """Dialog to choose whether to concede, negotiate, or fight."""

    def __init__(
        self,
        playername: str,
        attacker_legion: Legion.Legion,
        defender_legion: Legion.Legion,
        def1: defer.Deferred,
        parent: Gtk.Window,
    ):
        GObject.GObject.__init__(
            self, title=f"Negotiate - {playername}", parent=parent
        )
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = Gtk.Label(
            label=f"Legion {attacker_legion.markerid} "
            f"({attacker_legion.picname}) negotiates with "
            f"{defender_legion.markerid} "
            f"({defender_legion.picname}) "
            f"in hex {defender_legion.hexlabel}"
        )
        self.vbox.pack_start(legion_name, True, True, 0)

        attacker_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(attacker_hbox, True, True, 0)
        attacker_marker_hbox = Gtk.HBox()
        attacker_hbox.pack_start(attacker_marker_hbox, False, True, 0)
        attacker_score_label = Gtk.Label(
            label=f"{attacker_legion.score}\n points"
        )
        attacker_hbox.pack_start(attacker_score_label, False, True, 0)
        attacker_chits_hbox = Gtk.HBox(spacing=3)
        attacker_hbox.pack_start(attacker_chits_hbox, True, True, 0)

        defender_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(defender_hbox, True, True, 0)
        defender_marker_hbox = Gtk.HBox()
        defender_hbox.pack_start(defender_marker_hbox, False, True, 0)
        defender_chits_hbox = Gtk.HBox(spacing=3)
        defender_score_label = Gtk.Label(
            label=f"{defender_legion.score}\n points"
        )
        defender_hbox.pack_start(defender_score_label, False, True, 0)
        defender_hbox.pack_start(defender_chits_hbox, True, True, 0)

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        attacker_marker_hbox.pack_start(
            self.attacker_marker.event_box, False, False, 0
        )
        self.attacker_marker.connect("button-press-event", self.cb_click)

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        defender_marker_hbox.pack_start(
            self.defender_marker.event_box, False, False, 0
        )
        self.defender_marker.connect("button-press-event", self.cb_click)

        self.attacker_chits = []

        for creature in attacker_legion.sorted_creatures:
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20)
            attacker_chits_hbox.pack_start(chit.event_box, False, True, 0)
            chit.connect("button-press-event", self.cb_click)
            self.attacker_chits.append(chit)

        self.defender_chits = []

        for creature in defender_legion.sorted_creatures:
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20)
            defender_chits_hbox.pack_start(chit.event_box, False, True, 0)
            chit.connect("button-press-event", self.cb_click)
            self.defender_chits.append(chit)

        self.add_button("Concede", CONCEDE)
        self.proposal_button = self.add_button("Make proposal", MAKE_PROPOSAL)
        self.add_button("No more proposals", DONE_PROPOSING)
        self.add_button("Fight", FIGHT)
        self.connect("response", self.cb_response)

        self.proposal_button.set_sensitive(False)

        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Any) -> None:
        """Toggle the clicked-on chit's creature's status."""
        logging.debug(f"{event=}")
        event_box = widget
        if hasattr(event_box, "chit"):
            chit = event_box.chit
            chit.dead = not chit.dead
            # XXX What's the right way to force a repaint?
            chit.build_image()
        else:
            marker = event_box.marker
            if marker == self.attacker_marker:
                chits = self.attacker_chits
            else:
                chits = self.defender_chits
            num_alive = 0
            num_dead = 0
            for chit in chits:
                if chit.dead:
                    num_dead += 1
                else:
                    num_alive += 1
            dead = num_alive >= num_dead
            for chit in chits:
                chit.dead = dead
                chit.build_image()
        legal = self.is_legal_proposal()
        self.proposal_button.set_sensitive(legal)

    def all_dead(self, li: List[Chit.Chit]) -> bool:
        """Return True if all elements in the list are dead."""
        for chit in li:
            if not chit.dead:
                return False
        return True

    def is_legal_proposal(self) -> bool:
        """Return True iff at least one of the two legions is completely
        dead."""
        return self.all_dead(self.attacker_chits) or self.all_dead(
            self.defender_chits
        )

    def surviving_creature_names(self, chits: List[Chit.Chit]) -> List[str]:
        """Return a list of creature names for the survivors."""
        return [
            chit.creature.name
            for chit in chits
            if not chit.dead and chit.creature is not None
        ]

    def cb_response(self, widget: Gtk.Widget, response_id: int) -> None:
        """Fire the Deferred, with the attacker, the defender, and
        the response_id."""
        self.destroy()
        attacker_creature_names = self.surviving_creature_names(
            self.attacker_chits
        )
        defender_creature_names = self.surviving_creature_names(
            self.defender_chits
        )
        self.deferred.callback(
            (
                self.attacker_legion,
                attacker_creature_names,
                self.defender_legion,
                defender_creature_names,
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
    attacker_creatures = Creature.n2c(attacker_creature_names)
    attacker_legion = Legion.Legion(
        attacker_player, "Bk01", attacker_creatures, 1
    )

    defender_playername = "Eek!"
    defender_player = Player.Player(defender_playername, game, 0)
    defender_player.color = "Gold"
    defender_creature_names = ["Ogre", "Centaur", "Gargoyle"]
    defender_creatures = Creature.n2c(defender_creature_names)
    defender_legion = Legion.Legion(
        defender_player, "Rd01", defender_creatures, 1
    )

    def my_callback(*args: Any) -> None:
        logging.info(f"callback {args}")
        reactor.stop()  # type: ignore

    _, def1 = new(defender_playername, attacker_legion, defender_legion, None)
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]
