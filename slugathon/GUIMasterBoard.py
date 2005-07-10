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

import GUIMasterHex
import MasterBoard
import guiutils
from Observer import IObserver
import Action
import Marker
import ShowLegion
import Phase
import PickMarker
import SplitLegion
import About
import icon
import Die


SQRT3 = math.sqrt(3.0)


ui_string = """<ui>
  <menubar name="Menubar">
    <menu action="GameMenu">
      <menuitem action="Quit"/>
    </menu>
    <menu action="PhaseMenu">
      <menuitem action="Done"/>
      <menuitem action="Undo"/>
      <menuitem action="Redo"/>
      <separator/>
      <menuitem action="Mulligan"/>
    </menu>
    <menu action="HelpMenu">
      <menuitem action="About"/>
    </menu>
  </menubar>
  <toolbar name="Toolbar">
    <toolitem action="Done"/>
    <toolitem action="Undo"/>
    <toolitem action="Redo"/>
    <separator/>
    <toolitem action="Mulligan"/>
  </toolbar>
</ui>"""


class GUIMasterBoard(gtk.Window):

    zope.interface.implements(IObserver)

    def __init__(self, board, game=None, user=None, username=None, 
      scale=None):
        gtk.Window.__init__(self)

        self.board = board
        self.user = user
        self.username = username
        # XXX This feels like inappropriate coupling
        self.game = game

        self.set_icon(icon.pixbuf)
        self.set_title("Slugathon - Masterboard - %s" % self.username)
        self.connect("destroy", guiutils.die)

        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.create_ui()
        self.vbox.pack_start(self.ui.get_widget("/Menubar"), False, False, 0)
        self.vbox.pack_start(self.ui.get_widget("/Toolbar"), False, False, 0)

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
        self.vbox.pack_start(self.area)
        self.markers = []
        self.guihexes = {}
        self._splitting_legion = None
        for hex1 in self.board.hexes.values():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.cb_click)
        self.show_all()

    def create_ui(self):
        ag = gtk.ActionGroup("MasterActions")
        # TODO confirm quit
        actions = [
          ("GameMenu", None, "_Game"),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program",
            guiutils.die),
          ("PhaseMenu", None, "_Phase"),
          ("Done", gtk.STOCK_APPLY, "_Done", "d", "Done", self.cb_done),
          ("Undo", gtk.STOCK_UNDO, "_Undo", "u", "Undo", self.cb_undo),
          ("Redo", gtk.STOCK_REDO, "_Redo", "r", "Redo", self.cb_redo),
          ("Mulligan", gtk.STOCK_MEDIA_REWIND, "_Mulligan", "m", "Mulligan", 
            self.cb_mulligan),
          ("HelpMenu", None, "_Help"),
          ("About", gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)
        self.add_accel_group(self.ui.get_accel_group())

    def cb_area_expose(self, area, event):
        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        self.update_gui(gc, style)
        return True

    def cb_click(self, area, event):
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
                self.update_gui(gc, style, [guihex.masterhex.label])
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
                elif player != self.game.active_player:
                    return True
                # Ensure that the legion can legally be split.
                elif not legion.can_be_split(self.game.turn):
                    return True
                elif player.selected_markername:
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
        def1 = self.user.callRemote("split_legion", self.game.name,
          new_legion1.markername, new_legion2.markername, 
          new_legion1.creature_names(), new_legion2.creature_names())
        # TODO callbacks

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
        elif num == 3:
            mih[0].location = (base_location[0] - chit_scale / 2,
              base_location[1] - chit_scale / 2)
            mih[1].location = base_location
            mih[2].location = (base_location[0] + chit_scale / 2,
              base_location[1] + chit_scale / 2)
        else:
            raise AssertionError("invalid number of markers in hex")

    def _render_marker(self, marker, gc):
        drawable = self.area.window
        drawable.draw_pixbuf(gc, marker.pixbuf, 0, 0,
          int(round(marker.location[0])), int(round(marker.location[1])),
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

    def draw_markers(self, gc, style):
        if not self.game:
            return
        self._add_missing_markers()
        hexlabels = set((marker.hexlabel for marker in self.markers))
        for hexlabel in hexlabels:
            self._compute_marker_locations(hexlabel)
            mih = self.markers_in_hex(hexlabel)
            # Draw in reverse order so that the markers that come earlier
            # in self.markers are on top.
            for marker in reversed(mih):
                self._render_marker(marker, gc)

    def draw_movement_die(self, gc, style):
        try:
            roll = self.game.active_player.movement_roll
        except AttributeError:
            return
        if not roll:
            return
        die = Die.Die(roll, scale=self.scale)
        drawable = self.area.window
        drawable.draw_pixbuf(gc, die.pixbuf, 0, 0, 0, 0,
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)


    def update_gui(self, gc, style, hexlabels=None):
        if hexlabels is not None:
            guihexes = [self.guihexes[hl] for hl in hexlabels]
        else:
            guihexes = self.guihexes.values()
        for guihex in guihexes:
            guihex.update_gui(gc, style)
        self.draw_markers(gc, style)
        self.draw_movement_die(gc, style)


    def cb_done(self, action):
        print "done", action
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            if self.game.phase == Phase.SPLIT:
                if player.can_exit_split_phase():
                    def1 = self.user.callRemote("done_with_splits", 
                      self.game.name)

    def cb_mulligan(self, action):
        print "mulligan", action
        player = self.game.get_player_by_name(self.username)
        if self.game.can_take_mulligan(player):
            def1 = self.user.callRemote("take_mulligan", self.game.name)

    def cb_about(self, action):
        print "about", action
        about = About.About()

    # TODO
    def cb_undo(self, action):
        print "undo", action

    def cb_redo(self, action):
        print "redo", action


    def update(self, observed, action):
        print "GUIMasterBoard.update", self, observed, action
        if isinstance(action, Action.CreateStartingLegion):
            player = self.game.get_player_by_name(action.playername)
            legion = player.legions.values()[0]
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [legion.hexlabel])
        elif isinstance(action, Action.SplitLegion):
            player = self.game.get_player_by_name(action.playername)
            parent = player.legions[action.parent_markername]
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [parent.hexlabel])
        elif isinstance(action, Action.RollMovement):
            player = self.game.get_player_by_name(action.playername)
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style)


if __name__ == "__main__":
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(board)
    # Allow exiting with control-C, unlike mainloop()
    while True:
        gtk.main_iteration()
