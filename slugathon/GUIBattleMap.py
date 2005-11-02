#!/usr/bin/env python

import math
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import pango
import zope.interface

from Observer import IObserver
import BattleMap
import icon
import guiutils


class GUIBattleMap(gtk.Window):
    """GUI representation of a battlemap.

    We spin the map so that the attacker's entry side is always on the left.

               *
            *     *
    A    *     *     *       D
    T       *     *     *    E
    T    *     *     *       F
    A       *     *     *    E
    C    *     *     *       N
    K       *     *     *    D
    E    *     *     *       E
    R       *     *          R
               *
    """

    zope.interface.implements(IObserver)

    def __init__(self, battlemap, user=None, username=None, scale=None):
        gtk.Window.__init__(self)

        self.battlemap = battlemap
        self.user = user
        self.username = username

        self.set_icon(icon.pixbuf)
        self.set_title("Slugathon - BattleMap - %s" % self.username)
        self.connect("destroy", guiutils.die)

        if scale is None:
            self.scale = self.compute_scale
        else:
            self.scale = scale
        self.area = gtk.DrawingArea()
        # TODO Vary background color by terrain type?
        white = self.area.get_colormap().alloc_color("white")
        self.area.modify_bg(gtk.STATE_NORMAL, white)
        self.area.set_size_request(self.compute_width(), self.compute_height())
        # TODO Vary font size with scale
        self.area.modify_font(pango.FontDescription("monospace 8"))


    def compute_scale(self):
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()

    def compute_width(self):
        """Return the width of the map in pixels."""

    def compute_height(self):
        """Return the height of the map in pixels."""


if __name__ == "__main__":
    battlemap = BattleMap.BattleMap("Brush")
    guimap = GUIBattleMap(battlemap)
    while True:
        gtk.main_iteration()
