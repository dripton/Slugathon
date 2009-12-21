#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from zope.interface import implements

from slugathon.util.Observer import IObserver
from slugathon.gui import Chit
from slugathon.game import Creature, Action
from slugathon.data import creaturedata


class GUICaretaker(gtk.Window):
    """Caretaker status window."""

    implements(IObserver)

    def __init__(self, game, username):
        self.caretaker = game.caretaker

        gtk.Window.__init__(self)
        vbox1 = gtk.VBox()
        self.add(vbox1)
        table = gtk.Table(rows=4, columns=6)
        table.set_row_spacings(9)
        table.set_col_spacings(9)
        vbox1.pack_start(table, expand=False)

        self.max_count_labels = {}
        self.counts_labels = {}

        for ii, (creature_name, left_count) in enumerate(sorted(
          self.caretaker.counts.iteritems())):
            creature = Creature.Creature(creature_name)
            max_count = self.caretaker.max_counts[creature_name]
            dead_count = self.caretaker.graveyard[creature_name]
            game_count = max_count - left_count - dead_count
            vbox = gtk.VBox()
            col = (ii % 6) + 1
            row = (ii // 6) + 1
            table.attach(vbox, col, col + 1, row, row + 1)
            label = self.max_count_labels[creature_name] = gtk.Label()
            vbox.pack_start(label, expand=False)
            chit = Chit.Chit(creature, "Black", scale=20)
            vbox.pack_start(chit.event_box, expand=False)
            label = self.counts_labels[creature_name] = gtk.Label()
            vbox.pack_start(label, expand=False)
            self.update_max_count_label(creature_name, max_count)
            self.update_counts_label(creature_name, left_count, game_count,
              dead_count)

        self.set_title("Caretaker - %s" % username)
        self.show_all()

    def update_max_count_label(self, creature_name, max_count):
        label = self.max_count_labels[creature_name]
        label.set_markup("<span foreground='blue'>%d</span>" % max_count)

    def update_counts_label(self, creature_name, left_count, game_count,
      dead_count):
        label = self.counts_labels[creature_name]
        label.set_markup("<span foreground='black'>%d</span>" % left_count +
          "/<span foreground='green'>%d</span>" % game_count +
          "/<span foreground='red'>%d</span>" % dead_count)

    def update_creature(self, creature_name):
        left_count = self.caretaker.counts[creature_name]
        max_count = self.caretaker.max_counts[creature_name]
        dead_count = self.caretaker.graveyard[creature_name]
        game_count = max_count - left_count - dead_count
        self.update_counts_label(creature_name, left_count, game_count,
          dead_count)

    def update(self, observed, action):
        if isinstance(action, Action.CreateStartingLegion):
            for creature_name in set(creaturedata.starting_creature_names):
                self.update_creature(creature_name)

        elif isinstance(action, Action.RecruitCreature or
          isinstance(action, Action.UndoRecruit)):
            creature_name = action.creature_name
            self.update_creature(creature_name)

        # TODO Flee and Concede should reveal loser's creatures
        elif isinstance(action, Action.Flee or
          isinstance(action, Action.Concede) or
          isinstance(action, Action.AcceptProposal) or
          isinstance(action, Action.RemoveLegion) or
          isinstance(action, Action.BattleOver)):
            for creature_name in self.caretaker.counts:
                self.update_creature(creature_name)

        elif isinstance(action, Action.DriftDamage or
          isinstance(action, Action.Strike) or
          isinstance(action, Action.Carry)):
            creature_name = action.target_name
            self.update_creature(creature_name)

        elif isinstance(action, Action.AcquireAngel):
            creature_name = action.angel_name
            self.update_creature(creature_name)


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils
    from slugathon.game import Game, Player

    now = time.time()
    username = "Player 1"
    game = Game.Game("g1", username, now, now, 2, 6)

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

    guicaretaker = GUICaretaker(game, username)
    guicaretaker.connect("destroy", guiutils.exit)
    gtk.main()
