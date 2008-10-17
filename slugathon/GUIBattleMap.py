#!/usr/bin/env python

import math
import random
import sys

import gtk
import pango
from zope.interface import implements

from Observer import IObserver
import BattleMap
import icon
import guiutils
import GUIBattleHex
import battlemapdata
import Chit


SQRT3 = math.sqrt(3.0)


class GUIBattleMap(gtk.Window):
    """GUI representation of a battlemap."""

    implements(IObserver)

    def __init__(self, battlemap, game=None, user=None, username=None, 
      scale=None):
        gtk.Window.__init__(self)

        self.battlemap = battlemap
        self.game = game
        self.user = user
        self.username = username
        self.chits = []

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
        return int(math.ceil(self.scale * self.battlemap.hex_width() * 3.2)) 

    def compute_height(self):
        """Return the height of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_height() * 2 * 
          SQRT3))

    def cb_area_expose(self, area, event):
        self.update_gui()
        return True

    def cb_click(self, area, event):
        for chit in self.chits:
            if chit.point_inside((event.x, event.y)):
                self.clicked_on_chit(chit)
                return True
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

    def clicked_on_chit(self, chit):
        print "clicked on chit", chit, chit.creature

    def _add_missing_chits(self):
        """Add chits for any creatures that lack them."""
        chit_creatures = set(chit.creature for chit in self.chits)
        battle = self.game.battle
        for (legion, rotate) in [ 
          (battle.attacker_legion, gtk.gdk.PIXBUF_ROTATE_CLOCKWISE), 
          (battle.defender_legion, gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)]:
            for creature in legion.creatures:
                if creature not in chit_creatures:
                    chit = Chit.Chit(creature, legion.player.color, 
                      self.scale / 2, rotate=rotate)
                    self.chits.append(chit)

    def _compute_chit_locations(self, hexlabel):
        chits = self.chits_in_hex(hexlabel)
        num = len(chits)
        guihex = self.guihexes[hexlabel]
        chit_scale = self.chits[0].chit_scale
        bl = (guihex.center[0] - chit_scale / 2, guihex.center[1] - 
          chit_scale / 2)

        if num == 1:
            chits[0].location = bl
        elif num == 2:
            chits[0].location = (bl[0], bl[1] - chit_scale / 2)
            chits[1].location = (bl[0], bl[1] + chit_scale / 2)
        elif num == 3:
            chits[0].location = (bl[0], bl[1] - chit_scale)
            chits[1].location = bl
            chits[2].location = (bl[0], bl[1] + chit_scale)
        elif num == 4:
            chits[0].location = (bl[0], bl[1] - 3 * chit_scale / 2)
            chits[1].location = (bl[0], bl[1] - chit_scale / 2)
            chits[2].location = (bl[0], bl[1] + chit_scale / 2)
            chits[3].location = (bl[0], bl[1] + 3 * chit_scale / 2)
        elif num == 5:
            chits[0].location = (bl[0], bl[1] - 2 * chit_scale)
            chits[1].location = (bl[0], bl[1] - chit_scale)
            chits[2].location = bl
            chits[3].location = (bl[0], bl[1] + chit_scale)
            chits[4].location = (bl[0], bl[1] + 2 * chit_scale)
        elif num == 6:
            chits[0].location = (bl[0], bl[1] - 5 * chit_scale / 2)
            chits[1].location = (bl[0], bl[1] - 3 * chit_scale / 2)
            chits[2].location = (bl[0], bl[1] - chit_scale / 2)
            chits[3].location = (bl[0], bl[1] + chit_scale / 2)
            chits[4].location = (bl[0], bl[1] + 3 * chit_scale / 2)
            chits[5].location = (bl[0], bl[1] + 5 * chit_scale / 2)
        elif num == 7:
            chits[0].location = (bl[0], bl[1] - 3 * chit_scale)
            chits[1].location = (bl[0], bl[1] - 2 * chit_scale)
            chits[2].location = (bl[0], bl[1] - chit_scale)
            chits[3].location = bl
            chits[4].location = (bl[0], bl[1] + chit_scale)
            chits[5].location = (bl[0], bl[1] + 2 * chit_scale)
            chits[6].location = (bl[0], bl[1] + 3 * chit_scale)
        else:
            raise AssertionError("invalid number of chits in hex")

    def _render_chit(self, chit, gc):
        drawable = self.area.window
        drawable.draw_pixbuf(gc, chit.pixbuf, 0, 0,
          int(round(chit.location[0])), int(round(chit.location[1])),
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

    def chits_in_hex(self, hexlabel):
        return [chit for chit in self.chits 
          if chit.creature.hexlabel == hexlabel]

    def draw_chits(self, gc):
        if not self.game: 
            return
        self._add_missing_chits()
        hexlabels = set([chit.creature.hexlabel for chit in self.chits])
        for hexlabel in hexlabels:
            self._compute_chit_locations(hexlabel)
            chits = self.chits_in_hex(hexlabel)
            for chit in chits:
                self._render_chit(chit, gc)

    def update_gui(self, hexlabels=None):
        gc = self.area.get_style().fg_gc[gtk.STATE_NORMAL]
        gc.line_width = int(round(0.2 * self.scale))
        if hexlabels is None:
            guihexes = self.guihexes.itervalues()
        else:
            guihexes = set(self.guihexes[hexlabel] for hexlabel in hexlabels)
        for guihex in guihexes:
            guihex.update_gui(gc)
        self.draw_chits(gc)

    def update(self, observed, action):
        print "GUIBattleMap.update", observed, action


if __name__ == "__main__":
    entry_side = None
    if len(sys.argv) > 1:
        terrain = sys.argv[1].title()
        if len(sys.argv) > 2:
            entry_side = int(sys.argv[2])
    else:
        terrain = random.choice(battlemapdata.data.keys())
    if entry_side is None:
        if terrain == "Tower":
            entry_side = 5
        else:
            entry_side = random.choice([1, 3, 5])
    battlemap = BattleMap.BattleMap(terrain, entry_side)
    guimap = GUIBattleMap(battlemap)
    gtk.main()
