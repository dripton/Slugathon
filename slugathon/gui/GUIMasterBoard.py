#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"

# TODO When we click on a marker, move it to the top of the z-order

import math
from sys import maxint

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
import gtk
import cairo
from zope.interface import implements

from slugathon.gui import (GUIMasterHex, Marker, ShowLegion, PickMarker,
  SplitLegion, About, icon, Die, PickRecruit, Flee, Inspector, Chit,
  Negotiate, Proposal, AcquireAngel, GUIBattleMap, SummonAngel, PickEntrySide,
  PickMoveType, PickTeleportingLord, InfoDialog, StatusScreen, GUICaretaker)
from slugathon.util import guiutils, prefs
from slugathon.util.Observer import IObserver
from slugathon.game import Action, Phase, Game, Creature
from slugathon.util.log import log
from slugathon.util.bag import bag


SQRT3 = math.sqrt(3.0)


ui_string = """<ui>
  <menubar name="Menubar">
    <menu action="GameMenu">
      <menuitem action="Save"/>
      <menuitem action="Quit"/>
    </menu>
    <menu action="PhaseMenu">
      <menuitem action="Done"/>
      <menuitem action="Undo"/>
      <menuitem action="Undo All"/>
      <menuitem action="Redo"/>
      <separator/>
      <menuitem action="Mulligan"/>
      <menuitem action="Clear Recruit Chits"/>
    </menu>
    <menu action="HelpMenu">
      <menuitem action="About"/>
    </menu>
  </menubar>
  <toolbar name="Toolbar">
    <toolitem action="Done"/>
    <toolitem action="Undo"/>
    <toolitem action="Undo All"/>
    <toolitem action="Redo"/>
    <separator/>
    <toolitem action="Mulligan"/>
    <toolitem action="Clear Recruit Chits"/>
  </toolbar>
</ui>"""


