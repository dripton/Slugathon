#!/usr/bin/env python3

from typing import List

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
from zope.interface import implementer

from slugathon.util.Observer import IObserver
from slugathon.util.Observed import IObserved
from slugathon.gui import Chit
from slugathon.game import Creature, Action, Game, Player
from slugathon.data import creaturedata


__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class GUICaretaker(Gtk.EventBox):

    """Caretaker status window."""

    def __init__(self, game: Game.Game, playername: str):
        self.playername = playername
        self.caretaker = game.caretaker

        GObject.GObject.__init__(self)

        self.vbox = Gtk.VBox()
        self.add(self.vbox)

        table = Gtk.Table(rows=4, columns=6)
        table.set_row_spacings(9)
        table.set_col_spacings(9)
        self.vbox.pack_start(table, False, True, 0)

        self.max_count_labels = {}
        self.counts_labels = {}
        self.chits = {}

        for ii, (creature_name, left_count) in enumerate(
            sorted(self.caretaker.counts.items())
        ):
            creature = Creature.Creature(creature_name)
            max_count = self.caretaker.max_counts[creature_name]
            dead_count = self.caretaker.graveyard[creature_name]
            game_count = max_count - left_count - dead_count
            vbox = Gtk.VBox()
            col = (ii % 6) + 1
            row = (ii // 6) + 1
            table.attach(vbox, col, col + 1, row, row + 1)
            label = self.max_count_labels[creature_name] = Gtk.Label()
            vbox.pack_start(label, False, True, 0)
            chit = self.chits[creature_name] = Chit.Chit(
                creature, "Black", scale=15, dead=(not left_count)
            )
            vbox.pack_start(chit.event_box, False, True, 0)
            label = self.counts_labels[creature_name] = Gtk.Label()
            vbox.pack_start(label, False, True, 0)
            self.update_max_count_label(creature_name, max_count)
            self.update_counts_label(
                creature_name, left_count, game_count, dead_count
            )

        self.show_all()

    def update_max_count_label(
        self, creature_name: str, max_count: int
    ) -> None:
        label = self.max_count_labels[creature_name]
        label.set_markup(f"<span foreground='blue'>{max_count}</span>")

    def update_counts_label(
        self,
        creature_name: str,
        left_count: int,
        game_count: int,
        dead_count: int,
    ) -> None:
        label = self.counts_labels[creature_name]
        label.set_markup(
            f"<span foreground='black'>{left_count}</span>"
            f"/<span foreground='darkgreen'>{game_count}</span>"
            f"/<span foreground='red'>{dead_count}</span>"
        )
        if left_count == 0 and creature_name != "Titan":
            chit = self.chits[creature_name]
            chit.dead = True
            chit.build_image()
        elif left_count != 0:
            chit = self.chits[creature_name]
            if chit.dead:
                chit.dead = False
                chit.build_image()

    def update_creature(self, creature_name: str) -> None:
        left_count = self.caretaker.counts[creature_name]
        max_count = self.caretaker.max_counts[creature_name]
        dead_count = self.caretaker.graveyard[creature_name]
        game_count = max_count - left_count - dead_count
        self.update_counts_label(
            creature_name, left_count, game_count, dead_count
        )

    def update(
        self, observed: IObserved, action: Action.Action, names: List[str]
    ) -> None:
        if isinstance(action, Action.CreateStartingLegion):
            for creature_name in set(creaturedata.starting_creature_names):
                self.update_creature(creature_name)

        elif (
            isinstance(action, Action.RecruitCreature)
            or isinstance(action, Action.UndoRecruit)
            or isinstance(action, Action.UnReinforce)
        ):
            creature_name = action.creature_name
            self.update_creature(creature_name)

        elif isinstance(
            action,
            Action.Flee
            or isinstance(action, Action.Concede)
            or isinstance(action, Action.AcceptProposal)
            or isinstance(action, Action.BattleOver),
        ):
            for creature_name in self.caretaker.counts:
                self.update_creature(creature_name)

        elif isinstance(
            action,
            Action.DriftDamage
            or isinstance(action, Action.Strike)
            or isinstance(action, Action.Carry),
        ):
            creature_name = action.target_name
            self.update_creature(creature_name)

        elif isinstance(action, Action.AcquireAngels):
            for creature_name in action.angel_names:
                self.update_creature(creature_name)


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils

    now = time.time()
    playername = "Player 1"
    game = Game.Game("g1", playername, now, now, 2, 6)

    player1 = game.players[0]
    player1.assign_starting_tower(600)
    player1.assign_color("Red")
    player1.pick_marker("Rd01")
    player1.create_starting_legion()
    game.active_player = player1

    player2 = Player.Player("Player 2", game, 1)
    player2.assign_starting_tower(500)
    player2.assign_color("Blue")
    player2.pick_marker("Bu02")
    player2.create_starting_legion()
    game.players.append(player2)

    caretaker = game.caretaker
    for unused in range(10):
        caretaker.take_one("Colossus")

    window = Gtk.Window()
    guicaretaker = GUICaretaker(game, playername)
    guicaretaker.connect("destroy", guiutils.exit)
    window.add(guicaretaker)
    window.show_all()
    Gtk.main()
