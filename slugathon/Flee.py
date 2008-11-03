#!/usr/bin/env python

import time

import gtk
import gtk.glade

import Chit
import Marker
import Creature
import Legion
import Player
import icon
import guiutils
import Game


class Flee(object):
    """Dialog to choose whether to flee."""
    def __init__(self, username, attacker_legion, defender_legion,
      callback, parent):
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        self.callback = callback
        self.glade = gtk.glade.XML("../glade/flee.glade")
        self.widget_names = [
          "flee_dialog",
          "legion_name",
          "attacker_hbox",
          "attacker_marker_hbox",
          "attacker_chits_hbox",
          "defender_hbox",
          "defender_marker_hbox",
          "defender_chits_hbox",
          "flee_button",
          "do_not_flee_button"
        ]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.flee_dialog.set_icon(icon.pixbuf)
        self.flee_dialog.set_title("Flee - %s" % (username))
        self.flee_dialog.set_transient_for(parent)

        hexlabel = defender_legion.hexlabel
        masterhex = defender_legion.player.game.board.hexes[hexlabel]
        self.legion_name.set_text("Flee with legion %s in %s hex %s?" % (
          defender_legion.markername, masterhex.terrain, hexlabel))

        self.attacker_marker = Marker.Marker(attacker_legion, True, scale=20)
        self.attacker_marker_hbox.pack_start(self.attacker_marker.event_box,
          expand=False, fill=False)
        self.attacker_marker.show()

        self.defender_marker = Marker.Marker(defender_legion, True, scale=20)
        self.defender_marker_hbox.pack_start(self.defender_marker.event_box,
          expand=False, fill=False)
        self.defender_marker.show()

        for creature in attacker_legion.creatures:
            chit = Chit.Chit(creature, attacker_legion.player.color, scale=20)
            chit.show()
            self.attacker_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)

        for creature in defender_legion.creatures:
            chit = Chit.Chit(creature, defender_legion.player.color, scale=20)
            chit.show()
            self.defender_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)

        self.flee_dialog.connect("response", self.cb_response)
        self.flee_dialog.show()


    def cb_response(self, widget, response_id):
        """Calls the callback function, with the attacker, the defender, and
        a boolean which is True iff the user chose to flee."""
        self.flee_dialog.destroy()
        self.callback(self.attacker_legion, self.defender_legion,
          response_id == self.flee_dialog.get_response_for_widget(
          self.flee_button))


if __name__ == "__main__":
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

    def callback(attacker, defender, fled):
        print "fled is", fled
        guiutils.exit()

    flee = Flee(defender_username, attacker_legion, defender_legion,
      callback, None)

    gtk.main()