class GUIMasterBoard(gtk.Window):
    """GUI representation of the masterboard."""

    implements(IObserver)

    def __init__(self, board, game=None, user=None, username=None, scale=None):
        gtk.Window.__init__(self)

        self.board = board
        self.user = user
        self.username = username
        self.game = game

        self.set_icon(icon.pixbuf)
        self.set_title("Masterboard - Slugathon - %s" % self.username)
        self.connect("destroy", self.cb_destroy)
        self.connect("configure-event", self.cb_configure_event)

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
        self.area.set_size_request(self.compute_width(), self.compute_height())
        self.vbox.pack_start(self.area)
        self.markers = []
        self.guihexes = {}
        # list of tuples (Chit, hexlabel)
        self.recruitchits = []
        for hex1 in self.board.hexes.itervalues():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.selected_marker = None
        self.inspector = Inspector.Inspector(self.username, self)
        self.negotiate = None
        self.proposals = set()
        self.guimap = None
        self.acquire_angel = None
        self.game_over = None
        self.status_screen = None
        self.guicaretaker = None

        # Set of hexlabels of hexes to redraw.
        # If set to all hexlabels then we redraw the whole window.
        # Used to combine nearly simultaneous redraws into one.
        self.repaint_hexlabels = set()

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

        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)
        self.area.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.area.connect("motion-notify-event", self.cb_motion)
        self.show_all()

    def create_ui(self):
        ag = gtk.ActionGroup("MasterActions")
        # TODO confirm quit
        actions = [
          ("GameMenu", None, "_Game"),
          ("Save", gtk.STOCK_SAVE, "_Save", "s", "Save", self.cb_save),
          ("Quit", gtk.STOCK_QUIT, "_Quit", "<control>Q", "Quit program",
            guiutils.exit),
          ("PhaseMenu", None, "_Phase"),
          ("Done", gtk.STOCK_APPLY, "_Done", "d", "Done", self.cb_done),
          ("Undo", gtk.STOCK_UNDO, "_Undo", "u", "Undo", self.cb_undo),
          ("Undo All", gtk.STOCK_DELETE, "Undo _All", "a", "Undo All",
            self.cb_undo_all),
          ("Redo", gtk.STOCK_REDO, "_Redo", "r", "Redo", self.cb_redo),
          ("Mulligan", gtk.STOCK_MEDIA_REWIND, "_Mulligan", "m", "Mulligan",
            self.cb_mulligan),
          ("Clear Recruit Chits", gtk.STOCK_CLEAR, "_Clear Recruit Chits", "c",
           "Clear Recruit Chits", self.clear_all_recruitchits),
          ("HelpMenu", None, "_Help"),
          ("About", gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)
        self.add_accel_group(self.ui.get_accel_group())

    def _init_status_screen(self):
        if not self.status_screen:
            self.status_screen = StatusScreen.StatusScreen(self.game,
              self.username, self)
            self.game.add_observer(self.status_screen)

    def _init_caretaker(self):
        if not self.guicaretaker:
            self.guicaretaker = GUICaretaker.GUICaretaker(self.game,
              self.username, self)
            self.game.add_observer(self.guicaretaker)


    def cb_destroy(self, event):
        for widget in [self.guimap]:
            if widget is not None:
                widget.destroy()
        self.destroy()

    def cb_configure_event(self, event, unused):
        if self.username:
            x, y = self.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.username, self.__class__.__name__,
              width, height)
        return False

    def cb_area_expose(self, area, event):
        self.update_gui(event=event)
        return True

    def cb_click(self, area, event):
        for marker in self.markers:
            if marker.point_inside((event.x, event.y)):
                self.clicked_on_marker(area, event, marker)
                return True
        for guihex in self.guihexes.itervalues():
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

    def _no_teleports(self, moves):
        """Return True iff none of the move tuples in moves are teleports"""
        for move in moves:
            if move[1] == Game.TELEPORT:
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
            return
        if event.button == 1:
            phase = self.game.phase
            if phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif phase == Phase.MOVE and self.selected_marker:
                if guihex.selected:
                    legion = self.selected_marker.legion
                    all_moves = self.game.find_all_moves(legion,
                      self.board.hexes[legion.hexlabel],
                      legion.player.movement_roll)
                    moves = [m for m in all_moves if m[0] ==
                      guihex.masterhex.label]
                    self._pick_move_type(legion, moves)
                self.selected_marker = None
                self.clear_all_recruitchits()
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


    def _pick_move_type(self, legion, moves):
        """Figure out whether to teleport, then call _pick_entry_side."""
        if self._all_teleports(moves):
            self._pick_entry_side(True, legion, moves)
        elif self._no_teleports(moves):
            self._pick_entry_side(False, legion, moves)
        else:
            hexlabel = moves[0][0]
            _, def1 = PickMoveType.new(self.username, legion, hexlabel, self)
            def1.addCallback(self._pick_entry_side, legion, moves)

    def _pick_entry_side(self, teleport, legion, moves):
        """Pick an entry side, then call _pick_teleporting_lord.

        teleport can be True, False, or None (cancel the move).
        """
        if teleport is None:
            self.highlight_unmoved_legions()
            return
        hexlabel = moves[0][0]
        battlehex = self.game.board.hexes[hexlabel]
        terrain = battlehex.terrain
        if terrain == "Tower":
            entry_sides = set([5])
        elif teleport:
            entry_sides = set([1, 3, 5])
        else:
            entry_sides = set((m[1] for m in moves))
            entry_sides.discard("TELEPORT")
        if len(entry_sides) == 1 or not legion.player.enemy_legions(hexlabel):
            self._pick_teleporting_lord(entry_sides.pop(), legion, moves,
              teleport)
        else:
            if teleport:
                entry_sides = set([1, 3, 5])
            else:
                entry_sides = set((move[1] for move in moves))
            _, def1 = PickEntrySide.new(terrain, entry_sides, self)
            def1.addCallback(self._pick_teleporting_lord, legion, moves,
              teleport)

    def _pick_teleporting_lord(self, entry_side, legion, moves, teleport):
        """Pick a teleporting lord, then call _do_move_legion."""
        if entry_side is None:
            self.highlight_unmoved_legions()
            return
        hexlabel = moves[0][0]
        if teleport:
            if legion.player.enemy_legions(hexlabel):
                assert legion.has_titan
                lord_name = "Titan"
            else:
                lord_types = legion.lord_types
                if len(lord_types) == 1:
                    lord_name = lord_types.pop()
                else:
                    _, def1 = PickTeleportingLord.new(self.username, legion,
                      self)
                    def1.addCallback(self._do_move_legion, legion, moves,
                      teleport, entry_side)
                    return
        else:
            lord_name = None
        self._do_move_legion(lord_name, legion, moves, teleport,
          entry_side)

    def _do_move_legion(self, lord_name, legion, moves, teleport, entry_side):
        """Call the server to request a legion move."""
        hexlabel = moves[0][0]
        def1 = self.user.callRemote("move_legion", self.game.name,
          legion.markername, hexlabel, entry_side, teleport, lord_name)
        def1.addErrback(self.failure)


    def clicked_on_marker(self, area, event, marker):
        if event.button >= 2:
            ShowLegion.ShowLegion(self.username, marker.legion, True, self)

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
                    self.split_legion(legion)
                else:
                    if not player.markernames:
                        InfoDialog.InfoDialog(self, "Info",
                          "No markers available")
                        return
                    _, def1 = PickMarker.new(self.username, self.game.name,
                      player.markernames, self)
                    def1.addCallback(self.picked_marker_presplit, legion)

            elif phase == Phase.MOVE:
                legion = marker.legion
                player = legion.player
                if player.name != self.username:
                    # Not my marker; ignore it and click on the hex
                    guihex = self.guihexes[legion.hexlabel]
                    self.clicked_on_hex(area, event, guihex)
                    return
                self.unselect_all()
                self.clear_all_recruitchits()
                if legion.moved:
                    moves = []
                else:
                    moves = self.game.find_all_moves(legion, self.board.hexes[
                      legion.hexlabel], player.movement_roll)
                if moves:
                    self.selected_marker = marker
                    for move in moves:
                        hexlabel = move[0]
                        guihex = self.guihexes[hexlabel]
                        guihex.selected = True
                        self.repaint_hexlabels.add(hexlabel)
                        recruit_names = legion.available_recruits(
                          self.board.hexes[hexlabel].terrain,
                          self.game.caretaker)
                        if recruit_names:
                            self._create_recruitchits(legion, hexlabel,
                              recruit_names)
                self.repaint()

            elif phase == Phase.FIGHT:
                legion = marker.legion
                guihex = self.guihexes[legion.hexlabel]
                if guihex.selected and self.game.battle_masterhex is None:
                    self.user.callRemote("resolve_engagement", self.game.name,
                      guihex.masterhex.label)

            elif phase == Phase.MUSTER:
                self.unselect_all()
                legion = marker.legion
                if legion.moved:
                    masterhex = self.board.hexes[legion.hexlabel]
                    mterrain = masterhex.terrain
                    caretaker = self.game.caretaker
                    if legion.can_recruit:
                        log("PickRecruit.new (muster)")
                        _, def1 = PickRecruit.new(self.username, legion,
                          mterrain, caretaker, self)
                        def1.addCallback(self.picked_recruit)
                self.highlight_recruits()


    def picked_marker_presplit(self, (game_name, username, markername),
      legion):
        player = self.game.get_player_by_name(username)
        player.pick_marker(markername)
        if markername:
            self.split_legion(legion)

    def split_legion(self, legion):
        if legion is not None:
            _, def1 = SplitLegion.new(self.username, legion, self)
            def1.addCallback(self.try_to_split_legion)

    def try_to_split_legion(self, (old_legion, new_legion1, new_legion2)):
        if old_legion is None:
            # canceled
            return
        def1 = self.user.callRemote("split_legion", self.game.name,
          new_legion1.markername, new_legion2.markername,
          new_legion1.creature_names, new_legion2.creature_names)
        def1.addErrback(self.failure)

    def picked_recruit(self, (legion, creature, recruiter_names)):
        """Callback from PickRecruit"""
        if creature is not None:
            def1 = self.user.callRemote("recruit_creature", self.game.name,
              legion.markername, creature.name, recruiter_names)
            def1.addErrback(self.failure)
        elif self.game.phase == Phase.FIGHT:
            def1 = self.user.callRemote("do_not_reinforce", self.game.name,
              legion.markername)
            def1.addErrback(self.failure)

    def picked_summon(self, (legion, donor, creature)):
        """Callback from SummonAngel"""
        if donor is None or creature is None:
            def1 = self.user.callRemote("do_not_summon", self.game.name,
              legion.markername)
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("summon_angel", self.game.name,
              legion.markername, donor.markername, creature.name)
            def1.addErrback(self.failure)

    def picked_angels(self, (legion, angels)):
        """Callback from AcquireAngel"""
        log("picked_angels", legion, angels)
        self.acquire_angel = None
        if not angels:
            log("calling do_not_acquire", legion)
            def1 = self.user.callRemote("do_not_acquire", self.game.name,
              legion.markername)
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("acquire_angels", self.game.name,
              legion.markername, [angel.name for angel in angels])
            def1.addErrback(self.failure)

    def compute_scale(self):
        """Return the approximate maximum scale that let the board fit on
        the screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        xscale = math.floor(width / (self.board.hex_width() * 4. + 2))
        # Fudge factor to leave room for menus and toolbars.
        yscale = math.floor(height / (self.board.hex_height() * 4 * SQRT3)) - 4
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
        markernames = set((marker.name for marker in self.markers))
        for legion in self.game.all_legions():
            if legion.markername not in markernames:
                marker = Marker.Marker(legion, True, self.scale)
                self.markers.append(marker)

    def _remove_extra_markers(self):
        """Remove markers for any legions that are no longer there."""
        all_markernames = set([legion.markername for legion in
          self.game.all_legions()])
        hitlist = [marker for marker in self.markers
          if marker.name not in all_markernames]
        for marker in hitlist:
            self.markers.remove(marker)

    def _place_chits(self, chits, guihex):
        """Compute and set the correct locations for each chit (or recruitchit
        or marker) in the list, if they're all in guihex, taking their scale
        into account.
        """
        if not chits:
            return
        num = len(chits)
        chit_scale = chits[0].chit_scale
        # If we have a lot of chits, squeeze them closer together so they
        # fit in the hex.
        if num <= 3:
            increment = chit_scale / 2
        else:
            increment = chit_scale / 4
        base_location = (guihex.center[0] - chit_scale / 2,
          guihex.center[1] - chit_scale / 2)
        starting_offset = (num - 1) / 2.
        first_location = (base_location[0] - starting_offset * increment,
          base_location[1] - starting_offset * increment)
        for ii, chit in enumerate(chits):
            chit.location = (first_location[0] + ii * increment,
              first_location[1] + ii * increment)

    def _render_marker(self, marker, ctx):
        ctx.set_source_surface(marker.surface, int(round(marker.location[0])),
          int(round(marker.location[1])))
        ctx.paint()

    def draw_markers(self, ctx):
        if not self.game:
            return
        self._add_missing_markers()
        self._remove_extra_markers()
        hexlabels = set((marker.legion.hexlabel for marker in self.markers))
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            mih = self.markers_in_hex(hexlabel)
            self._place_chits(mih, guihex)
            # Draw in reverse order so that the markers that come earlier
            # in self.markers are on top.
            for marker in reversed(mih):
                marker.update_height()
                self._render_marker(marker, ctx)

    def _create_recruitchits(self, legion, hexlabel, recruit_names):
        player = legion.player
        guihex = self.guihexes[hexlabel]
        recruitchit_scale = self.scale * Chit.CHIT_SCALE_FACTOR / 4
        # If there are already recruitchits here (because we reinforced
        # without clearing them), use a bag and take the maximum number
        # of each creature.
        old_chits = bag()
        for (chit, hexlabel2) in self.recruitchits:
            if hexlabel == hexlabel2:
                old_chits.add(chit.creature.name)
        new_chits = bag()
        for name in recruit_names:
            new_chits.add(name)
        diff = new_chits.difference(old_chits)
        chits = []
        for name, number in diff.iteritems():
            for unused in xrange(number):
                recruit = Creature.Creature(name)
                chit = Chit.Chit(recruit, player.color, recruitchit_scale)
                chits.append(chit)
                self.recruitchits.append((chit, hexlabel))
        self._place_chits(chits, guihex)

    def draw_recruitchits(self, ctx):
        if not self.game:
            return
        # Draw in forward order so the last recruitchit in the list is on top.
        for (chit, unused) in self.recruitchits:
            self._render_marker(chit, ctx)

    def draw_movement_die(self, ctx):
        try:
            roll = self.game.active_player.movement_roll
        except AttributeError:
            return
        if not roll:
            return
        die = Die.Die(roll, scale=self.scale)
        ctx.set_source_surface(die.surface, 0, 0)
        ctx.paint()

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

        Compute the dirty rectangle from the union of
        self.repaint_hexlabels and the event's area.
        """
        if event is None:
            if not self.repaint_hexlabels:
                return
            else:
                clip_rect = self.bounding_rect_for_hexlabels(
                  self.repaint_hexlabels)
        else:
            if self.repaint_hexlabels:
                clip_rect = guiutils.combine_rectangles(event.area,
                  self.bounding_rect_for_hexlabels(self.repaint_hexlabels))
            else:
                clip_rect = event.area

        x, y, width, height = self.allocation
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.rectangle(*clip_rect)
        ctx.clip()

        # black background
        if event is not None:
            ctx.set_source_rgb(0, 0, 0)
            width, height = self.area.size_request()
            ctx.rectangle(0, 0, width, height)
            ctx.fill()
        for hexlabel in self.repaint_hexlabels:
            if hexlabel:
                ctx.set_source_rgb(0, 0, 0)
                guihex = self.guihexes[hexlabel]
                x, y, width, height = guihex.bounding_rect
                ctx.rectangle(x, y, width, height)
                ctx.fill()
        for guihex in self.guihexes.itervalues():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)

        self.draw_markers(ctx)
        self.draw_recruitchits(ctx)
        self.draw_movement_die(ctx)

        ctx2 = self.area.window.cairo_create()
        ctx2.set_source_surface(surface)
        ctx2.paint()

        self.repaint_hexlabels.clear()

    def repaint(self, hexlabels=None):
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)

    def unselect_all(self):
        for guihex in self.guihexes.itervalues():
            if guihex.selected:
                guihex.selected = False
                self.repaint_hexlabels.add(guihex.masterhex.label)
        self.repaint()

    def clear_all_recruitchits(self, *unused):
        if self.recruitchits:
            hexlabels = set((tup[1] for tup in self.recruitchits))
            self.recruitchits = []
            self.repaint(hexlabels)

    def clear_recruitchits(self, hexlabel):
        """Clear recruitchits in one hex."""
        self.recruitchits = [(chit, hexlabel2) for (chit, hexlabel2)
          in self.recruitchits if hexlabel2 != hexlabel]
        self.repaint([hexlabel])

    def highlight_tall_legions(self):
        """Highlight all hexes containing a legion of height 7 or more
        belonging to the active, current player."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            if player.markernames:
                for legion in player.legions.itervalues():
                    if len(legion) >= 7:
                        self.repaint_hexlabels.add(legion.hexlabel)
                        guihex = self.guihexes[legion.hexlabel]
                        guihex.selected = True
            self.repaint()

    def highlight_unmoved_legions(self):
        """Highlight all hexes containing an unmoved legion belonging to the
        active, current player."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.clear_all_recruitchits()
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.itervalues():
                if not legion.moved:
                    hexlabels.add(legion.hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.repaint(hexlabels)

    def highlight_engagements(self):
        """Highlight all hexes with engagements."""
        self.unselect_all()
        hexlabels = self.game.engagement_hexlabels
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            guihex.selected = True
        self.repaint(hexlabels)

    def highlight_hex(self, hexlabel):
        """Highlight one hex."""
        self.unselect_all()
        guihex = self.guihexes[hexlabel]
        guihex.selected = True
        self.repaint([hexlabel])

    def highlight_recruits(self):
        """Highlight all hexes in which the active player can recruit."""
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions.itervalues():
                hexlabel = legion.hexlabel
                if legion.moved and legion.can_recruit:
                    hexlabels.add(hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.repaint(hexlabels)

    def cb_save(self, action):
        def1 = self.user.callRemote("save", self.game.name)
        def1.addErrback(self.failure)

    def cb_done(self, action):
        if not self.game:
            return
        player = self.game.get_player_by_name(self.username)
        if player == self.game.active_player:
            if self.game.phase == Phase.SPLIT:
                if player.can_exit_split_phase:
                    def1 = self.user.callRemote("done_with_splits",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(self, "Info",
                      "Must split initial legion 4-4")
            elif self.game.phase == Phase.MOVE:
                if player.can_exit_move_phase:
                    def1 = self.user.callRemote("done_with_moves",
                      self.game.name)
                    def1.addErrback(self.failure)
                elif not player.moved_legions:
                    InfoDialog.InfoDialog(self, "Info",
                      "Must move at least one legion")
                else:
                    InfoDialog.InfoDialog(self, "Info",
                      "Must separate split legions")
            elif self.game.phase == Phase.FIGHT:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote("done_with_engagements",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(self, "Info",
                      "Must resolve engagements")
            elif self.game.phase == Phase.MUSTER:
                def1 = self.user.callRemote("done_with_recruits",
                  self.game.name)
                def1.addErrback(self.failure)

    def cb_mulligan(self, action):
        if not self.game:
            return
        player = self.game.get_player_by_name(self.username)
        if player.can_take_mulligan:
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
        About.About(self)

    def cb_undo(self, action):
        if self.game:
            history = self.game.history
            if history.can_undo(self.username):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action",
                  last_action.undo_action())
                def1.addErrback(self.failure)

    def cb_undo_all(self, action):
        if self.game:
            history = self.game.history
            if history.can_undo(self.username):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action",
                  last_action.undo_action())
                def1.addCallback(self.cb_undo_all)
                def1.addErrback(self.failure)

    def cb_redo(self, action):
        if self.game:
            history = self.game.history
            if history.can_redo(self.username):
                action = history.undone[-1]
                def1 = self.user.callRemote("apply_action", action)
                def1.addErrback(self.failure)

    def cb_maybe_flee(self, (attacker, defender, fled)):
        if fled:
            self.user.callRemote("flee", self.game.name, defender.markername)
        else:
            self.user.callRemote("do_not_flee", self.game.name,
              defender.markername)

    def cb_negotiate(self, (attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names, response_id)):
        """Callback from Negotiate dialog."""
        player = self.game.get_player_by_name(self.username)
        hexlabel = attacker_legion.hexlabel
        for legion in player.friendly_legions(hexlabel):
            friendly_legion = legion
        if attacker_legion == friendly_legion:
            enemy_legion = defender_legion
        else:
            enemy_legion = attacker_legion
        if response_id == Negotiate.CONCEDE:
            self.user.callRemote("concede", self.game.name,
              friendly_legion.markername, enemy_legion.markername, hexlabel)
        elif response_id == Negotiate.MAKE_PROPOSAL:
            self.user.callRemote("make_proposal", self.game.name,
              attacker_legion.markername, attacker_creature_names,
              defender_legion.markername, defender_creature_names)
        elif response_id == Negotiate.DONE_PROPOSING:
            # TODO no more proposals
            pass
        elif response_id == Negotiate.FIGHT:
            self.user.callRemote("fight", self.game.name,
              attacker_legion.markername, defender_legion.markername)

    def cb_proposal(self, (attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names, response_id)):
        """Callback from Proposal dialog."""
        if response_id == Proposal.ACCEPT:
            self.user.callRemote("accept_proposal", self.game.name,
              attacker_legion.markername, attacker_creature_names,
              defender_legion.markername, defender_creature_names)
        elif response_id == Proposal.REJECT:
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
        log("failure", arg)

    def update(self, observed, action):
        if isinstance(action, Action.PickedColor):
            self._init_status_screen()
            self._init_caretaker()

        elif isinstance(action, Action.CreateStartingLegion):
            legion = self.game.find_legion(action.markername)
            self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.SplitLegion):
            legion = self.game.find_legion(action.parent_markername)
            self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.UndoSplit):
            legion = self.game.find_legion(action.parent_markername)
            for hexlabel in [legion.hexlabel, legion.previous_hexlabel]:
                if hexlabel is not None:
                    self.repaint_hexlabels.add(hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.RollMovement):
            self.repaint_hexlabels.update(self.board.hexes.keys())
            if action.playername == self.username:
                self.highlight_unmoved_legions()
            else:
                self.repaint()

        elif isinstance(action, Action.MoveLegion) or isinstance(action,
          Action.UndoMoveLegion):
            self.selected_marker = None
            self.unselect_all()
            legion = self.game.find_legion(action.markername)
            for hexlabel in [legion.hexlabel, legion.previous_hexlabel]:
                if hexlabel is not None:
                    self.repaint_hexlabels.add(hexlabel)
            self.clear_recruitchits(legion.previous_hexlabel)
            if action.playername == self.username:
                self.highlight_unmoved_legions()
            else:
                self.repaint()

        elif isinstance(action, Action.StartFightPhase):
            if action.playername == self.username:
                self.clear_all_recruitchits()
            self.highlight_engagements()
            player = self.game.active_player
            if self.username == player.name:
                if not self.game.engagement_hexlabels:
                    def1 = self.user.callRemote("done_with_engagements",
                      self.game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.StartMusterPhase):
            if action.playername == self.username:
                self.clear_all_recruitchits()
            self.highlight_recruits()
            player = self.game.active_player
            if self.username == player.name:
                if not player.can_recruit:
                    def1 = self.user.callRemote("done_with_recruits",
                      self.game.name)
                    def1.addErrback(self.failure)


        elif isinstance(action, Action.ResolvingEngagement):
            hexlabel = action.hexlabel
            self.highlight_hex(hexlabel)
            for legion in self.game.all_legions(hexlabel):
                if legion.player == self.game.active_player:
                    attacker = legion
                else:
                    defender = legion
            if defender.player.name == self.username:
                if defender.can_flee:
                    _, def1 = Flee.new(self.username, attacker, defender, self)
                    def1.addCallback(self.cb_maybe_flee)
                else:
                    # Can't flee, so we always send the do_not_flee.
                    # (Others may not know that we have a lord here.)
                    self.cb_maybe_flee((attacker, defender, False))

        elif isinstance(action, Action.Flee):
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()

        elif isinstance(action, Action.DoNotFlee):
            markername = action.markername
            defender = self.game.find_legion(markername)
            hexlabel = defender.hexlabel
            attacker = None
            for legion in self.game.all_legions(hexlabel=hexlabel):
                if legion != defender:
                    attacker = legion
            if (attacker is not None and (
              defender.player.name == self.username or
              attacker.player.name == self.username)):
                self.negotiate, def1 = Negotiate.new(self.username, attacker,
                  defender, self)
                def1.addCallback(self.cb_negotiate)

        elif isinstance(action, Action.Concede):
            self.destroy_negotiate()
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()

        elif isinstance(action, Action.MakeProposal):
            attacker_markername = action.attacker_markername
            attacker = self.game.find_legion(attacker_markername)
            defender_markername = action.defender_markername
            defender = self.game.find_legion(defender_markername)
            if attacker is not None and defender is not None:
                proposal, def1 = Proposal.new(self.username, attacker,
                  action.attacker_creature_names, defender,
                  action.defender_creature_names, self)
                def1.addCallback(self.cb_proposal)
                self.proposals.add(proposal)

        elif isinstance(action, Action.AcceptProposal):
            self.destroy_negotiate()
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()

        elif isinstance(action, Action.RejectProposal):
            attacker_markername = action.attacker_markername
            attacker = self.game.find_legion(attacker_markername)
            defender_markername = action.defender_markername
            defender = self.game.find_legion(defender_markername)
            if (action.other_playername == self.username):
                self.negotiate, def1 = Negotiate.new(self.username, attacker,
                  defender, self)
                def1.addCallback(self.cb_negotiate)

        elif isinstance(action, Action.RecruitCreature):
            legion = self.game.find_legion(action.markername)
            if legion:
                self.repaint_hexlabels.add(legion.hexlabel)
                creature_names = list(action.recruiter_names)
                creature_names.append(action.creature_name)
                self._create_recruitchits(legion, legion.hexlabel,
                  creature_names)
            self.highlight_recruits()

        elif (isinstance(action, Action.UndoRecruit) or
              isinstance(action, Action.UnReinforce)):
            legion = self.game.find_legion(action.markername)
            if legion:
                self.repaint_hexlabels.add(legion.hexlabel)
                self.clear_recruitchits(legion.hexlabel)
            self.highlight_recruits()

        elif isinstance(action, Action.StartSplitPhase):
            player = self.game.active_player
            if self.username == player.name:
                self.unselect_all()
                self.highlight_tall_legions()
                if not player.can_split:
                    def1 = self.user.callRemote("done_with_splits",
                      self.game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.SummonAngel):
            legion = self.game.find_legion(action.markername)
            donor = self.game.find_legion(action.donor_markername)
            lst = []
            if legion and legion.hexlabel:
                lst.append(legion.hexlabel)
                self._create_recruitchits(legion, legion.hexlabel,
                  [action.creature_name])
            if donor and donor.hexlabel:
                lst.append(donor.hexlabel)
            self.repaint(lst)
            self.highlight_engagements()

        elif isinstance(action, Action.UnSummon):
            legion = self.game.find_legion(action.markername)
            donor = self.game.find_legion(action.donor_markername)
            lst = []
            if legion and legion.hexlabel:
                lst.append(legion.hexlabel)
                self.clear_recruitchits(legion.hexlabel)
            if donor and donor.hexlabel:
                lst.append(donor.hexlabel)
            self.repaint(lst)
            self.highlight_engagements()

        elif isinstance(action, Action.CanAcquire):
            if (self.acquire_angel is None and action.playername ==
              self.username):
                markername = action.markername
                legion = self.game.find_legion(markername)
                angels = action.angels
                archangels = action.archangels
                caretaker = self.game.caretaker
                if angels or archangels:
                    self.acquire_angel, def1 = AcquireAngel.new(self.username,
                      legion, archangels, angels, self.game.caretaker, self)
                    def1.addCallback(self.picked_angels)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.Acquire):
            markername = action.markername
            legion = self.game.find_legion(markername)
            if legion and legion.hexlabel and action.angel_names:
                self._create_recruitchits(legion, legion.hexlabel,
                  action.angel_names)
                self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_engagements()

        elif isinstance(action, Action.Fight):
            self.destroy_negotiate()
            self.unselect_all()
            if self.guimap is None:
                self.guimap = GUIBattleMap.GUIBattleMap(self.game.battlemap,
                  self.game, self.user, self.username)
                self.game.add_observer(self.guimap)

        elif isinstance(action, Action.BattleOver):
            legion = self.game.find_legion(action.winner_markername)
            if legion:
                player = legion.player
                if (player.name == self.username and
                  self.game.phase == Phase.FIGHT):
                    if player == self.game.active_player:
                        # attacker can possibly summon
                        if legion.can_summon:
                            _, def1 = SummonAngel.new(self.username, legion,
                              self)
                            def1.addCallback(self.picked_summon)
                        else:
                            log("calling do_not_summon")
                            def1 = self.user.callRemote("do_not_summon",
                              self.game.name, legion.markername)
                            def1.addErrback(self.failure)
                    else:
                        # defender can possibly reinforce
                        masterhex = self.game.board.hexes[legion.hexlabel]
                        caretaker = self.game.caretaker
                        mterrain = masterhex.terrain
                        if legion.can_recruit:
                            log("PickRecruit.new (after)")
                            _, def1 = PickRecruit.new(self.username, legion,
                              mterrain, caretaker, self)
                            def1.addCallback(self.picked_recruit)
                        else:
                            log("calling do_not_reinforce")
                            def1 = self.user.callRemote("do_not_reinforce",
                              self.game.name, legion.markername)
                            def1.addErrback(self.failure)

            self.game.remove_observer(self.guimap)
            del self.guimap
            self.guimap = None
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()

        elif isinstance(action, Action.GameOver):
            if self.game_over is None:
                if action.winner_names:
                    message = "Game over.  %s wins." % action.winner_names[0]
                else:
                    message = "Game over.  Draw."
                self.game_over = InfoDialog.InfoDialog(self, "Info", message)


def main():
    from slugathon.game import MasterBoard

    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(board)
    guiboard.connect("destroy", lambda x: reactor.stop())
    reactor.run()

if __name__ == "__main__":
    main()
