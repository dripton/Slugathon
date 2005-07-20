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
import Game
import PickRecruit


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
        self.selected_marker = None

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
                self.clicked_on_hex(area, event, guihex)
                return True
        self.clicked_on_background(area, event)
        return True

    def _all_teleports(self, moves):
        """Return True iff all the move tuples in moves are teleports"""
        for move in moves:
            if move[1] != Game.TELEPORT:
                return False
        return True

    def clicked_on_background(self, area, event):
        """The user clicked on the board outside a hex or marker."""
        game = self.game
        if game:
            if game.phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif game.phase == Phase.MOVE:
                self.selected_marker = None
                self.highlight_unmoved_legions()
            elif game.phase == Phase.FIGHT:
                self.highlight_engagements()
            elif self.game.phase == Phase.MUSTER:
                self.highlight_recruits()

    def clicked_on_hex(self, area, event, guihex):
        repaint_hexlabels = set()
        if not self.game:
            guihex.toggle_selection()
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [guihex.masterhex.label])
        elif event.button == 1:
            phase = self.game.phase
            if phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif phase == Phase.MOVE and self.selected_marker:
                if guihex.selected:
                    legion = self.selected_marker.legion
                    hexlabel = guihex.masterhex.label
                    moves = self.game.find_all_moves(legion, self.board.hexes[
                      legion.hexlabel], legion.player.movement_roll)
                    hexmoves = [m for m in moves if m[0] == hexlabel]
                    # TODO if choice between titan teleport and normal, pick
                    teleport = self._all_teleports(hexmoves)
                    # TODO if >1 entry side and enemy in hex, pick
                    if teleport:
                        entry_side = 1
                        # TODO if >1 lord type and tower teleport, pick
                        teleporting_lord = legion.first_lord_name()
                    else:
                        entry_side = hexmoves[0][1]
                        teleporting_lord = None
                    def1 = self.user.callRemote("move_legion", self.game.name,
                      legion.markername, guihex.masterhex.label, entry_side,
                      teleport, teleporting_lord)
                    def1.addErrback(self.failure)
                self.selected_marker = None
                self.unselect_all()
            elif phase == Phase.MOVE:
                self.highlight_unmoved_legions()
            elif phase == Phase.MUSTER:
                self.highlight_recruits()


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
            elif phase == Phase.MOVE:
                self.unselect_all()
                legion = marker.legion
                if legion.moved:
                    moves = []
                else:
                    moves = self.game.find_all_moves(legion, self.board.hexes[
                      legion.hexlabel], legion.player.movement_roll)
                repaint_hexlabels = set()
                if moves:
                    self.selected_marker = marker
                    for move in moves:
                        hexlabel = move[0]
                        guihex = self.guihexes[hexlabel]
                        guihex.selected = True
                        repaint_hexlabels.add(hexlabel)
                style = self.area.get_style()
                gc = style.fg_gc[gtk.STATE_NORMAL]
                self.update_gui(gc, style, repaint_hexlabels)
            elif phase == Phase.MUSTER:
                self.unselect_all()
                legion = marker.legion
                if not legion.recruited:
                    masterhex = self.board.hexes[legion.hexlabel]
                    caretaker = self.game.caretaker
                    recruit_names = legion.available_recruits(masterhex,
                      caretaker)
                    if recruit_names:
                        PickRecruit.PickRecruit(self.username, legion.player,
                          legion, masterhex, caretaker, self.picked_recruit)
                self.highlight_recruits()
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
        def1 = self.user.callRemote("split_legion", self.game.name,
          new_legion1.markername, new_legion2.markername, 
          new_legion1.creature_names(), new_legion2.creature_names())
        def1.addErrback(self.failure)

    def picked_recruit(self, legion, creature):
        """Callback from PickRecruit"""
        legion.recruit(creature)

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
        for legion in self.game.all_legions():
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

    def draw_markers(self, gc):
        if not self.game:
            return
        self._add_missing_markers()
        hexlabels = set((marker.legion.hexlabel for marker in self.markers))
        for hexlabel in hexlabels:
            self._compute_marker_locations(hexlabel)
            mih = self.markers_in_hex(hexlabel)
            # Draw in reverse order so that the markers that come earlier
            # in self.markers are on top.
            for marker in reversed(mih):
                self._render_marker(marker, gc)

    def draw_movement_die(self, gc):
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
        if hexlabels is None:
            guihexes = self.guihexes.values()
        else:
            # Also redraw neighbors, to clean up chit overdraw.
            guihexes = set()
            for hexlabel in hexlabels:
                guihexes.add(self.guihexes[hexlabel])
                masterhex = self.board.hexes[hexlabel]
                for neighbor in masterhex.neighbors:
                    if neighbor:
                        guihexes.add(self.guihexes[neighbor.label])
        for guihex in guihexes:
            guihex.update_gui(gc, style)
        self.draw_markers(gc)
        self.draw_movement_die(gc)

    def unselect_all(self):
        repaint_hexlabels = set()
        for guihex in self.guihexes.values():
            if guihex.selected:
                guihex.selected = False
                repaint_hexlabels.add(guihex.masterhex.label)
        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        self.update_gui(gc, style, repaint_hexlabels)

    def highlight_tall_legions(self):
        """Highlight all hexes containing a legion of height 7 or more
        belonging to the active, current player."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.values():
                if len(legion) >= 7:
                    hexlabels.add(legion.hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, hexlabels)

    def highlight_unmoved_legions(self):
        """Highlight all hexes containing an unmoved legion belonging to the
        active, current player."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.values():
                if not legion.moved:
                    hexlabels.add(legion.hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, hexlabels)
                
    def highlight_engagements(self):
        """Highlight all hexes with engagements."""
        self.unselect_all()
        hexlabels = self.game.engagement_hexlabels()
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            guihex.selected = True
        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        self.update_gui(gc, style, hexlabels)

    def highlight_recruits(self):
        """Highlight all hexes in which the active player can recruit."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.values():
                hexlabel = legion.hexlabel
                if (legion.moved and not legion.recruited and 
                  legion.available_recruits(self.game.board.hexes[hexlabel],
                    self.game.caretaker)):
                      hexlabels.add(hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, hexlabels)

    def cb_done(self, action):
        print "done", action
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            if self.game.phase == Phase.SPLIT:
                if player.can_exit_split_phase():
                    def1 = self.user.callRemote("done_with_splits", 
                      self.game.name)
                    def1.addErrback(self.failure)
            elif self.game.phase == Phase.MOVE:
                if player.can_exit_move_phase(self.game):
                    def1 = self.user.callRemote("done_with_moves",
                      self.game.name)
                    def1.addErrback(self.failure)

    def cb_mulligan(self, action):
        print "mulligan", action
        player = self.game.get_player_by_name(self.username)
        if player.can_take_mulligan(self.game):
            def1 = self.user.callRemote("take_mulligan", self.game.name)
            def1.addErrback(self.failure)

    def cb_about(self, action):
        About.About()

    # TODO
    def cb_undo(self, action):
        print "undo", action

    def cb_redo(self, action):
        print "redo", action

    def failure(self, arg):
        print "GUIMasterBoard.failure", arg

    def update(self, observed, action):
        print "GUIMasterBoard.update", self, observed, action
        if isinstance(action, Action.CreateStartingLegion):
            player = self.game.get_player_by_name(action.playername)
            legion = player.legions.values()[0]
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [legion.hexlabel])
            self.highlight_tall_legions()
        elif isinstance(action, Action.SplitLegion):
            player = self.game.get_player_by_name(action.playername)
            parent = player.legions[action.parent_markername]
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [parent.hexlabel])
        elif isinstance(action, Action.RollMovement):
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, [])
            if action.playername == self.username:
                self.highlight_unmoved_legions()
        elif isinstance(action, Action.MoveLegion):
            self.selected_marker = None
            self.unselect_all()
            legion = self.game.find_legion(action.markername)
            repaint_hexlabels = set([legion.hexlabel, 
              legion.previous_hexlabel])
            style = self.area.get_style()
            gc = style.fg_gc[gtk.STATE_NORMAL]
            self.update_gui(gc, style, repaint_hexlabels)
        elif isinstance(action, Action.DoneMoving):
            if self.game.phase == Phase.FIGHT:
                self.highlight_engagements()
            elif self.game.phase == Phase.MUSTER:
                self.highlight_recruits()
        elif isinstance(action, Action.RecruitCreature):
            self.highlight_recruits()


if __name__ == "__main__":
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(board)
    # Allow exiting with control-C, unlike mainloop()
    while True:
        gtk.main_iteration()
