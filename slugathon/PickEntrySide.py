#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import math
import random
from sys import maxint, argv

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor

import gtk

import BattleMap
import icon
import guiutils
import GUIBattleHex
import battlemapdata
import prefs


SQRT3 = math.sqrt(3.0)

hexlabel_to_entry_side = {
    "F1": 1,
    "F2": 1,
    "F3": 1,
    "F4": 1,
    "A3": 3,
    "B4": 3,
    "C5": 3,
    "D6": 3,
    "A1": 5,
    "B1": 5,
    "C1": 5,
    "D1": 5,
}


class PickEntrySide(gtk.Window):
    """Dialog to pick a masterhex entry side."""

    def __init__(self, terrain, entry_sides, callback, username=None, 
      scale=None):
        gtk.Window.__init__(self)

        # We always orient the map as if for entry side 5.
        self.battlemap = BattleMap.BattleMap(terrain, 5)
        self.entry_sides = entry_sides
        self.callback = callback
        self.username = username

        self.set_icon(icon.pixbuf)
        self.set_title("PickEntrySide - Slugathon - %s" % self.username)

        self.vbox = gtk.VBox()
        self.add(self.vbox)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = gtk.DrawingArea()
        self.area.set_size_request(self.compute_width(), self.compute_height())

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

        self.vbox.pack_start(self.area)

        self.guihexes = {}
        for hex1 in self.battlemap.hexes.itervalues():
            # Don't show entrances.
            if hex1.label not in ["ATTACKER", "DEFENDER"]:
                self.guihexes[hex1.label] = GUIBattleHex.GUIBattleHex(hex1,
                  self)
        self.repaint_hexlabels = set()
        # Hexes that need their bounding rectangles cleared, too.
        # This fixes chits.
        self.clear_hexlabels = set()

        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)

        self.connect("destroy", self.callback_with_none)

        for hexlabel, entry_side in hexlabel_to_entry_side.iteritems():
            if entry_side in self.entry_sides:
                self.guihexes[hexlabel].selected = True
        self.show_all()


    def compute_scale(self):
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        # Fudge factor to leave room on the sides.
        xscale = math.floor(width / (2 * self.battlemap.hex_width())) - 5
        # Fudge factor for menus and toolbars.
        yscale = math.floor(height / (2 * SQRT3 *
          self.battlemap.hex_height())) - 11
        return int(min(xscale, yscale))

    def compute_width(self):
        """Return the width of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_width() * 3.2))

    def compute_height(self):
        """Return the height of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_height() * 2 *
          SQRT3))

    def cb_area_expose(self, area, event):
        self.update_gui(event=event)
        return True

    def cb_click(self, area, event):
        for guihex in self.guihexes.itervalues():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                self.clicked_on_hex(area, event, guihex)
                return True
        return True

    def clicked_on_hex(self, area, event, guihex):
        if guihex.selected:
            entry_side = hexlabel_to_entry_side[guihex.battlehex.label]
            self.callback(entry_side)
            self.destroy()

    def bounding_rect_for_hexlabels(self, hexlabels):
        """Return the minimum bounding rectangle that encloses all
        GUIMasterHexes whose hexlabels are given, as a tuple
        (x, y, width, height)
        """
        min_x = maxint
        max_x = -maxint
        min_y = maxint
        max_y = -maxint
        for hexlabel in hexlabels:
            try:
                guihex = self.guihexes[hexlabel]
                x, y, width, height = guihex.bounding_rect
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
            except KeyError:   # None check
                pass
        width = max_x - min_x
        height = max_y - min_y
        return min_x, min_y, width, height

    def update_gui(self, event=None):
        """Repaint the amount of the GUI that needs repainting.

        If event is not None, then that's the dirty rectangle.
        If event is None, then we compute the dirty rectangle from
        self.repaint_hexlabels.
        """
        if event is None:
            if not self.repaint_hexlabels:
                return
            clip_rect = self.bounding_rect_for_hexlabels(
              self.repaint_hexlabels)
        else:
            clip_rect = event.area
        if not self.area or not self.area.window:
            return
        ctx = self.area.window.cairo_create()
        ctx.set_line_width(round(0.2 * self.scale))
        ctx.rectangle(*clip_rect)
        ctx.clip()
        # white background, only when we get an event
        if event is not None:
            ctx.set_source_rgb(1, 1, 1)
            width, height = self.area.size_request()
            ctx.rectangle(0, 0, width, height)
            ctx.fill()
        for hexlabel in self.clear_hexlabels:
            ctx.set_source_rgb(1, 1, 1)
            guihex = self.guihexes[hexlabel]
            x, y, width, height = guihex.bounding_rect
            ctx.rectangle(x, y, width, height)
            ctx.fill()
        for guihex in self.guihexes.itervalues():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)
        self.repaint_hexlabels.clear()
        self.clear_hexlabels.clear()

    def repaint(self, hexlabels=None):
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)

    def callback_with_none(self, *args):
        """Called if the window is destroyed."""
        self.callback(None)


if __name__ == "__main__":
    entry_side = None
    if len(argv) > 1:
        terrain = argv[1].title()
    else:
        terrain = random.choice(battlemapdata.data.keys())

    def my_callback(choice):
        print "chose entry side", choice
        guiutils.exit()

    pick_entry_side = PickEntrySide(terrain, set([1, 3, 5]), my_callback)
    reactor.run()
