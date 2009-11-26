#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2009 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils

class Negotiate(object):
    """Dialog to choose whether to concede, negotiate, or fight."""
    def __init__(self, username, attacker_legion, defender_legion,
      callback, parent):
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        self.callback = callback
        self.builder = gtk.Builder()
        self.builder.add_from_file(guiutils.basedir("ui/negotiate.ui"))
        self.widget_names = [
          "negotiate_dialog",
          "legion_name",
          "attacker_hbox",
          "attacker_marker_hbox",
          "attacker_chits_hbox",
          "defender_hbox",
          "defender_marker_hbox",
          "defender_chits_hbox",
          "concede_button",
          "proposal_button",
          "done_proposing_button",
          "fight_button",
        ]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.proposal_button.set_sensitive(False)

        self.negotiate_dialog.set_icon(icon.pixbuf)
        self.negotiate_dialog.set_title("Negotiate - %s" % (username))
        self.negotiate_dialog.set_transient_for(parent)

        self.legion_name.set_text("Legion %s negotiates with %s in hex %s?" % (
          attacker_legion.markername, defender_legion.markername,
          defender_legion.hexlabel))

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        self.attacker_marker_hbox.pack_start(self.attacker_marker.event_box,
          expand=False, fill=False)
        self.attacker_marker.connect("button-press-event", self.cb_click)
        self.attacker_marker.show()

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        self.defender_marker_hbox.pack_start(self.defender_marker.event_box,
          expand=False, fill=False)
        self.defender_marker.connect("button-press-event", self.cb_click)
        self.defender_marker.show()

        self.attacker_chits = []

        for creature in attacker_legion.creatures:
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20)
            chit.show()
            self.attacker_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button-press-event", self.cb_click)
            self.attacker_chits.append(chit)

        self.defender_chits = []

        for creature in defender_legion.creatures:
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20)
            chit.show()
            self.defender_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button-press-event", self.cb_click)
            self.defender_chits.append(chit)

        self.negotiate_dialog.connect("response", self.cb_response)
        self.negotiate_dialog.show()

    def cb_click(self, widget, event):
        """Toggle the clicked-on chit's creature's status."""
        event_box = widget
        if hasattr(event_box, "chit"):
            chit = event_box.chit
            chit.dead = not chit.dead
            # XXX What's the right way to force a repaint?
            chit.build_image()
        else:
            marker = event_box.marker
            if marker == self.attacker_marker:
                chits = self.attacker_chits
            else:
                chits = self.defender_chits
            num_alive = 0
            num_dead = 0
            for chit in chits:
                if chit.dead:
                    num_dead += 1
                else:
                    num_alive += 1
            dead = num_alive >= num_dead
            for chit in chits:
                chit.dead = dead
                chit.build_image()
        legal = self.is_legal_proposal()
        self.proposal_button.set_sensitive(legal)

    def all_dead(self, li):
        """Return True if all elements in the list are dead."""
        for chit in li:
            if not chit.dead:
                return False
        return True

    def is_legal_proposal(self):
        """Return True iff at least one of the two legions is completely
        dead."""
        return self.all_dead(self.attacker_chits) or self.all_dead(
          self.defender_chits)

    def surviving_creature_names(self, chits):
        """Return a list of creature names for the survivors."""
        li = []
        for chit in chits:
            if not chit.dead:
                li.append(chit.creature.name)
        return li

    def cb_response(self, widget, response_id):
        """Calls the callback function, with the attacker, the defender, and
        the response_id."""
        self.negotiate_dialog.destroy()
        attacker_creature_names = self.surviving_creature_names(
          self.attacker_chits)
        defender_creature_names = self.surviving_creature_names(
          self.defender_chits)
        self.callback(self.attacker_legion, attacker_creature_names,
          self.defender_legion, defender_creature_names, response_id)

    def destroy(self):
        self.negotiate_dialog.destroy()

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
    attacker_creatures = Creature.n2c(attacker_creature_names)
    attacker_legion = Legion.Legion(attacker_player, "Bk01",
      attacker_creatures, 1)

    defender_username = "Eek!"
    defender_player = Player.Player(defender_username, game, 0)
    defender_player.color = "Gold"
    defender_creature_names = ["Ogre", "Centaur", "Gargoyle"]
    defender_creatures = Creature.n2c(defender_creature_names)
    defender_legion = Legion.Legion(defender_player, "Rd01",
      defender_creatures, 1)

    def callback(*args):
        print "callback", args
        guiutils.exit()

    negotiate = Negotiate(defender_username, attacker_legion, defender_legion,
      callback, None)
    gtk.main()
