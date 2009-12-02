#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util.bag import bag
from slugathon.util import guiutils

ACCEPT = 0
REJECT = 1

class Proposal(gtk.Dialog):
    """Dialog to choose whether to accept an opponent's proposal."""
    def __init__(self, username, attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names, callback, parent):
        gtk.Dialog.__init__(self, "Proposal - %s" % username, parent)
        self.attacker_legion = attacker_legion
        self.attacker_creature_names = attacker_creature_names
        self.defender_legion = defender_legion
        self.defender_creature_names = defender_creature_names
        self.callback = callback

        [
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

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_has_separator(False)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label("Legion %s negotiates with %s in hex %s" % (
          attacker_legion.markername, defender_legion.markername,
          defender_legion.hexlabel))
        self.vbox.pack_start(legion_name)

        attacker_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(attacker_hbox)
        attacker_marker_hbox = gtk.HBox()
        attacker_hbox.pack_start(attacker_marker_hbox, expand=False)
        attacker_chits_hbox = gtk.HBox(spacing=3)
        attacker_hbox.pack_start(attacker_chits_hbox)

        attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        attacker_marker_hbox.pack_start(attacker_marker.event_box,
          expand=False)

        defender_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(defender_hbox)
        defender_marker_hbox = gtk.HBox()
        defender_hbox.pack_start(defender_marker_hbox, expand=False)
        defender_chits_hbox = gtk.HBox(spacing=3)
        defender_hbox.pack_start(defender_chits_hbox)

        defender_marker = Marker.Marker(defender_legion, True, scale=20)
        defender_marker_hbox.pack_start(defender_marker.event_box,
          expand=False)

        attacker_chits = []

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
            attacker_chits_hbox.pack_start(chit.event_box, expand=False)
            attacker_chits.append(chit)

        defender_chits = []

        for creature in defender_legion.creatures:
            name = creature.name
            if name in surviving_defenders:
                surviving_defenders.remove(name)
                dead = False
            else:
                dead = True
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20,
              dead=dead)
            defender_chits_hbox.pack_start(chit.event_box, expand=False)
            defender_chits.append(chit)

        hseparator = gtk.HSeparator()
        self.vbox.pack_start(hseparator)

        buttons_hbox = gtk.HBox(homogeneous=True)
        self.vbox.pack_start(buttons_hbox)

        accept_button = gtk.Button("Accept")
        accept_button.connect("button-press-event", self.cb_click)
        accept_button.response_id = ACCEPT
        buttons_hbox.pack_start(accept_button)

        reject_button = gtk.Button("Reject")
        reject_button.connect("button-press-event", self.cb_click)
        reject_button.response_id = REJECT
        buttons_hbox.pack_start(reject_button)

        self.show_all()


    def cb_click(self, widget, event):
        """Calls the callback function, with the attacker, the defender, and
        the response_id."""
        self.destroy()
        self.callback(self.attacker_legion, self.attacker_creature_names,
          self.defender_legion, self.defender_creature_names,
          widget.response_id)


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game

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
