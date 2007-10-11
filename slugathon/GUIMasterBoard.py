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
import Flee
import Inspector
import Creature
import Chit
import Negotiate
import Proposal
import AcquireAngel


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
    """GUI representation of the masterboard."""

    implements(IObserver)

    def __init__(self, board, game=None, user=None, username=None, 
      scale=None):
        gtk.Window.__init__(self)

        self.board = board
        self.user = user
        self.username = username
        self.game = game

        self.set_icon(icon.pixbuf)
        self.set_title("Slugathon - Masterboard - %s" % self.username)
        self.connect("destroy", guiutils.exit)

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
        # list of tuples (Chit, hexlabel)
        self.recruitchits = []
        self._splitting_legion = None
        for hex1 in self.board.hexes.values():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.selected_marker = None
        self.inspector = Inspector.Inspector(self.username)
        self.negotiate = None
        self.proposals = set()

        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button_press_event", self.cb_click)
        self.area.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.area.connect("motion_notify_event", self.cb_motion)
        self.show_all()

    def create_ui(self):
        ag = gtk.ActionGroup("MasterActions")
        # TODO confirm quit
        actions = [
          ("GameMenu", None, "_Game"),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program",
            guiutils.exit),
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
        self.update_gui()
        return True

    def cb_click(self, area, event):
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

    def cb_motion(self, area, event):
        """Callback for mouse motion."""
        for marker in self.markers:
            if marker.point_inside((event.x, event.y)):
                self.inspector.show_legion(marker.legion)
                return True
        return True

    def _all_teleports(self, moves):
        """Return True iff all the move tuples in moves are teleports"""
        for move in moves:
            if move[1] != Game.TELEPORT:
                return False
        return True

    def clicked_on_background(self, area, event):
        """The user clicked on the board outside a hex or marker."""
        if self.game:
            if self.game.phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif self.game.phase == Phase.MOVE:
                self.selected_marker = None
                self.highlight_unmoved_legions()
            elif self.game.phase == Phase.FIGHT:
                self.highlight_engagements()
            elif self.game.phase == Phase.MUSTER:
                self.highlight_recruits()

    def clicked_on_hex(self, area, event, guihex):
        if not self.game:
            guihex.toggle_selection()
            self.update_gui([guihex.masterhex.label])
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
                self.clear_recruitchits()
                self.unselect_all()
                self.highlight_unmoved_legions()
            elif phase == Phase.MOVE:
                self.highlight_unmoved_legions()
            elif phase == Phase.FIGHT:
                if guihex.selected:
                    self.user.callRemote("resolve_engagement", self.game.name,
                      guihex.masterhex.label)
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
                    return
                elif player != self.game.active_player:
                    return
                # Ensure that the legion can legally be split.
                elif not legion.can_be_split(self.game.turn):
                    return
                elif player.selected_markername:
                    self.split_legion(player)
                else:
                    if not player.markernames:
                        return
                    self._splitting_legion = legion
                    PickMarker.PickMarker(self.username, self.game.name, 
                      player.markernames, self.picked_marker_presplit, self)

            elif phase == Phase.MOVE:
                legion = marker.legion
                player = legion.player
                if player.name != self.username:
                    # Not my marker; ignore it and click on the hex
                    guihex = self.guihexes[legion.hexlabel]
                    self.clicked_on_hex(area, event, guihex)
                    return
                self.unselect_all()
                self.clear_recruitchits()
                if legion.moved:
                    moves = []
                else:
                    moves = self.game.find_all_moves(legion, self.board.hexes[
                      legion.hexlabel], player.movement_roll)
                repaint_hexlabels = set()
                if moves:
                    self.selected_marker = marker
                    for move in moves:
                        hexlabel = move[0]
                        guihex = self.guihexes[hexlabel]
                        guihex.selected = True
                        repaint_hexlabels.add(hexlabel)
                        recruitnames = legion.available_recruits(
                          self.board.hexes[hexlabel], self.game.caretaker)
                        if recruitnames:
                            creaturename = recruitnames[-1]
                            recruit = Creature.Creature(creaturename)
                            chit = Chit.Chit(recruit, player.color, 
                              self.scale / 2)
                            chit_scale = chit.chit_scale
                            chit.location = (guihex.center[0] - chit_scale / 2,
                              guihex.center[1] - chit_scale / 2)
                            self.recruitchits.append((chit, hexlabel))
                self.update_gui(repaint_hexlabels)

            elif phase == Phase.FIGHT:
                legion = marker.legion
                guihex = self.guihexes[legion.hexlabel]
                if guihex.selected:
                    self.user.callRemote("resolve_engagement", self.game.name,
                      guihex.masterhex.label)

            elif phase == Phase.MUSTER:
                self.unselect_all()
                legion = marker.legion
                if legion.moved and not legion.recruited and len(legion) < 7:
                    masterhex = self.board.hexes[legion.hexlabel]
                    caretaker = self.game.caretaker
                    recruit_names = legion.available_recruits(masterhex,
                      caretaker)
                    if recruit_names:
                        PickRecruit.PickRecruit(self.username, legion.player,
                          legion, masterhex, caretaker, self.picked_recruit,
                          self)
                self.highlight_recruits()


    def picked_marker_presplit(self, game_name, username, markername):
        player = self.game.get_player_by_name(username)
        player.pick_marker(markername)
        self.split_legion(player)

    def split_legion(self, player):
        legion = self._splitting_legion
        SplitLegion.SplitLegion(self.username, player, legion,
          self.try_to_split_legion, self)

    def try_to_split_legion(self, old_legion, new_legion1, new_legion2):
        def1 = self.user.callRemote("split_legion", self.game.name,
          new_legion1.markername, new_legion2.markername, 
          new_legion1.creature_names(), new_legion2.creature_names())
        def1.addErrback(self.failure)

    def picked_recruit(self, legion, creature):
        """Callback from PickRecruit"""
        def1 = self.user.callRemote("recruit_creature", self.game.name,
          legion.markername, creature.name)
        def1.addErrback(self.failure)

    def picked_angel(self, legion, angel):
        """Callback from AcquireAngel"""
        print "GUIMasterBoard.picked_angel", legion, angel
        def1 = self.user.callRemote("acquire_angel", self.game.name,
          legion.markername, angel.name)
        def1.addErrback(self.failure)

    def compute_scale(self):
        """Return the approximate maximum scale that let the board fit on 
        the screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        xscale = math.floor(width / (self.board.hex_width() * 4. + 2))
        # The -3 is a fudge factor to leave room for menus and toolbars.
        yscale = math.floor(height / (self.board.hex_height() * 4 * SQRT3)) - 3
        return int(min(xscale, yscale))

    def compute_width(self):
        """Return the width of the board in pixels."""
        return int(math.ceil(self.scale * (self.board.hex_width() * 4 + 2)))

    def compute_height(self):
        """Return the height of the board in pixels."""
        return int(math.ceil(self.scale * self.board.hex_height() * 4 * SQRT3))

    def markers_in_hex(self, hexlabel):
        return [marker for marker in self.markers if marker.legion.hexlabel ==
          hexlabel]

    def _add_missing_markers(self):
        """Add markers for any legions that lack them."""
        for legion in self.game.all_legions():
            if legion.markername not in (marker.name for marker in 
              self.markers):
                marker = Marker.Marker(legion, True, self.scale)
                self.markers.append(marker)

    def _remove_extra_markers(self):
        """Remove markers for any legions that are no longer there."""
        all_markernames = [legion.markername for legion in 
          self.game.all_legions()]
        hitlist = [marker for marker in self.markers 
          if marker.name not in all_markernames]
        for marker in hitlist:
            self.markers.remove(marker)

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
        self._remove_extra_markers()
        hexlabels = set((marker.legion.hexlabel for marker in self.markers))
        for hexlabel in hexlabels:
            self._compute_marker_locations(hexlabel)
            mih = self.markers_in_hex(hexlabel)
            # Draw in reverse order so that the markers that come earlier
            # in self.markers are on top.
            for marker in reversed(mih):
                marker.update_height()
                self._render_marker(marker, gc)

    def draw_recruitchits(self, gc):
        if not self.game:
            return
        for (chit, unused) in self.recruitchits:
            self._render_marker(chit, gc)

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


    def update_gui(self, hexlabels=None):
        gc = self.area.get_style().fg_gc[gtk.STATE_NORMAL]
        if hexlabels is None:
            guihexes = self.guihexes.values()
        else:
            # Also redraw neighbors, to clean up chit overdraw.
            guihexes = set()
            for hexlabel in hexlabels:
                if hexlabel in self.guihexes:
                    guihexes.add(self.guihexes[hexlabel])
                    masterhex = self.board.hexes[hexlabel]
                    for neighbor in masterhex.neighbors:
                        if neighbor:
                            guihexes.add(self.guihexes[neighbor.label])
        for guihex in guihexes:
            guihex.update_gui(gc)
        self.draw_markers(gc)
        self.draw_recruitchits(gc)
        self.draw_movement_die(gc)

    def unselect_all(self):
        repaint_hexlabels = set()
        for guihex in self.guihexes.values():
            if guihex.selected:
                guihex.selected = False
                repaint_hexlabels.add(guihex.masterhex.label)
        self.update_gui(repaint_hexlabels)

    def clear_recruitchits(self):
        if self.recruitchits:
            hexlabels = set((tup[1] for tup in self.recruitchits))
            self.recruitchits = []
            self.update_gui(hexlabels)

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
            self.update_gui(hexlabels)

    def highlight_unmoved_legions(self):
        """Highlight all hexes containing an unmoved legion belonging to the
        active, current player."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.clear_recruitchits()
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.values():
                if not legion.moved:
                    hexlabels.add(legion.hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.update_gui(hexlabels)
                
    def highlight_engagements(self):
        """Highlight all hexes with engagements."""
        self.unselect_all()
        hexlabels = self.game.engagement_hexlabels()
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            guihex.selected = True
        self.update_gui(hexlabels)

    def highlight_hex(self, hexlabel):
        """Highlight one hex."""
        self.unselect_all()
        guihex = self.guihexes[hexlabel]
        guihex.selected = True
        self.update_gui([hexlabel])

    def highlight_recruits(self):
        """Highlight all hexes in which the active player can recruit."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.values():
                hexlabel = legion.hexlabel
                if (legion.moved and not legion.recruited and 
                  len(legion) < 7 and 
                  legion.available_recruits(self.game.board.hexes[hexlabel],
                    self.game.caretaker)):
                      hexlabels.add(hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.update_gui(hexlabels)

    def cb_done(self, action):
        print "done", action, self.game.phase
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
            elif self.game.phase == Phase.FIGHT:
                if player.can_exit_fight_phase(self.game):
                    def1 = self.user.callRemote("done_with_engagements",
                      self.game.name)
                    def1.addErrback(self.failure)
            elif self.game.phase == Phase.MUSTER:
                def1 = self.user.callRemote("done_with_recruits",
                  self.game.name)
                def1.addErrback(self.failure)

    def cb_mulligan(self, action):
        print "mulligan", action
        player = self.game.get_player_by_name(self.username)
        if player.can_take_mulligan(self.game):
            history = self.game.history
            if history.can_undo(self.username):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action", 
                  last_action.undo_action())
                def1.addCallback(self.cb_mulligan)
                def1.addErrback(self.failure)
            else:
                def1 = self.user.callRemote("take_mulligan", self.game.name)
                def1.addErrback(self.failure)

    def cb_about(self, action):
        About.About()

    def cb_undo(self, action):
        print "undo", action
        if self.game:
            history = self.game.history
            if history.can_undo(self.username):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action", 
                  last_action.undo_action())
                def1.addErrback(self.failure)

    def cb_redo(self, action):
        print "redo", action
        if self.game:
            history = self.game.history
            if history.can_redo(self.username):
                action = history.undone[-1]
                def1 = self.user.callRemote("apply_action", action)
                def1.addErrback(self.failure)

    def cb_maybe_flee(self, attacker, defender, fled):
        print "maybe_flee", attacker, defender, fled
        if fled:
            self.user.callRemote("flee", self.game.name, defender.markername)
        else:
            self.user.callRemote("do_not_flee", self.game.name, 
              defender.markername)

    def cb_negotiate(self, attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names, response_id):
        """Callback from Negotiate dialog.

        response_ids: 0 - Concede
                      1 - Make proposal
                      2 - Done proposing
                      3 - Fight
        """
        print "negotiate", response_id
        player = self.game.get_player_by_name(self.username)
        hexlabel = attacker_legion.hexlabel
        for legion in player.friendly_legions(hexlabel):
            friendly_legion = legion
        if attacker_legion == friendly_legion:
            enemy_legion = defender_legion
        else:
            enemy_legion = attacker_legion
        if response_id == 0:
            self.user.callRemote("concede", self.game.name, 
              friendly_legion.markername, enemy_legion.markername, hexlabel)
        elif response_id == 1:
            self.user.callRemote("make_proposal", self.game.name,
              attacker_legion.markername, attacker_creature_names, 
              defender_legion.markername, defender_creature_names)
        elif response_id == 2:
            # TODO no more proposals
            pass
        elif response_id == 3:
            self.user.callRemote("fight", self.game.name,
              attacker_legion.markername, defender_legion.markername)
              
    def cb_proposal(self, attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names, response_id):
        """Callback from Proposal dialog.

        response_ids: 0 - Accept
                      1 - Reject
        """
        print "proposal", response_id
        if response_id == 0:
            self.user.callRemote("accept_proposal", self.game.name, 
              attacker_legion.markername, attacker_creature_names, 
              defender_legion.markername, defender_creature_names)
        elif response_id == 1:
            self.user.callRemote("reject_proposal", self.game.name,
              attacker_legion.markername, attacker_creature_names, 
              defender_legion.markername, defender_creature_names)

    def destroy_negotiate(self):
        if self.negotiate is not None:
            self.negotiate.destroy()
            self.negotiate = None
        for proposal in self.proposals:
            proposal.destroy()
        self.proposals.clear()

    def failure(self, arg):
        print "GUIMasterBoard.failure", arg

    def update(self, observed, action):
        print "GUIMasterBoard.update", self, observed, action

        if isinstance(action, Action.CreateStartingLegion):
            legion = self.game.find_legion(action.markername)
            hexlabels = [legion.hexlabel]
            self.update_gui(hexlabels)
            self.highlight_tall_legions()

        elif isinstance(action, Action.SplitLegion):
            self._splitting_legion = None
            legion = self.game.find_legion(action.parent_markername)
            hexlabels = [legion.hexlabel]
            self.update_gui(hexlabels)
            self.highlight_tall_legions()

        elif isinstance(action, Action.UndoSplit):
            self._splitting_legion = None
            legion = self.game.find_legion(action.parent_markername)
            repaint_hexlabels = set([legion.hexlabel,
              legion.previous_hexlabel])
            self.update_gui(repaint_hexlabels)
            self.highlight_tall_legions()

        elif isinstance(action, Action.RollMovement):
            if action.playername == self.username:
                self.highlight_unmoved_legions()
            else:
                self.update_gui([])

        elif isinstance(action, Action.MoveLegion) or isinstance(action,
          Action.UndoMoveLegion):
            self.selected_marker = None
            self.unselect_all()
            legion = self.game.find_legion(action.markername)
            repaint_hexlabels = set([legion.hexlabel,
              legion.previous_hexlabel])
            self.update_gui(repaint_hexlabels)
            if action.playername == self.username:
                self.highlight_unmoved_legions()

        elif isinstance(action, Action.DoneMoving):
            self.clear_recruitchits()
            if self.game.phase == Phase.FIGHT:
                self.highlight_engagements()
            elif self.game.phase == Phase.MUSTER:
                self.highlight_recruits()

        elif isinstance(action, Action.ResolvingEngagement):
            hexlabel = action.hexlabel
            self.highlight_hex(hexlabel)
            for legion in self.game.all_legions(hexlabel):
                if legion.player == self.game.active_player:
                    attacker = legion
                else:
                    defender = legion
            if defender.player.name == self.username:
                if defender.can_flee():
                    Flee.Flee(self.username, attacker, defender, 
                      self.cb_maybe_flee, self)
                else:
                    # Can't flee, so we always send the do_not_flee.
                    # (Others may not know that we have a lord here.)
                    self.cb_maybe_flee(attacker, defender, False)

        elif isinstance(action, Action.Flee):
            print "GUIMasterBoard got Flee", action.markername, action.hexlabel
            self.update_gui([action.hexlabel])
            self.highlight_engagements()

        elif isinstance(action, Action.DoNotFlee):
            print "GUIMasterBoard got DoNotFlee", action.markername
            markername = action.markername
            defender = self.game.find_legion(markername)
            hexlabel = defender.hexlabel
            for legion in self.game.all_legions(hexlabel=hexlabel):
                if legion != defender:
                    attacker = legion
            if (defender.player.name == self.username or
              attacker.player.name == self.username):
                self.negotiate = Negotiate.Negotiate(self.username, attacker, 
                  defender, self.cb_negotiate, self)

        elif isinstance(action, Action.Concede):
            print "GUIMasterBoard got Concede", action.markername, \
              action.hexlabel
            self.destroy_negotiate()
            self.update_gui([action.hexlabel])
            self.highlight_engagements()

        elif isinstance(action, Action.MakeProposal):
            print "GUIMasterBoard got MakeProposal"
            attacker_markername = action.attacker_markername
            attacker = self.game.find_legion(attacker_markername)
            defender_markername = action.defender_markername
            defender = self.game.find_legion(defender_markername)
            if attacker is not None and defender is not None:
                self.proposals.add(Proposal.Proposal(self.username, attacker, 
                  action.attacker_creature_names, defender,
                  action.defender_creature_names, self.cb_proposal, self))

        elif isinstance(action, Action.AcceptProposal):
            print "GUIMasterBoard got AcceptProposal"
            self.destroy_negotiate()
            self.update_gui([action.hexlabel])
            self.highlight_engagements()

        elif isinstance(action, Action.RejectProposal):
            print "GUIMasterBoard got RejectProposal"
            attacker_markername = action.attacker_markername
            attacker = self.game.find_legion(attacker_markername)
            defender_markername = action.defender_markername
            defender = self.game.find_legion(defender_markername)
            if (action.other_playername == self.username):
                self.negotiate = Negotiate.Negotiate(self.username, attacker, 
                  defender, self.cb_negotiate, self)

        elif isinstance(action, Action.DoneFighting):
            self.highlight_recruits()

        elif isinstance(action, Action.RecruitCreature) or isinstance(action,
          Action.UndoRecruit):
            self.highlight_recruits()

        elif isinstance(action, Action.DoneRecruiting):
            if self.game.phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif self.game.phase == Phase.MOVE:
                self.highlight_unmoved_legions()

        elif isinstance(action, Action.AcquireAngels):
            if action.playername == self.username:
                markername = action.markername
                legion = self.game.find_legion(markername)
                angels = action.angels
                archangels = action.archangels
                caretaker = self.game.caretaker
                while archangels > 0:
                    possible_angels = ["Archangel", "Angel"]
                    available_angels = [angel for angel in possible_angels
                      if caretaker.counts.get(angel) > 0]
                    if not available_angels:
                        break
                    AcquireAngel.AcquireAngel(self.username, legion.player,
                      legion, available_angels, self.picked_angel, self)
                    archangels -= 1
                while angels > 0:
                    possible_angels = ["Angel"]
                    available_angels = [angel for angel in possible_angels
                      if caretaker.counts.get(angel) > 0]
                    if not available_angels:
                        break
                    AcquireAngel.AcquireAngel(self.username, legion.player,
                      legion, available_angels, self.picked_angel, self)
                    angels -= 1

        elif isinstance(action, Action.AcquireAngel):
            markername = action.markername
            legion = self.game.find_legion(markername)
            hexlabel = legion.hexlabel
            self.update_gui([hexlabel])
            self.highlight_engagements()


if __name__ == "__main__":
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(board)
    # Allow exiting with control-C, unlike mainloop()
    while True:
        gtk.main_iteration()
