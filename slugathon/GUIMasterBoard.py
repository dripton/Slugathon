#!/usr/bin/env python

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
import pango
import sys
import math
import GUIMasterHex
import MasterBoard
import guiutils

SQRT3 = math.sqrt(3.0)


class GUIMasterBoard:
    def __init__(self, root, board, scale=15):
        self.root = root
        self.board = board
        self.scale = scale
        self.area = gtk.DrawingArea()
        black = self.area.get_colormap().alloc_color('black')
        self.area.modify_bg(gtk.STATE_NORMAL, black)
        self.area.set_size_request(self.compute_width(), self.compute_height())
        # TODO Vary font size with scale
        self.area.modify_font(pango.FontDescription('monospace 8'))
        self.root.add(self.area)
        self.guihexes = {}
        for hex in self.board.hexes.values():
            guihex = GUIMasterHex.GUIMasterHex(hex, self)
            self.guihexes[hex.label] = guihex
        self.area.connect("expose-event", self.area_expose_cb)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.click_cb)
        self.area.show()
        self.root.show()

    def area_expose_cb(self, area, event):
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        for guihex in self.guihexes.values():
            guihex.update(self.gc, self.style)
        return True

    def click_cb(self, area, event):
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.allPoints):
                guihex.toggleSelection()
                guihex.update(self.gc, self.style)
        return True

    def compute_width(self):
        return self.scale * (self.board.hex_width() * 4 + 2)

    def compute_height(self):
        return self.scale * self.board.hex_height() * 4 * SQRT3


def quit(unused):
    sys.exit()

if __name__ == '__main__':
    root = gtk.Window()
    root.set_title('Slugathon - MasterBoard')
    root.connect("destroy", quit)

    pixbuf = gtk.gdk.pixbuf_new_from_file('../images/Colossus.gif')
    root.set_icon(pixbuf)

    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(root, board)
    # Allow exiting with control-C, unlike mainloop()
    while 1:
        gtk.mainiteration()
