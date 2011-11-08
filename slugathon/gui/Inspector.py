#!/usr/bin/env python

__copyright__ = "Copyright (c) 2006-2011 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.util import prefs


class Inspector(gtk.Dialog):
    """Window to show a legion's contents."""
    def __init__(self, username, parent):
        gtk.Dialog.__init__(self, "Inspector", parent)

        self.username = username

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Inspector - %s" % (username))

        self.legion_name = gtk.Label()
        self.vbox.pack_start(self.legion_name)

        hbox = gtk.HBox(spacing=3)
        self.vbox.pack_start(hbox)

        self.marker_hbox = gtk.HBox(spacing=3)
        hbox.pack_start(self.marker_hbox, expand=False)
        self.chits_hbox = gtk.HBox(spacing=3)
        hbox.pack_start(self.chits_hbox, expand=True)

        self.legion = None
        self.marker = None

        if self.username:
            tup = prefs.load_window_position(self.username,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(self.username,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.resize(width, height)

        self.connect("delete-event", self.hide_window)
        self.connect("configure-event", self.cb_configure_event)

    def cb_configure_event(self, event, unused):
        if self.username:
            x, y = self.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.username, self.__class__.__name__,
              width, height)
        return False

    def show_legion(self, legion):
        self.legion_name.set_text("Legion %s (%s) in hex %s (%d points)" % (
          legion.markername, legion.picname, legion.hexlabel, legion.score))

        for hbox in [self.marker_hbox, self.chits_hbox]:
            for child in hbox.get_children():
                hbox.remove(child)

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False)

        # TODO Handle unknown creatures correctly
        playercolor = legion.player.color
        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, playercolor, scale=20)
            self.chits_hbox.pack_start(chit.event_box, expand=False)

        self.show_all()

    def hide_window(self, event, unused):
        self.hide()
        return True


if __name__ == "__main__":
    import random
    from slugathon.data import creaturedata, playercolordata
    from slugathon.game import Creature, Legion, Player

    def cb_destroy(confirmed):
        print "destroy"
        inspector.destroy()
        gtk.main_quit()

    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]

    username = "test"
    player = Player.Player(username, None, None)
    player.color = random.choice(playercolordata.colors)
    abbrev = player.color_abbrev
    index = random.randrange(1, 12 + 1)
    inspector = Inspector(username, None)

    legion = Legion.Legion(player, "%s%02d" % (abbrev, index), creatures, 1)
    inspector.show_legion(legion)

    creatures2 = [Creature.Creature(name) for name in
      ["Angel", "Giant", "Warbear", "Unicorn"]]
    index = random.randrange(1, 12 + 1)
    legion2 = Legion.Legion(player, "%s%02d" % (abbrev, index), creatures2, 2)
    inspector.show_legion(legion2)

    gtk.main()
