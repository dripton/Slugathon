#!/usr/bin/env python

__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

from twisted.internet import defer
import gtk

from slugathon.gui import Chit, Marker, icon


def new(playername, legion, parent):
    """Create a SummonAngel dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    summonangel = SummonAngel(playername, legion, def1, parent)
    return summonangel, def1


class SummonAngel(gtk.Dialog):
    """Dialog to summon an angel."""
    def __init__(self, playername, legion, def1, parent):
        gtk.Dialog.__init__(self, "SummonAngel - %s" % playername, parent)
        self.legion = legion
        player = legion.player
        self.deferred = def1
        self.donor = None
        self.summonable = None

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        top_label = gtk.Label(
          "Summoning an angel into legion %s (%s) in hex %s"
          % (legion.markerid, legion.picname, legion.hexlabel))
        self.vbox.set_spacing(9)
        self.vbox.pack_start(top_label)
        middle_label = gtk.Label("Summonable creatures have a red border")
        self.vbox.pack_start(middle_label)
        bottom_label = gtk.Label("Click one to summon it.")
        self.vbox.pack_start(bottom_label)

        for legion2 in player.legions:
            if (legion2.any_summonable and not legion2.engaged and
              legion2 != legion):
                hbox = gtk.HBox(spacing=3)
                self.vbox.pack_start(hbox)
                marker = Marker.Marker(legion2, False, scale=20)
                hbox.pack_start(marker.event_box, expand=False, fill=False)
                for creature in legion2.sorted_creatures:
                    chit = Chit.Chit(creature, player.color, scale=20,
                      outlined=creature.summonable)
                    hbox.pack_start(chit.event_box, expand=False, fill=False)
                    if creature.summonable:
                        chit.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()

    def cb_click(self, widget, event):
        """Summon the clicked-on Chit's creature."""
        eventbox = widget
        chit = eventbox.chit
        creature = chit.creature
        donor = creature.legion
        self.deferred.callback((self.legion, donor, creature))
        self.destroy()

    def cb_cancel(self, widget, response_id):
        self.deferred.callback((self.legion, None, None))
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Creature, Legion, Player, Game
    from slugathon.util import guiutils

    now = time.time()
    playername = "test"
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    creatures1 = [Creature.Creature(name) for name in
      ["Titan", "Ogre", "Troll", "Ranger"]]
    creatures2 = [Creature.Creature(name) for name in
      ["Angel", "Ogre", "Troll", "Ranger"]]
    creatures3 = [Creature.Creature(name) for name in
      ["Archangel", "Centaur", "Lion", "Ranger"]]
    creatures4 = [Creature.Creature(name) for name in
      ["Gargoyle", "Cyclops", "Gorgon", "Behemoth"]]
    creatures5 = [Creature.Creature(name) for name in
      ["Angel", "Angel", "Warlock", "Guardian"]]
    legion1 = Legion.Legion(player, "Rd01", creatures1, 1)
    legion2 = Legion.Legion(player, "Rd02", creatures2, 2)
    legion3 = Legion.Legion(player, "Rd03", creatures3, 3)
    legion4 = Legion.Legion(player, "Rd04", creatures4, 4)
    legion5 = Legion.Legion(player, "Rd05", creatures5, 4)
    for legion in [legion1, legion2, legion3, legion4, legion5]:
        player.markerid_to_legion[legion.markerid] = legion

    def my_callback((legion, donor, creature)):
        logging.info("Will summon %s from %s into %s", creature, donor, legion)
        guiutils.exit()

    summonangel, def1 = new(playername, legion1, None)
    def1.addCallback(my_callback)
    summonangel.connect("destroy", guiutils.exit)

    gtk.main()
