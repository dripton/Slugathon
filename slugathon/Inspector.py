#!/usr/bin/env python

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import Chit
import creaturedata
import Creature
import Legion
import Marker
import icon
import guiutils
import Player

class Inspector(object):
    """Window to show a legion's contents."""
    def __init__(self, username):
        self.glade = gtk.glade.XML("../glade/showlegion.glade")
        self.widget_names = ["show_legion_window", "marker_hbox", "chits_hbox",
          "legion_name"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.show_legion_window.set_icon(icon.pixbuf)
        self.show_legion_window.set_title("Inspector - %s" % (username))

        self.legion = None
        self.marker = None
        self.destroyed = False

        self.show_legion_window.connect("delete-event", self.hide_window)


    def show_legion(self, legion):
        self.legion_name.set_text("Legion %s in hex %s" % (legion.markername,
          legion.hexlabel))

        for hbox in [self.marker_hbox, self.chits_hbox]:
            for child in hbox.get_children():
                hbox.remove(child)

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False,
          fill=False)
        self.marker.show()

        # TODO Handle unknown creatures correctly
        playercolor = legion.player.color
        for creature in legion.sorted_creatures():
            chit = Chit.Chit(creature, playercolor, scale=20)
            chit.show()
            self.chits_hbox.add(chit.event_box)

        self.show_legion_window.show()

    def destroy(self, unused):
        self.destroyed = True

    def hide_window(self, event, unused):
        self.show_legion_window.hide()
        return True


if __name__ == "__main__":
    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]

    username = "test"
    player = Player.Player(username, None, None)
    player.color = "Red"
    inspector = Inspector(username)
    inspector.show_legion_window.connect("delete-event", guiutils.exit)

    legion = Legion.Legion(player, "Rd01", creatures, 1)
    inspector.show_legion(legion)

    creatures2 = [Creature.Creature(name) for name in
      ["Angel", "Giant", "Warbear", "Unicorn"]]
    legion2 = Legion.Legion(player, "Rd02", creatures2, 2)
    inspector.show_legion(legion2)

    gtk.main()
