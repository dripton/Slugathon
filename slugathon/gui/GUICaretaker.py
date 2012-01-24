#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009-2012 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from zope.interface import implementer

from slugathon.util.Observer import IObserver
from slugathon.gui import Chit, icon
from slugathon.game import Creature, Action
from slugathon.data import creaturedata
from slugathon.util import prefs


@implementer(IObserver)
class GUICaretaker(gtk.Dialog):
    """Caretaker status window."""
    def __init__(self, game, username, parent):
        self.username = username
        self.caretaker = game.caretaker

        gtk.Dialog.__init__(self, "Caretaker - %s" % username, parent)
        table = gtk.Table(rows=4, columns=6)
        table.set_row_spacings(9)
        table.set_col_spacings(9)
        self.vbox.pack_start(table, expand=False)

        self.max_count_labels = {}
        self.counts_labels = {}
        self.chits = {}

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
            chit = self.chits[creature_name] = Chit.Chit(creature, "Black",
              scale=20, dead=(not left_count))
            vbox.pack_start(chit.event_box, expand=False)
            label = self.counts_labels[creature_name] = gtk.Label()
            vbox.pack_start(label, expand=False)
            self.update_max_count_label(creature_name, max_count)
            self.update_counts_label(creature_name, left_count, game_count,
              dead_count)

        if self.username:
            tup = prefs.load_window_position(self.username,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(self.username,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.resize(width, height)

        self.connect("configure-event", self.cb_configure_event)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Caretaker - %s" % username)
        self.show_all()

    def cb_configure_event(self, event, unused):
        if self.username:
            x, y = self.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.username, self.__class__.__name__,
              width, height)
        return False

    def update_max_count_label(self, creature_name, max_count):
        label = self.max_count_labels[creature_name]
        label.set_markup("<span foreground='blue'>%d</span>" % max_count)

    def update_counts_label(self, creature_name, left_count, game_count,
      dead_count):
        label = self.counts_labels[creature_name]
        label.set_markup("<span foreground='black'>%d</span>" % left_count +
          "/<span foreground='darkgreen'>%d</span>" % game_count +
          "/<span foreground='red'>%d</span>" % dead_count)
        if left_count == 0 and creature_name != "Titan":
            chit = self.chits[creature_name]
            chit.dead = True
            chit.build_image()
        elif left_count != 0:
            chit = self.chits[creature_name]
            if chit.dead:
                chit.dead = False
                chit.build_image()

    def update_creature(self, creature_name):
        left_count = self.caretaker.counts[creature_name]
        max_count = self.caretaker.max_counts[creature_name]
        dead_count = self.caretaker.graveyard[creature_name]
        game_count = max_count - left_count - dead_count
        self.update_counts_label(creature_name, left_count, game_count,
          dead_count)

    def update(self, observed, action, names):
        if isinstance(action, Action.CreateStartingLegion):
            for creature_name in set(creaturedata.starting_creature_names):
                self.update_creature(creature_name)

        elif (isinstance(action, Action.RecruitCreature) or
          isinstance(action, Action.UndoRecruit) or
          isinstance(action, Action.UnReinforce)):
            creature_name = action.creature_name
            self.update_creature(creature_name)

        elif isinstance(action, Action.Flee or
          isinstance(action, Action.Concede) or
          isinstance(action, Action.AcceptProposal) or
          isinstance(action, Action.BattleOver)):
            for creature_name in self.caretaker.counts:
                self.update_creature(creature_name)

        elif isinstance(action, Action.DriftDamage or
          isinstance(action, Action.Strike) or
          isinstance(action, Action.Carry)):
            creature_name = action.target_name
            self.update_creature(creature_name)

        elif isinstance(action, Action.AcquireAngels):
            for creature_name in action.angel_names:
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

    caretaker = game.caretaker
    for unused in xrange(10):
        caretaker.take_one("Colossus")

    guicaretaker = GUICaretaker(game, username, None)
    guicaretaker.connect("destroy", guiutils.exit)
    gtk.main()
