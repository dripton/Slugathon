#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon


class Inspector(gtk.Window):
    """Window to show a legion's contents."""
    def __init__(self, username):
        gtk.Window.__init__(self)

        self.set_icon(icon.pixbuf)
        self.set_title("Inspector - %s" % (username))

        vbox = gtk.VBox(spacing=9)
        self.add(vbox)

        self.legion_name = gtk.Label()
        vbox.pack_start(self.legion_name)

        hbox = gtk.HBox(spacing=3)
        vbox.pack_start(hbox)

        self.marker_hbox = gtk.HBox(spacing=3)
        hbox.pack_start(self.marker_hbox, expand=False)
        self.chits_hbox = gtk.HBox(spacing=3)
        hbox.pack_start(self.chits_hbox, expand=True)

        self.legion = None
        self.marker = None
        self.destroyed = False

        self.connect("delete-event", self.hide_window)


    def show_legion(self, legion):
        self.legion_name.set_text("Legion %s in hex %s (%d points)" % (
          legion.markername, legion.hexlabel, legion.score))

        for hbox in [self.marker_hbox, self.chits_hbox]:
            for child in hbox.get_children():
                hbox.remove(child)

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False)

        # TODO Handle unknown creatures correctly
        playercolor = legion.player.color
        for creature in legion.sorted_creatures:
            chit = Chit.Chit(creature, playercolor, scale=20)
            self.chits_hbox.pack_start(chit.event_box, expand=False)

        self.show_all()

    def destroy(self, unused):
        self.destroyed = True

    def hide_window(self, event, unused):
        self.hide()
        return True


if __name__ == "__main__":
    import random
    from slugathon.data import creaturedata, playercolordata
    from slugathon.game import Creature, Legion, Player

    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]

    username = "test"
    player = Player.Player(username, None, None)
    player.color = random.choice(playercolordata.colors)
    abbrev = playercolordata.name_to_abbrev[player.color]
    inspector = Inspector(username)

    legion = Legion.Legion(player, "%s01" % abbrev, creatures, 1)
    inspector.show_legion(legion)

    creatures2 = [Creature.Creature(name) for name in
      ["Angel", "Giant", "Warbear", "Unicorn"]]
    legion2 = Legion.Legion(player, "%s02" % abbrev, creatures2, 2)
    inspector.show_legion(legion2)

    gtk.main()
