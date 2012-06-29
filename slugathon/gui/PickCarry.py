#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor, defer
import gtk

from slugathon.gui import icon


def new(playername, game_name, striker, target, num_dice, strike_number,
  carries, parent):
    """Create a PickCarry dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    pickcarry = PickCarry(playername, game_name, striker, target, num_dice,
      strike_number, carries, def1, parent)
    return pickcarry, def1


class PickCarry(gtk.Dialog):
    """Dialog to pick whether and where to carry excess hits."""
    def __init__(self, playername, game_name, striker, target, num_dice,
      strike_number, carries, def1, parent):
        gtk.Dialog.__init__(self, "PickCarry - %s" % playername, parent)
        self.playername = playername
        self.game_name = game_name
        self.carries = carries
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        label = gtk.Label("%r strikes %r and may carry over %d hit%s." %
          (striker, target, carries, "" if carries == 1 else "s"))
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

    def cb_click(self, widget, event):
        creature = widget.creature
        self.destroy()
        if creature:
            self.deferred.callback((creature, self.carries))
        else:
            self.deferred.callback((None, 0))


if __name__ == "__main__":
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
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    rd01 = player0.markerid_to_legion["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    bu01 = player1.markerid_to_legion["Bu01"]

    rd01.move(6, False, None, 3)
    bu01.move(6, False, None, 3)
    game._init_battle(bu01, rd01)
    defender = game.defender_legion
    titan1 = defender.creatures[0]
    titan1.move("F2")
    ogre1 = defender.creatures[1]
    ogre1.move("E2")
    centaur1 = defender.creatures[2]
    centaur1.move("D2")
    gargoyle1 = defender.creatures[3]
    gargoyle1.move("C1")

    attacker = game.attacker_legion
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

    def my_callback((creature, carries)):
        logging.info("carry %d hits to %s" % (carries, creature))
        reactor.stop()

    _, def1 = new(playername, game_name, titan2, centaur1, 6, 4, 1, None)
    def1.addCallback(my_callback)
    reactor.run()
