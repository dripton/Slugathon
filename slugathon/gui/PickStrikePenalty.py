#!/usr/bin/env python3


import logging

import gi

gi.require_version("Gtk", "3.0")
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor, defer
from gi.repository import Gtk, GObject

from slugathon.gui import icon
from slugathon.game import Phase


__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(playername, game_name, striker, target, parent):
    """Create a PickStrikePenalty dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    pick_strike_penalty = PickStrikePenalty(
        playername, game_name, striker, target, def1, parent
    )
    return pick_strike_penalty, def1


class PickStrikePenalty(Gtk.Dialog):

    """Dialog to pick whether to take a strike penalty to allow carrying
    excess hits."""

    def __init__(self, playername, game_name, striker, target, def1, parent):
        GObject.GObject.__init__(
            self, title=f"PickStrikePenalty - {playername}", parent=parent
        )
        self.playername = playername
        self.game_name = game_name
        self.striker = striker
        self.target = target
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        self.vbox.set_spacing(9)

        label = Gtk.Label(
            name=f"Choose strike penalty for {repr(striker)} "
            f"striking {repr(target)}"
        )
        self.vbox.add(label)

        # Map tuple of (num_dice, strike_number) to set of creatures it can hit
        dice_strike_to_creatures = {}
        for tup in striker.valid_strike_penalties(target):
            num_dice, strike_number = tup
            dice_strike_to_creatures[tup] = set()
            for creature in striker.engaged_enemies:
                if creature is not target:
                    if striker.can_carry_to(
                        creature, target, num_dice, strike_number
                    ):
                        dice_strike_to_creatures[tup].add(creature)

        for ii, (tup, creatures) in enumerate(
            sorted(dice_strike_to_creatures.items())
        ):
            (num_dice3, strike_number3) = tup
            if creatures:
                st = (
                    f"{num_dice3} dice at strike number {strike_number3}, "
                    f"able to carry to "
                    f"{', '.join(sorted(repr(cr) for cr in creatures))}"
                )
            else:
                st = (
                    f"{num_dice3} dice at strike number {strike_number3}, "
                    f"unable to carry"
                )
            button = Gtk.Button(label=st)
            self.vbox.pack_start(button, True, True, 0)
            button.tup = tup
            button.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", Gtk.ResponseType.CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()

    def cb_click(self, widget, event):
        self.destroy()
        num_dice, strike_number = widget.tup
        self.deferred.callback(
            (self.striker, self.target, num_dice, strike_number)
        )

    def cb_cancel(self, widget, response_id):
        self.destroy()
        self.deferred.callback((None, None, None, None))


def main():
    import time
    from slugathon.game import Game

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

    def my_callback(tup):
        (striker, target, num_dice, strike_number) = tup
        logging.info(
            f"called my_callback {striker} {target} {num_dice} "
            f"{strike_number}"
        )
        reactor.stop()

    pick_strike_penalty, def1 = new(
        playername, game_name, titan2, gargoyle1, None
    )
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
