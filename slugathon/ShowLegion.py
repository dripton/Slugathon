#!/usr/bin/env python 

import sys
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import Chit
import creaturedata
import Creature
import Legion


class ShowLegion(object):
    """Dialog to show a legion's contents."""
    def __init__(self, username, legion, playercolor):
        print "ShowLegion.__init__", username, legion, playercolor
        self.show_legion_dialog = gtk.Dialog()

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          "../images/creature/Colossus.png")
        self.show_legion_dialog.set_icon(pixbuf)
        self.show_legion_dialog.set_title("ShowLegion - %s" % (username))

        # TODO Handle unknown creatures correctly
        for creature in legion.creatures:
            chit = Chit.Chit(creature, playercolor, scale=20)
            chit.show()
            self.show_legion_dialog.action_area.add(chit.event_box)

        self.show_legion_dialog.show()


def quit(unused):
    sys.exit()

if __name__ == "__main__":
    creatures = [Creature.Creature(name) for name in 
      creaturedata.starting_creature_names]
    
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    username = "test"
    playercolor = "Red"
    showlegion = ShowLegion(username, legion, playercolor)
    showlegion.show_legion_dialog.connect("destroy", quit)

    gtk.main()
