#!/usr/bin/env python

import math
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import pango
from zope.interface import implements

from Observer import IObserver
import BattleMap
import icon
import guiutils
import GUIBattleHex

SQRT3 = math.sqrt(3.0)


class GUIBattleMap(gtk.Window):
    """GUI representation of a battlemap.

    We spin the map so that the attacker's entry side is always on the left.

    entry_side 1:

               D6 
            E5    C5 
    A    F4    D5    B4       D
    T       E4    C4    A3    E
    T    F3    D4    B3       F
    A       E3    C3    A2    E
    C    F2    D3    B2       N
    K       E2    C2    A1    D
    E    F1    D2    B1       E
    R       E1    C1          R
               D1
               
    entry_side 3:

               A1 
            A2    B1 
    A    A3    B2    C1       D
    T       B3    C2    D1    E
    T    B4    C3    D2       F
    A       C4    D3    E1    E
    C    C5    D4    E2       N
    K       D5    E3    F1    D
    E    D6    E4    F2       E
    R       E5    F3          R
               F4
               
    entry_side 5:

               F1 
            E1    F2 
    A    D1    E2    F3       D
    T       D2    E3    F4    E
    T    C1    D3    E4       F
    A       C2    D4    E5    E
    C    B1    C3    D5       N
    K       B2    C5    D6    D
    E    A1    B3    C5       E
    R       A2    B4          R
               A3

    """

    implements(IObserver)

    def __init__(self, battlemap, entry_side, user=None, username=None, 
      scale=None):
        gtk.Window.__init__(self)

        self.battlemap = battlemap
        self.entry_side = entry_side
        self.user = user
        self.username = username

        self.set_icon(icon.pixbuf)
        self.set_title("Slugathon - BattleMap - %s" % self.username)
        self.connect("destroy", guiutils.exit)

        self.vbox = gtk.VBox()
        self.add(self.vbox)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = gtk.DrawingArea()
        # TODO Vary background color by terrain type?
        white = self.area.get_colormap().alloc_color("white")
        self.area.modify_bg(gtk.STATE_NORMAL, white)
        self.area.set_size_request(self.compute_width(), self.compute_height())
        # TODO Vary font size with scale
        self.area.modify_font(pango.FontDescription("monospace 8"))
        self.vbox.pack_start(self.area)
        self.guihexes = {}
        for hex1 in self.battlemap.hexes.itervalues():
            self.guihexes[hex1.label] = GUIBattleHex.GUIBattleHex(hex1, self)
        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.cb_click)
        self.show_all()


    def compute_scale(self):
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        # The -2 is a fudge factor to leave room on the sides.
        xscale = math.floor(width / (2 * self.battlemap.hex_width())) - 2
        # The -3 is a fudge factor for menus and toolbars.
        yscale = math.floor(height / (2 * SQRT3 * 
          self.battlemap.hex_height())) - 3
        return int(min(xscale, yscale))

    def compute_width(self):
        """Return the width of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_width() * 4)) 

    def compute_height(self):
        """Return the height of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_height() * 2 * 
          SQRT3))

    def cb_area_expose(self, area, event):
        self.update_gui()
        return True

    def cb_click(self, area, event):
        for guihex in self.guihexes.itervalues():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                self.clicked_on_hex(area, event, guihex)
                return True
        self.clicked_on_background(area, event)
        return True

    def clicked_on_background(self, area, event):
        pass

    def clicked_on_hex(self, area, event, guihex):
        guihex.toggle_selection()
        self.update_gui([guihex.battlehex.label])

    def update_gui(self, hexlabels=None):
        gc = self.area.get_style().fg_gc[gtk.STATE_NORMAL]
        if hexlabels is None:
            guihexes = self.guihexes.itervalues()
        else:
            guihexes = set(self.guihexes[hexlabel] for hexlabel in hexlabels)
        for guihex in guihexes:
            guihex.update_gui(gc)

    def update(self, observed, action):
        print "GUIBattleMap.update", observed, action


if __name__ == "__main__":
    import random
    import battlemapdata
    import sys
    if len(sys.argv) > 1:
        terrain = sys.argv[1].title()
    else:
        terrain = random.choice(battlemapdata.data.keys())
    battlemap = BattleMap.BattleMap(terrain)
    if terrain == "Tower":
        entry_side = 3
    else:
        entry_side = random.choice([1, 3, 5])
    guimap = GUIBattleMap(battlemap, entry_side)
    while True:
        gtk.main_iteration()
