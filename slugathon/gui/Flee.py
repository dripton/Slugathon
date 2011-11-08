#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2010 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import defer, reactor
import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util.log import log


DO_NOT_FLEE = 0
FLEE = 1


def new(username, attacker_legion, defender_legion, parent):
    """Create a Flee dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    flee = Flee(username, attacker_legion, defender_legion, def1, parent)
    return flee, def1


class Flee(gtk.Dialog):
    """Dialog to choose whether to flee."""
    def __init__(self, username, attacker_legion, defender_legion, def1,
      parent):
        gtk.Dialog.__init__(self, "Flee - %s" % (username), parent)
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        self.vbox.set_spacing(9)

        hexlabel = defender_legion.hexlabel
        masterhex = defender_legion.player.game.board.hexes[hexlabel]
        self.legion_name = gtk.Label("Flee with legion %s (%s) in %s hex %s?"
          % (defender_legion.markername, defender_legion.picname,
          masterhex.terrain, hexlabel))
        self.vbox.pack_start(self.legion_name)

        self.attacker_hbox = gtk.HBox(False, 15)
        self.vbox.pack_start(self.attacker_hbox)

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        self.attacker_hbox.pack_start(self.attacker_marker.event_box,
          expand=False, fill=False)

        self.attacker_score_label = gtk.Label("%d\npoints" %
          attacker_legion.score)
        self.attacker_hbox.pack_start(self.attacker_score_label, expand=False)

        self.attacker_chits_hbox = gtk.HBox(False, 3)
        self.attacker_hbox.pack_start(self.attacker_chits_hbox, expand=True,
          fill=True)
        for creature in attacker_legion.sorted_creatures:
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20)
            chit.show()
            self.attacker_chits_hbox.pack_start(chit.event_box, expand=False)

        self.defender_hbox = gtk.HBox(False, 15)
        self.vbox.pack_start(self.defender_hbox)

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        self.defender_hbox.pack_start(self.defender_marker.event_box,
          expand=False, fill=False)

        self.defender_score_label = gtk.Label("%d\npoints" %
          defender_legion.score)
        self.defender_hbox.pack_start(self.defender_score_label, expand=False)

        self.defender_chits_hbox = gtk.HBox(False, 3)
        self.defender_hbox.pack_start(self.defender_chits_hbox, expand=True,
          fill=True)
        for creature in defender_legion.sorted_creatures:
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20)
            chit.show()
            self.defender_chits_hbox.pack_start(chit.event_box, expand=False)

        self.add_button("Do Not Flee", DO_NOT_FLEE)
        self.add_button("Flee", FLEE)

        self.connect("response", self.cb_response)
        self.show_all()

    def cb_response(self, widget, response_id):
        """Fires the deferred, with the attacker, the defender, and
        a boolean which is True iff the user chose to flee."""
        self.destroy()
        self.deferred.callback((self.attacker_legion, self.defender_legion,
          response_id))


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game

    now = time.time()
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

    def my_callback((attacker, defender, fled)):
        log("fled is", fled)
        reactor.stop()

    _, def1 = new(defender_username, attacker_legion, defender_legion, None)
    def1.addCallback(my_callback)
    reactor.run()
