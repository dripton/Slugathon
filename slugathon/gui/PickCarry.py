#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import defer, reactor

from slugathon.game import Creature
from slugathon.gui import icon


__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    playername: str,
    game_name: str,
    striker: Creature.Creature,
    target: Creature.Creature,
    num_dice: int,
    strike_number: int,
    carries: int,
    parent: Gtk.Window,
) -> Tuple[PickCarry, defer.Deferred]:
    """Create a PickCarry dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pickcarry = PickCarry(
        playername,
        game_name,
        striker,
        target,
        num_dice,
        strike_number,
        carries,
        def1,
        parent,
    )
    return pickcarry, def1


class PickCarry(Gtk.Dialog):

    """Dialog to pick whether and where to carry excess hits."""

    def __init__(
        self,
        playername: str,
        game_name: str,
        striker: Creature.Creature,
        target: Creature.Creature,
        num_dice: int,
        strike_number: int,
        carries: int,
        def1: defer.Deferred,
        parent: Gtk.Window,
    ):
        GObject.GObject.__init__(
            self, title=f"PickCarry - {playername}", parent=parent
        )
        self.playername = playername
        self.game_name = game_name
        self.carries = carries
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        label = Gtk.Label(
            label=f"{repr(striker)} strikes "
            f"{repr(target)} "
            f"and may carry over {carries} "
            f"hit{'' if carries == 1 else 's'}"
            f"."
        )
        # We could use get_content_area() instead of vbox, in PyGTK 2.14+
        self.vbox.add(label)

        for ii, creature in enumerate(striker.engaged_enemies):
            if striker.can_carry_to(creature, target, num_dice, strike_number):
                button = self.add_button(repr(creature), ii)
                button.creature = creature
                button.connect("button-press-event", self.cb_click)
        button = self.add_button("Do not carry", ii + 1)
        button.creature = None
        button.connect("button-press-event", self.cb_click)

        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        creature = widget.creature
        self.destroy()
        if creature:
            self.deferred.callback((creature, self.carries))
        else:
            self.deferred.callback((None, 0))


def main() -> None:
    import time
    from slugathon.game import Game, Phase

    now = time.time()
    playername = "p0"
    game_name = "g1"
    game = Game.Game(game_name, playername, now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p1", "Blue")
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Centaur", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Ogre", "Gargoyle"],
    )
    rd01 = player0.markerid_to_legion["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion(
        "Bu01",
        "Bu02",
        ["Titan", "Centaur", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Ogre", "Gargoyle"],
    )
    bu01 = player1.markerid_to_legion["Bu01"]

    rd01.move(6, False, None, 3)
    bu01.move(6, False, None, 3)
    game._init_battle(bu01, rd01)
    defender = game.defender_legion
    if defender is None:
        return
    titan1 = defender.creatures[0]
    titan1.move("F2")
    ogre1 = defender.creatures[1]
    ogre1.move("E2")
    centaur1 = defender.creatures[2]
    centaur1.move("D2")
    gargoyle1 = defender.creatures[3]
    gargoyle1.move("C1")

    attacker = game.attacker_legion
    if attacker is None:
        return
    game.battle_active_legion = attacker
    titan2 = attacker.creatures[0]
    titan2.move("C2")
    ogre2 = attacker.creatures[1]
    ogre2.move("B3")
    centaur2 = attacker.creatures[2]
    centaur2.move("D3")
    gargoyle2 = attacker.creatures[3]
    gargoyle2.move("D4")
    game.battle_phase = Phase.STRIKE

    def my_callback(tup: Tuple[Creature.Creature, int]) -> None:
        (creature, carries) = tup
        logging.info(f"carry {carries} hits to {creature}")
        reactor.stop()  # type: ignore

    _, def1 = new(playername, game_name, titan2, centaur1, 6, 4, 1, None)
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
