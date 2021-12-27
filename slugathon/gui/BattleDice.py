#!/usr/bin/env python3

from typing import List, Optional, Tuple

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from zope.interface import implementer

from slugathon.game import Action, Creature
from slugathon.gui import Chit, Die
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class BattleDice(Gtk.EventBox):

    """Widget to show die rolls in battle."""

    def __init__(self, scale: int):
        GObject.GObject.__init__(self)
        self.scale = scale
        self.n_rows = 2
        self.n_columns = 9
        self.spacing = int(round(0.1 * self.scale))
        self.set_size_request(
            self.n_columns * self.scale + (self.n_columns - 1) * self.spacing,
            self.n_rows * self.scale + (self.n_rows - 1) * self.spacing,
        )

        self.table = Gtk.Table(n_rows=self.n_rows, n_columns=self.n_columns)
        self.add(self.table)
        gtkcolor = Gdk.color_parse("white")
        self.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
        self.table.modify_bg(Gtk.StateType.NORMAL, gtkcolor)

        self.show_all()

    def row_and_column(self, ii: int) -> Tuple[int, int]:
        """Return the row and column for ii."""
        row = ii // self.n_columns
        column = ii % self.n_columns
        return (row, column)

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        if isinstance(action, Action.Strike):
            rolls = sorted(action.rolls, reverse=True)
            changed = False
            while len(rolls) > self.n_rows * self.n_columns:
                self.n_columns += 1
                changed = True
            if changed:
                self.table.resize(self.n_rows, self.n_columns)
                self.set_size_request(
                    self.n_columns * self.scale
                    + (self.n_columns - 1) * self.spacing,
                    self.n_rows * self.scale
                    + (self.n_rows - 1) * self.spacing,
                )
            hits = action.hits
            chit_scale = int(round(self.scale / Die.CHIT_SCALE_FACTOR))
            gtkcolor = Gdk.color_parse("white")
            for ii, roll in enumerate(rolls):
                die = Die.Die(roll, ii < hits, scale=chit_scale)
                die.event_box.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
                row, col = self.row_and_column(ii)
                self.table.attach(die.event_box, col, col + 1, row, row + 1)
            ii += 1
            while ii < self.n_rows * self.n_columns:
                row, col = self.row_and_column(ii)
                chit = Chit.Chit(None, None, scale=chit_scale, name="Nothing")
                die.event_box.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
                self.table.attach(chit.event_box, col, col + 1, row, row + 1)
                ii += 1
            self.show_all()


if __name__ == "__main__":
    from slugathon.util import guiutils, Dice

    window = Gtk.Window()
    battle_dice = BattleDice(80)
    battle_dice.connect("destroy", guiutils.exit)
    window.add(battle_dice)
    window.show_all()
    rolls = Dice.roll(numrolls=12)
    action = Action.Strike(
        "",
        "",
        "",
        "",
        "",
        "",
        3,
        3,
        rolls,
        sum(1 for roll in rolls if roll >= 4),
        1,
    )
    battle_dice.update(None, action, None)
    Gtk.main()
