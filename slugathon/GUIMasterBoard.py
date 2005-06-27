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
import Marker
import ShowLegion
import BoardRoot
import Phase
import PickMarker
import SplitLegion

SQRT3 = math.sqrt(3.0)


class GUIMasterBoard(object):

    zope.interface.implements(IObserver)

    def __init__(self, root, board, game=None, username=None, scale=None):
        self.root = root
        self.board = board
        self.username = username

        # XXX This feels like inappropriate coupling, but I haven't thought
        # of a better way to handle the data needed for markers yet.
        self.game = game

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = gtk.DrawingArea()
        black = self.area.get_colormap().alloc_color("black")
        self.area.modify_bg(gtk.STATE_NORMAL, black)
        self.area.set_size_request(self.compute_width(), self.compute_height())
        # TODO Vary font size with scale
        self.area.modify_font(pango.FontDescription("monospace 8"))
        self.root.vbox.pack_start(self.area)
        self.markers = []
        self.guihexes = {}
        self._splitting_legion = None
        for hex1 in self.board.hexes.values():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.area.connect("expose-event", self.area_expose_cb)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.click_cb)
        self.root.show_all()

    def area_expose_cb(self, area, event):
        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        self.update_gui(gc, style)
        return True

    def click_cb(self, area, event):
        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        for marker in self.markers:
            if marker.point_inside((event.x, event.y)):
                print "clicked on", marker, "with button", event.button
                self.clicked_on_marker(area, event, marker)
                return True
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                guihex.toggle_selection()
                self.update_gui(gc, style, [guihex.hex.label])
                return True
        return True

    def clicked_on_marker(self, area, event, marker):
        if event.button >= 2:
            ShowLegion.ShowLegion(self.username, marker.legion,
              marker.legion.player.color, True)
        else: # left button
            phase = self.game.phase
            if phase == Phase.SPLIT:
                legion = marker.legion
                player = legion.player
                # Make sure it's this player's legion and turn.
                if player.name != self.username:
                    return True
                if player != self.game.active_player:
                    return True
                if player.selected_markername:
                    self.split_legion(player, legion)
                else:
                    if not player.markernames:
                        return True
                    self._splitting_legion = legion
                    PickMarker.PickMarker(self.username, self.game.name, 
                      player.markernames, self.picked_marker_presplit)
        return True

    def picked_marker_presplit(self, game_name, username, markername):
        player = self.game.get_player_by_name(username)
        player.pick_marker(markername)
        self.split_legion(player)

    def split_legion(self, player):
        legion = self._splitting_legion
        self._splitting_legion = None
        SplitLegion.SplitLegion(self.username, player, legion,
          self.try_to_split_legion)

    def try_to_split_legion(self, old_legion, new_legion1, new_legion2):
        print "try_to_split_legion", old_legion, new_legion1, new_legion2
        # TODO

    def compute_scale(self):
        """Return the maximum scale that let the board fit on the screen
        
        This is approximate not exact.
        """
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        xscale = math.floor(width / (self.board.hex_width() * 4. + 2))
        # The -3 is a fudge factor to leave room for menus and toolbars.
        yscale = math.floor(height / (self.board.hex_height() * 4 * SQRT3)) - 3
        return int(min(xscale, yscale))

    def compute_width(self):
        return int(math.ceil(self.scale * (self.board.hex_width() * 4 + 2)))

    def compute_height(self):
        return int(math.ceil(self.scale * self.board.hex_height() * 4 * SQRT3))

    def markers_in_hex(self, hexlabel):
        return [marker for marker in self.markers if marker.legion.hexlabel ==
          hexlabel]

    def _add_missing_markers(self):
        """Add markers for any legions that lack them.

        Return a list of new markernames.
        """
        result = []
        for legion in self.game.gen_all_legions():
            if legion.markername not in (marker.name for marker in 
              self.markers):
                result.append(legion.markername)
                marker = Marker.Marker(legion, self.scale)
                self.markers.append(marker)
        return result

    def _compute_marker_locations(self, hex1):
        mih = self.markers_in_hex(hex1)
        num = len(mih)
        assert 1 <= num <= 3
        guihex = self.guihexes[hex1]
        chit_scale = self.markers[0].chit_scale
        base_location = (guihex.center[0] - chit_scale / 2,
          guihex.center[1] - chit_scale / 2)

        if num == 1:
            mih[0].location = base_location
        elif num == 2:
            mih[0].location = (base_location[0] - chit_scale / 4,
              base_location[1] - chit_scale / 4)
            mih[1].location = (base_location[0] + chit_scale / 4,
              base_location[1] + chit_scale / 4)
        else:
            mih[0].location = (base_location[0] - chit_scale / 2,
              base_location[1] - chit_scale / 2)
            mih[1].location = base_location
            mih[2].location = (base_location[0] + chit_scale / 2,
              base_location[1] + chit_scale / 2)

    def _render_marker(self, marker, gc):
        drawable = self.area.window
        drawable.draw_pixbuf(gc, marker.pixbuf, 0, 0,
          int(round(marker.location[0])), int(round(marker.location[1])),
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

    def draw_markers(self, gc, style):
        if not self.game:
            return
        self._add_missing_markers()
        if not self.markers:
            return
        hexes_done = set()
        for marker in self.markers:
            hexlabel = marker.hexlabel
            if hexlabel in hexes_done:
                continue
            hexes_done.add(hexlabel)
            self._compute_marker_locations(hexlabel)
            mih = self.markers_in_hex(hexlabel)
            for marker in mih:
                self._render_marker(marker, gc)


    def update_gui(self, gc, style, hexlabels=None):
        if hexlabels is not None:
            guihexes = [self.guihexes[hl] for hl in hexlabels]
        else:
            guihexes = self.guihexes.values()
        for guihex in guihexes:
            guihex.update_gui(gc, style)
        self.draw_markers(gc, style)

    def update(self, observed, action):
        print "GUIMasterBoard.update", self, observed, action
        if isinstance(action, Action.CreateStartingLegion):
            player = self.game.get_player_by_name(action.playername)
            legion = player.legions.values()[0]
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [legion.hexlabel])


if __name__ == "__main__":
    root = BoardRoot.BoardRoot("player")
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(root, board)
    # Allow exiting with control-C, unlike mainloop()
    while True:
        gtk.main_iteration()
