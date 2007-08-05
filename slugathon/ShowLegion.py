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

class ShowLegion(object):
    """Window to show a legion's contents."""
    def __init__(self, username, legion, playercolor, show_marker):
        print "ShowLegion.__init__", username, legion, playercolor
        self.glade = gtk.glade.XML("../glade/showlegion.glade")
        self.widgets = ["show_legion_window", "marker_hbox", "chits_hbox",
          "legion_name"]
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.show_legion_window.set_icon(icon.pixbuf)
        self.show_legion_window.set_title("ShowLegion - %s" % (username))

        self.legion_name.set_text("Legion %s in hex %s" % (legion.markername,
          legion.hexlabel))

        self.marker = None
        if show_marker:
            self.marker = Marker.Marker(legion, True, scale=20)
            self.marker_hbox.pack_start(self.marker.event_box, expand=False,
              fill=False)
            self.marker.show()

        # TODO Handle unknown creatures correctly
        for creature in legion.sorted_creatures():
            chit = Chit.Chit(creature, playercolor, scale=20)
            chit.show()
            self.chits_hbox.add(chit.event_box)

        self.show_legion_window.show()


if __name__ == "__main__":
    creatures = [Creature.Creature(name) for name in 
      creaturedata.starting_creature_names]
    
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    username = "test"
    playercolor = "Red"
    showlegion = ShowLegion(username, legion, playercolor, True)
    showlegion.show_legion_window.connect("destroy", guiutils.exit)

    gtk.main()
