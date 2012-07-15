#!/usr/bin/env python

__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import Chit


class Graveyard(gtk.EventBox):
    """Show a legion's dead creatures."""
    def __init__(self, legion):
        self.legion = legion
        gtk.EventBox.__init__(self)
        gtkcolor = gtk.gdk.color_parse("white")
        self.modify_bg(gtk.STATE_NORMAL, gtkcolor)
        self.hbox = gtk.HBox(spacing=3)
        self.add(self.hbox)

    def update_gui(self):
        playercolor = self.legion.player.color
        for child in self.hbox.get_children():
            self.hbox.remove(child)
        for creature in self.legion.dead_creatures:
            chit = Chit.Chit(creature, playercolor, scale=15)
            self.hbox.pack_start(chit.event_box, expand=False)
        self.show_all()
