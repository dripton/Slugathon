#!/usr/bin/env python3

__copyright__ = "Copyright (c) 2006-2012 David Ripton"
__license__ = "GNU GPL v2"


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

from slugathon.gui import Chit, Marker
from slugathon.data import recruitdata
from slugathon.game import Creature


class Inspector(Gtk.EventBox):

    """Window to show a legion's contents."""

    def __init__(self, playername):
        GObject.GObject.__init__(self)

        self.playername = playername

        self.vbox = Gtk.VBox()
        self.add(self.vbox)

        self.legion_name = Gtk.Label()
        self.vbox.pack_start(self.legion_name, True, True, 0)

        hbox = Gtk.HBox(spacing=3)
        self.vbox.pack_start(hbox, True, True, 0)

        self.marker_hbox = Gtk.HBox(spacing=3)
        hbox.pack_start(self.marker_hbox, False, True, 0)
        self.chits_hbox = Gtk.HBox(spacing=3)
        hbox.pack_start(self.chits_hbox, True, True, 0)

        self.legion = None
        self.marker = None

    def show_legion(self, legion):
        self.legion_name.set_text(
            "Legion %s (%s) in hex %s (%d%s points)"
            % (
                legion.markerid,
                legion.picname,
                legion.hexlabel,
                legion.score,
                "+?" if legion.any_unknown else "",
            )
        )

        for hbox in [self.marker_hbox, self.chits_hbox]:
            for child in hbox.get_children():
                hbox.remove(child)

        self.marker = Marker.Marker(legion, True, scale=15)
        self.marker_hbox.pack_start(self.marker.event_box, False, True, 0)

        playercolor = legion.player.color
        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, playercolor, scale=15)
            self.chits_hbox.pack_start(chit.event_box, False, True, 0)

        self.show_all()

    def show_recruit_tree(self, terrain, playercolor):
        """Show the recruit tree for terrain."""
        self.legion_name.set_text(terrain)
        for hbox in [self.marker_hbox, self.chits_hbox]:
            for child in hbox.get_children():
                hbox.remove(child)
        tuples = recruitdata.data[terrain]
        for tup in tuples:
            if len(tup) == 2 and tup[1] != 0:
                creature_name, count = tup
                if count >= 2:
                    label = Gtk.Label(label=str(count))
                    self.chits_hbox.pack_start(label, False, True, 0)
                creature = Creature.Creature(creature_name)
                chit = Chit.Chit(creature, playercolor, scale=15)
                self.chits_hbox.pack_start(chit.event_box, False, True, 0)
        self.show_all()


if __name__ == "__main__":
    import random
    from slugathon.data import creaturedata, playercolordata
    from slugathon.game import Legion, Player
    from slugathon.util import guiutils

    def cb_destroy(confirmed):
        print("destroy")
        inspector.destroy()
        Gtk.main_quit()

    creatures = [
        Creature.Creature(name)
        for name in creaturedata.starting_creature_names
    ]

    playername = "test"
    player = Player.Player(playername, None, None)
    player.color = random.choice(playercolordata.colors)
    abbrev = player.color_abbrev
    index = random.randrange(1, 12 + 1)
    inspector = Inspector(playername)
    inspector.connect("destroy", guiutils.exit)

    legion = Legion.Legion(player, "%s%02d" % (abbrev, index), creatures, 1)
    inspector.show_legion(legion)

    creatures2 = [
        Creature.Creature(name)
        for name in ["Angel", "Giant", "Warbear", "Unicorn"]
    ]
    index = random.randrange(1, 12 + 1)
    legion2 = Legion.Legion(player, "%s%02d" % (abbrev, index), creatures2, 2)
    inspector.show_legion(legion2)

    window = Gtk.Window()
    window.add(inspector)
    window.show_all()

    Gtk.main()
