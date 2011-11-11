#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon


class ShowLegion(gtk.Dialog):
    """Window to show a legion's contents."""
    def __init__(self, username, legion, show_marker, parent):
        gtk.Dialog.__init__(self, "Show Legion", parent)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("ShowLegion - %s" % (username))

        legion_name = gtk.Label("Legion %s (%s) in hex %s (%d points)" % (
          legion.markerid, legion.picname, legion.hexlabel, legion.score))
        self.vbox.pack_start(legion_name)

        hbox = gtk.HBox(spacing=3)
        self.vbox.pack_start(hbox)

        marker_hbox = gtk.HBox()
        hbox.pack_start(marker_hbox, expand=False)
        chits_hbox = gtk.HBox(spacing=3)
        hbox.pack_start(chits_hbox, expand=True)

        marker = None
        if show_marker:
            marker = Marker.Marker(legion, True, scale=20)
            marker_hbox.pack_start(marker.event_box, expand=False)

        # TODO Handle unknown creatures correctly
        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, legion.player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, expand=False)

        self.show_all()


if __name__ == "__main__":
    import time
    from slugathon.data import creaturedata
    from slugathon.game import Creature, Legion, Game, Player
    from slugathon.util import guiutils

    now = time.time()
    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]
    username = "test"
    game = Game.Game("g1", username, now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    showlegion = ShowLegion(username, legion, True, None)
    showlegion.connect("destroy", guiutils.exit)

    gtk.main()
