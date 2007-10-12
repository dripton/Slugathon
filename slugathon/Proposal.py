#!/usr/bin/env python 

import time

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade

import Chit
import Marker
import creaturedata
import Creature
import Legion
import Player
import icon
import guiutils
import Game
from bag import bag

class Proposal(object):
    """Dialog to choose whether to accept an opponent's proposal."""
    def __init__(self, username, attacker_legion, attacker_creature_names, 
      defender_legion, defender_creature_names, callback, parent):
        self.attacker_legion = attacker_legion
        self.attacker_creature_names = attacker_creature_names
        self.defender_legion = defender_legion
        self.defender_creature_names = defender_creature_names
        self.callback = callback
        self.glade = gtk.glade.XML("../glade/proposal.glade")
        self.widget_names = [
          "proposal_dialog", 
          "legion_name", 
          "attacker_hbox", 
          "attacker_marker_hbox", 
          "attacker_chits_hbox", 
          "defender_hbox", 
          "defender_marker_hbox", 
          "defender_chits_hbox", 
          "accept_button", 
          "reject_button", 
        ]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.proposal_dialog.set_icon(icon.pixbuf)
        self.proposal_dialog.set_title("Proposal - %s" % (username))
        self.proposal_dialog.set_transient_for(parent)

        self.legion_name.set_text("Legion %s negotiates with %s in hex %s?" % (
          attacker_legion.markername, defender_legion.markername, 
          defender_legion.hexlabel))

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        self.attacker_marker_hbox.pack_start(self.attacker_marker.event_box,
          expand=False, fill=False)
        self.attacker_marker.show()

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        self.defender_marker_hbox.pack_start(self.defender_marker.event_box,
          expand=False, fill=False)
        self.defender_marker.show()

        self.attacker_chits = []

        surviving_attackers = bag(attacker_creature_names)
        surviving_defenders = bag(defender_creature_names)

        for creature in attacker_legion.creatures:
            name = creature.name
            if name in surviving_attackers:
                surviving_attackers.remove(name)
                dead = False
            else:
                dead = True
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20,
              dead=dead)
            chit.show()
            self.attacker_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            self.attacker_chits.append(chit)

        self.defender_chits = []

        for creature in defender_legion.creatures:
            name = creature.name
            if name in surviving_defenders:
                surviving_defenders.remove(name)
                dead = False
            else:
                dead = True
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20,
              dead=dead)
            chit.show()
            self.defender_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            self.defender_chits.append(chit)

        self.proposal_dialog.connect("response", self.cb_response)
        self.proposal_dialog.show()

    def cb_response(self, widget, response_id):
        """Calls the callback function, with the attacker, the defender, and
        the response_id."""
        self.proposal_dialog.destroy()
        self.callback(self.attacker_legion, self.attacker_creature_names,
          self.defender_legion, self.defender_creature_names, response_id)

    def destroy(self):
        self.proposal_dialog.destroy()

if __name__ == "__main__":
    now = time.time()
    game_name = "Game1"
    attacker_username = "Roar!"
    game = Game.Game("g1", attacker_username, now, now, 2, 6)
    attacker_player = Player.Player(attacker_username, game, 0)
    attacker_player.color = "Black"
    attacker_creature_names = ["Titan", "Colossus", "Serpent", "Hydra",
      "Archangel", "Angel", "Unicorn"]
    attacker_survivor_names = ["Titan", "Colossus", "Serpent", "Hydra",
      "Archangel", "Angel"]
    attacker_creatures = Creature.n2c(attacker_creature_names)
    attacker_legion = Legion.Legion(attacker_player, "Bk01", 
      attacker_creatures, 1)

    defender_username = "Eek!"
    defender_player = Player.Player(defender_username, game, 0)
    defender_player.color = "Gold"
    defender_creature_names = ["Ogre", "Centaur", "Gargoyle"]
    defender_survivor_names = []
    defender_creatures = Creature.n2c(defender_creature_names)
    defender_legion = Legion.Legion(defender_player, "Rd01", 
      defender_creatures, 1)

    def callback(*args):
        print "callback", args
        guiutils.exit()

    proposal = Proposal(defender_username, attacker_legion, 
      attacker_survivor_names, defender_legion, defender_survivor_names, 
      callback, None)
    gtk.main()
