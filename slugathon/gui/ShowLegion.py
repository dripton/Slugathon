#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import guiutils


class ShowLegion(object):
    """Window to show a legion's contents."""
    def __init__(self, username, legion, playercolor, show_marker):
        self.builder = gtk.Builder()
        self.builder.add_from_file(guiutils.basedir("ui/showlegion.ui"))
        self.widget_names = ["show_legion_window", "marker_hbox", "chits_hbox",
          "legion_name"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.show_legion_window.set_icon(icon.pixbuf)
        self.show_legion_window.set_title("ShowLegion - %s" % (username))

        self.legion_name.set_text("Legion %s in hex %s (%d points)" % (
          legion.markername, legion.hexlabel, legion.score))

        self.marker = None
        if show_marker:
            self.marker = Marker.Marker(legion, True, scale=20)
            self.marker_hbox.pack_start(self.marker.event_box, expand=False,
              fill=False)
            self.marker.show()

        # TODO Handle unknown creatures correctly
        for creature in legion.sorted_creatures:
            chit = Chit.Chit(creature, playercolor, scale=20)
            chit.show()
            self.chits_hbox.add(chit.event_box)

        self.show_legion_window.show()


if __name__ == "__main__":
    import time
    from slugathon.data import creaturedata
    from slugathon.game import Creature, Legion, Game, Player

    now = time.time()
    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]
    username = "test"
    game = Game.Game("g1", username, now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    showlegion = ShowLegion(username, legion, player.color, True)
    showlegion.show_legion_window.connect("destroy", guiutils.exit)

    gtk.main()
