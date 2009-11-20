#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"

import gtk

import icon
import Phase


class PickStrikePenalty(object):
    """Dialog to pick whether to take a strike penalty to allow carrying 
    excess hits."""
    def __init__(self, username, game_name, striker, target, callback, parent):
        self.username = username
        self.game_name = game_name
        self.striker = striker
        self.target = target
        self.callback = callback

        self.pick_strike_penalty_dialog = gtk.Dialog()

        self.pick_strike_penalty_dialog.set_icon(icon.pixbuf)
        self.pick_strike_penalty_dialog.set_title("PickStrikePenalty - %s" %
          (self.username))
        self.pick_strike_penalty_dialog.set_transient_for(parent)

        label = gtk.Label("Choose strike penalty for %r striking %r?" %
          (striker, target))
        label.show()
        # We could use get_content_area() instead of vbox, in PyGTK 2.14+
        self.pick_strike_penalty_dialog.vbox.add(label)

        num_dice = striker.number_of_dice(target)
        strike_number = striker.strike_number(target)
        # Map tuple of (num_dice, strike_number) to set of creatures it can hit
        dice_strike_to_creatures = {}
        dice_strike_to_creatures[(num_dice, strike_number)] = set()
        for creature in striker.engaged_enemies:
            if creature is not target:
                num_dice2 = striker.number_of_dice(creature)
                strike_number2 = striker.strike_number(creature)
                tup = (num_dice2, strike_number2)
                dice_strike_to_creatures.setdefault(tup, set()).add(creature)
        for ii, (tup, creatures) in enumerate(sorted(
          dice_strike_to_creatures.iteritems())):
            (num_dice3, strike_number3) = tup
            if creatures:
                st = "%d dice at strike number %d, able to carry to %s" % (
                  num_dice3, strike_number3, ", ".join(sorted(
                  repr(creature) for creature in creatures)))
            else:
                st = "%d dice at strike number %d, unable to carry" % (
                  num_dice3, strike_number3)
            button = self.pick_strike_penalty_dialog.add_button(st, ii)
            button.tup = tup
            button.show()
            button.connect("button-press-event", self.cb_click)
        button = self.pick_strike_penalty_dialog.add_button("Cancel strike",
          ii + 1)
        button.tup = None
        button.show()
        button.connect("button-press-event", self.cb_click)

        self.pick_strike_penalty_dialog.show()


    def cb_click(self, widget, event):
        tup = widget.tup
        if tup is None:
            self.callback(None, None, None, None)
        else:
            num_dice, strike_number = tup
            self.callback(self.striker, self.target, num_dice, strike_number)
        self.pick_strike_penalty_dialog.destroy()


if __name__ == "__main__":
    import time
    import guiutils
    import Game

    now = time.time()
    username = "p0"
    game_name = "g1"
    game = Game.Game(game_name, username, now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p0", "Red")
    game.assign_color("p1", "Blue")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    rd01 = player0.legions["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    bu01 = player1.legions["Bu01"]

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

    def my_callback(striker, target, num_dice, strike_number):
        print "called my_callback", striker, target, num_dice, strike_number
        guiutils.exit()

    pick_strike_penalty = PickStrikePenalty(username, game_name, titan2,
      centaur1, my_callback, None)
    # XXX Remove commented-out code
    #pick_strike_penalty.pick_strike_penalty_dialog.connect("destroy",
    #  guiutils.exit)
    gtk.main()
