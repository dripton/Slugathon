#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import defer, reactor
import gtk

from slugathon.gui import Chit, Marker, icon


CONCEDE = 0
MAKE_PROPOSAL = 1
DONE_PROPOSING = 2
FIGHT = 3


def new(playername, attacker_legion, defender_legion, parent):
    """Create a Negotiate dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    negotiate = Negotiate(playername, attacker_legion, defender_legion, def1,
      parent)
    return negotiate, def1


class Negotiate(gtk.Dialog):
    """Dialog to choose whether to concede, negotiate, or fight."""
    def __init__(self, playername, attacker_legion, defender_legion,
      def1, parent):
        gtk.Dialog.__init__(self, "Negotiate - %s" % playername, parent)
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label(
          "Legion %s (%s) negotiates with %s (%s) in hex %s?" % (
          attacker_legion.markerid, attacker_legion.picname,
          defender_legion.markerid, defender_legion.picname,
          defender_legion.hexlabel))
        self.vbox.pack_start(legion_name)

        attacker_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(attacker_hbox)
        attacker_marker_hbox = gtk.HBox()
        attacker_hbox.pack_start(attacker_marker_hbox, expand=False)
        attacker_score_label = gtk.Label("%d\n points" %
          attacker_legion.score)
        attacker_hbox.pack_start(attacker_score_label, expand=False)
        attacker_chits_hbox = gtk.HBox(spacing=3)
        attacker_hbox.pack_start(attacker_chits_hbox)

        defender_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(defender_hbox)
        defender_marker_hbox = gtk.HBox()
        defender_hbox.pack_start(defender_marker_hbox, expand=False)
        defender_chits_hbox = gtk.HBox(spacing=3)
        defender_score_label = gtk.Label("%d\n points" %
          defender_legion.score)
        defender_hbox.pack_start(defender_score_label, expand=False)
        defender_hbox.pack_start(defender_chits_hbox)

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        attacker_marker_hbox.pack_start(self.attacker_marker.event_box,
          expand=False)
        self.attacker_marker.connect("button-press-event", self.cb_click)

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        defender_marker_hbox.pack_start(self.defender_marker.event_box,
          expand=False)
        self.defender_marker.connect("button-press-event", self.cb_click)

        self.attacker_chits = []

        for creature in attacker_legion.sorted_creatures:
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20)
            attacker_chits_hbox.pack_start(chit.event_box, expand=False)
            chit.connect("button-press-event", self.cb_click)
            self.attacker_chits.append(chit)

        self.defender_chits = []

        for creature in defender_legion.sorted_creatures:
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20)
            defender_chits_hbox.pack_start(chit.event_box, expand=False)
            chit.connect("button-press-event", self.cb_click)
            self.defender_chits.append(chit)

        self.add_button("Concede", CONCEDE)
        self.proposal_button = self.add_button("Make proposal", MAKE_PROPOSAL)
        self.add_button("No more proposals", DONE_PROPOSING)
        self.add_button("Fight", FIGHT)
        self.connect("response", self.cb_response)

        self.proposal_button.set_sensitive(False)

        self.show_all()

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
        return [chit.creature.name for chit in chits if not chit.dead]

    def cb_response(self, widget, response_id):
        """Fires the Deferred, with the attacker, the defender, and
        the response_id."""
        self.destroy()
        attacker_creature_names = self.surviving_creature_names(
          self.attacker_chits)
        defender_creature_names = self.surviving_creature_names(
          self.defender_chits)
        self.deferred.callback((self.attacker_legion, attacker_creature_names,
          self.defender_legion, defender_creature_names, response_id))


if __name__ == "__main__":
    import time

    from slugathon.game import Creature, Legion, Player, Game

    now = time.time()
    game_name = "Game1"
    attacker_playername = "Roar!"
    game = Game.Game("g1", attacker_playername, now, now, 2, 6)
    attacker_player = Player.Player(attacker_playername, game, 0)
    attacker_player.color = "Black"
    attacker_creature_names = ["Titan", "Colossus", "Serpent", "Hydra",
      "Archangel", "Angel", "Unicorn"]
    attacker_creatures = Creature.n2c(attacker_creature_names)
    attacker_legion = Legion.Legion(attacker_player, "Bk01",
      attacker_creatures, 1)

    defender_playername = "Eek!"
    defender_player = Player.Player(defender_playername, game, 0)
    defender_player.color = "Gold"
    defender_creature_names = ["Ogre", "Centaur", "Gargoyle"]
    defender_creatures = Creature.n2c(defender_creature_names)
    defender_legion = Legion.Legion(defender_player, "Rd01",
      defender_creatures, 1)

    def my_callback(*args):
        logging.info("callback %s", args)
        reactor.stop()

    _, def1 = new(defender_playername, attacker_legion, defender_legion, None)
    def1.addCallback(my_callback)
    reactor.run()
