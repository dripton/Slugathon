#!/usr/bin/env python 

import sys
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import Chit
import Marker
import creaturedata
import Creature
import Legion
import Player
import icon
import guiutils


class SplitLegion(object):
    """Dialog to split a legion."""
    def __init__(self, username, player, legion):
        print "SplitLegion.__init__", username, player, legion
        self.glade = gtk.glade.XML("../glade/splitlegion.glade")
        self.widgets = ["split_legion_dialog", "old_marker_hbox", 
          "old_chits_hbox", "new_marker_hbox", "new_chits_hbox",
          "legion_name"]
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.split_legion_dialog.set_icon(icon.pixbuf)
        self.split_legion_dialog.set_title("SplitLegion - %s" % (username))

        self.legion_name.set_text("Splitting legion %s in hex %s" % (
          legion.markername, legion.hexlabel))

        self.old_marker = Marker.Marker(legion, scale=20)
        self.old_marker_hbox.pack_start(self.old_marker.image, expand=False,
          fill=False)
        self.old_marker.show()

        self.new_legion = Legion.Legion(player, player.selected_markername, [],
          legion.hexlabel)
        self.new_marker = Marker.Marker(self.new_legion, scale=20)
        self.new_marker_hbox.pack_start(self.new_marker.image, expand=False,
          fill=False)
        self.new_marker.show()

        # TODO Handle unknown creatures correctly
        for creature in legion.creatures:
            chit = Chit.Chit(creature, playercolor, scale=20)
            chit.show()
            self.old_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button_press_event", self.cb_click)
            
        self.split_legion_dialog.show()


    def cb_click(self, widget, event):
        """Move the clicked-on Chit's EventBox to the other hbox."""
        if widget in self.old_chits_hbox.get_children():
            prev = self.old_chits_hbox
            next = self.new_chits_hbox
        else:
            prev = self.new_chits_hbox
            next = self.old_chits_hbox
        prev.remove(widget)
        next.pack_start(widget, expand=False, fill=False)


if __name__ == "__main__":
    creatures = [Creature.Creature(name) for name in 
      creaturedata.starting_creature_names]
    
    username = "test"
    playercolor = "Red"
    player = Player.Player(username, "Game1", 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    player.selected_markername = "Rd02"
    SplitLegion = SplitLegion(username, player, legion)
    SplitLegion.split_legion_dialog.connect("destroy", guiutils.die)

    gtk.main()
