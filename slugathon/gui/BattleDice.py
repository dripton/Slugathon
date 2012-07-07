#!/usr/bin/env python

__copyright__ = "Copyright (c) 2010-2011 David Ripton"
__license__ = "GNU GPL v2"

import gtk
from zope.interface import implementer

from slugathon.gui import Die, Chit
from slugathon.util.Observer import IObserver
from slugathon.game import Action


@implementer(IObserver)
class BattleDice(gtk.EventBox):
    """Widget to show die rolls in battle."""
    def __init__(self, scale):
        gtk.EventBox.__init__(self)
        self.scale = scale
        self.rows = 2
        self.columns = 9
        self.spacing = int(round(0.1 * self.scale))
        self.set_size_request(
          self.columns * self.scale + (self.columns - 1) * self.spacing,
          self.rows * self.scale + (self.rows - 1) * self.spacing)

        self.table = gtk.Table(rows=self.rows, columns=self.columns)
        self.table.set_row_spacings(self.spacing)
        self.table.set_col_spacings(self.spacing)
        self.table.set_homogeneous(True)
        self.add(self.table)
        gtkcolor = gtk.gdk.color_parse("white")
        self.modify_bg(gtk.STATE_NORMAL, gtkcolor)
        self.table.modify_bg(gtk.STATE_NORMAL, gtkcolor)
        self.show_all()

    def row_and_column(self, ii):
        """Return the row and column for ii."""
        row = ii // self.columns
        column = ii % self.columns
        return (row, column)

    def update(self, observed, action, names):
        if isinstance(action, Action.Strike):
            rolls = sorted(action.rolls, reverse=True)
            changed = False
            while len(rolls) > self.rows * self.columns:
                self.columns += 1
                changed = True
            if changed:
                self.table.resize(self.rows, self.columns)
                self.set_size_request(
                  self.columns * self.scale +
                    (self.columns - 1) * self.spacing,
                  self.rows * self.scale + (self.rows - 1) * self.spacing)
            hits = action.hits
            gtkcolor = gtk.gdk.color_parse("white")
            chit_scale = int(round(self.scale / Die.CHIT_SCALE_FACTOR))
            for ii, roll in enumerate(rolls):
                die = Die.Die(roll, ii < hits, scale=chit_scale)
                die.event_box.modify_bg(gtk.STATE_NORMAL, gtkcolor)
                row, col = self.row_and_column(ii)
                self.table.attach(die.event_box, col, col + 1, row, row + 1)
            ii += 1
            while ii < self.rows * self.columns:
                row, col = self.row_and_column(ii)
                chit = Chit.Chit(None, None, scale=chit_scale, name="Nothing")
                chit.event_box.modify_bg(gtk.STATE_NORMAL, gtkcolor)
                self.table.attach(chit.event_box, col, col + 1, row, row + 1)
                ii += 1
            self.show_all()


if __name__ == "__main__":
    from slugathon.util import guiutils, Dice

    window = gtk.Window()
    battle_dice = BattleDice(80)
    battle_dice.connect("destroy", guiutils.exit)
    window.add(battle_dice)
    window.show_all()
    rolls = Dice.roll(numrolls=12)
    action = Action.Strike(None, None, None, None, None, None, None, None,
      rolls, sum(1 for roll in rolls if roll >= 4), 1)
    battle_dice.update(None, action, None)
    gtk.main()
