#!/usr/bin/env python

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import pango
import sys
import math
import zope.interface

import GUIMasterHex
import MasterBoard
import guiutils
from Observer import IObserver
import Action
import Game

SQRT3 = math.sqrt(3.0)


class GUIMasterBoard(object):

    zope.interface.implements(IObserver)

    def __init__(self, root, board, game=None, scale=15):
        self.root = root
        self.board = board

        # XXX This feels like inappropriate coupling, but I haven't thought
        # of a better way to handle the data needed for markers yet.
        self.game = game

        self.scale = scale
        self.area = gtk.DrawingArea()
        black = self.area.get_colormap().alloc_color("black")
        self.area.modify_bg(gtk.STATE_NORMAL, black)
        self.area.set_size_request(self.compute_width(), self.compute_height())
        # TODO Vary font size with scale
        self.area.modify_font(pango.FontDescription("monospace 8"))
        self.root.add(self.area)
        self.guihexes = {}
        for hex1 in self.board.hexes.values():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.area.connect("expose-event", self.area_expose_cb)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.click_cb)
        self.area.show()
        self.root.show()

    def area_expose_cb(self, area, event):
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        for guihex in self.guihexes.values():
            guihex.update_gui(self.gc, self.style)
        return True

    def click_cb(self, area, event):
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                guihex.toggle_selection()
                guihex.update_gui(self.gc, self.style)
                break
        return True

    def compute_width(self):
        return int(round(self.scale * (self.board.hex_width() * 4 + 2)))

    def compute_height(self):
        return int(round(self.scale * self.board.hex_height() * 4 * SQRT3))

    def update(self, observed, action):
        print "GUIMasterBoard.update", self, observed, action
        if isinstance(action, Action.CreateStartingLegion):
            guihex.update_gui(self.gc, self.style)


def quit(unused):
    sys.exit()

if __name__ == "__main__":
    root = gtk.Window()
    root.set_title("Slugathon - MasterBoard")
    root.connect("destroy", quit)

    pixbuf = gtk.gdk.pixbuf_new_from_file("../images/creature/Colossus.png")
    root.set_icon(pixbuf)

    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(root, board)
    # Allow exiting with control-C, unlike mainloop()
    while True:
        gtk.main_iteration()
