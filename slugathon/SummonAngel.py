#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

import Chit
import Marker
import icon


class SummonAngel(object):
    """Dialog to summon an angel."""
    def __init__(self, username, player, legion, callback, parent):
        self.player = player
        self.legion = legion
        self.callback = callback
        self.builder = gtk.Builder()
        self.donor = None
        self.summonable = None

        self.builder.add_from_file("../ui/summonangel.ui")
        self.widget_names = ["summon_angel_dialog", "top_label",
          "middle_label", "bottom_label", "vbox1"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.summon_angel_dialog.set_icon(icon.pixbuf)
        self.summon_angel_dialog.set_title("SummonAngel - %s" % (username))
        self.summon_angel_dialog.set_transient_for(parent)

        self.top_label.set_text("Summoning an angel into legion %s in hex %s"
          % (legion.markername, legion.hexlabel))

        for legion2 in self.player.legions.itervalues():
            if legion2.any_summonable:
                print legion2, "has a summonable"
                hbox = gtk.HBox(spacing=3)
                hbox.show()
                self.vbox1.pack_start(hbox)
                marker = Marker.Marker(legion2, False, scale=20)
                hbox.pack_start(marker.event_box, expand=False, fill=False)
                marker.show()
                for creature in legion2.sorted_creatures:
                    chit = Chit.Chit(creature, self.player.color, scale=20,
                      outlined=creature.summonable)
                    chit.show()
                    hbox.pack_start(chit.event_box, expand=False, fill=False)
                    if creature.summonable:
                        chit.connect("button-press-event", self.cb_click)

        self.summon_angel_dialog.connect("response", self.cb_response)
        self.summon_angel_dialog.show()


    def cb_click(self, widget, event):
        """Summon the clicked-on Chit's creature."""
        eventbox = widget
        chit = eventbox.chit
        creature = chit.creature
        donor = creature.legion
        self.summon_angel_dialog.destroy()
        self.callback(self.legion, donor, creature)

    def cb_response(self, widget, response_id):
        self.summon_angel_dialog.destroy()


if __name__ == "__main__":
    import time
    import Creature
    import Legion
    import Player
    import guiutils
    import Game

    now = time.time()
    username = "test"
    game = Game.Game("g1", username, now, now, 2, 6)
    player = Player.Player(username, game, 0)
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
        player.legions[legion.markername] = legion

    def callback(legion, donor, creature):
        print "Will summon", creature, "from", donor, "into", legion
        guiutils.exit()

    summonangel = SummonAngel(username, player, legion1, callback, None)
    summonangel.summon_angel_dialog.connect("destroy", guiutils.exit)

    gtk.main()
