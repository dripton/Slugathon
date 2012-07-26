#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


import math
from sys import maxint, argv
import logging

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
import gtk
import cairo
from zope.interface import implementer

from slugathon.util.Observer import IObserver
from slugathon.gui import (GUIBattleHex, Chit, PickRecruit, SummonAngel,
  PickCarry, PickStrikePenalty, InfoDialog, ConfirmDialog, Marker, TurnTrack,
  BattleDice, EventLog, Graveyard, About)
from slugathon.util import guiutils, prefs
from slugathon.game import Phase, Action


SQRT3 = math.sqrt(3.0)

ui_string = """<ui>
  <menubar name="Menubar">
    <menu action="PhaseMenu">
      <menuitem action="Done"/>
      <menuitem action="Undo"/>
      <menuitem action="Undo All"/>
      <menuitem action="Redo"/>
      <separator/>
      <menuitem action="Concede Battle"/>
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
  </toolbar>
</ui>"""


@implementer(IObserver)
class GUIBattleMap(gtk.EventBox):
    """GUI representation of a battlemap."""
    def __init__(self, battlemap, game=None, user=None, playername=None,
      scale=None, parent_window=None):
        gtk.EventBox.__init__(self)

        self.battlemap = battlemap
        self.game = game
        self.user = user
        self.playername = playername
        self.parent_window = parent_window

        self.chits = []
        self.selected_chit = None

        self.vbox = gtk.VBox(spacing=1)
        self.add(self.vbox)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = gtk.DrawingArea()
        self.area.set_size_request(self.compute_width(), self.compute_height())

        gtkcolor = gtk.gdk.color_parse("white")
        self.modify_bg(gtk.STATE_NORMAL, gtkcolor)

        if game:
            self.turn_track = TurnTrack.TurnTrack(game.attacker_legion,
                                                 game.defender_legion,
                                                 game,
                                                 self.scale)
            game.add_observer(self.turn_track)
            self.battle_dice = BattleDice.BattleDice(self.scale)
            game.add_observer(self.battle_dice)
            event_log = EventLog.EventLog(game, self.playername)
            game.add_observer(event_log)
            self.attacker_graveyard = Graveyard.Graveyard(game.attacker_legion)
            self.defender_graveyard = Graveyard.Graveyard(game.defender_legion)
        else:
            self.turn_track = None
            self.battle_dice = None
            self.attacker_graveyard = None
            self.defender_graveyard = None

        self.create_ui()
        self.vbox.pack_start(self.ui.get_widget("/Menubar"), expand=False)
        self.vbox.pack_start(self.ui.get_widget("/Toolbar"), expand=False)
        self.hbox1 = gtk.HBox()
        self.hbox2 = gtk.HBox()
        self.hbox3 = gtk.HBox()
        self.hbox4 = gtk.HBox()
        self.hbox5 = gtk.HBox(homogeneous=True)
        self.vbox.pack_start(self.hbox1, expand=False)
        self.vbox.pack_start(self.hbox2, fill=True)
        self.vbox.pack_start(self.hbox3, expand=False)
        self.vbox.pack_start(self.hbox4, expand=False)
        self.vbox.pack_start(self.hbox5, expand=False)
        if game:
            self.vbox.pack_start(event_log)
            gtkcolor = gtk.gdk.color_parse("white")
            attacker_marker = Marker.Marker(game.attacker_legion, True,
              self.scale / 2)
            attacker_marker.event_box.modify_bg(gtk.STATE_NORMAL, gtkcolor)
            defender_marker = Marker.Marker(game.defender_legion, True,
              self.scale / 2)
            defender_marker.event_box.modify_bg(gtk.STATE_NORMAL, gtkcolor)
            board = game.board
            hexlabel = game.defender_legion.hexlabel
            masterhex = board.hexes[hexlabel]
            own_hex_label = self.masterhex_label(masterhex, "xx-large")
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(own_hex_label)
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(self.spacer())
            self.hbox1.pack_start(self.spacer())
            self.hbox3.pack_start(self.turn_track, expand=False)
            self.hbox3.pack_start(self.battle_dice, fill=True)
            self.hbox2.pack_start(attacker_marker.event_box)
        self.hbox2.pack_start(self.area)
        if game:
            self.hbox2.pack_start(defender_marker.event_box)
            self.hbox5.pack_start(self.attacker_graveyard)
            self.hbox5.pack_start(self.defender_graveyard)

        self.guihexes = {}
        for hex1 in self.battlemap.hexes.itervalues():
            self.guihexes[hex1.label] = GUIBattleHex.GUIBattleHex(hex1, self)
        self.repaint_hexlabels = set()

        self.area.connect("expose-event", self.cb_area_expose)
        self.area.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)
        self.show_all()
        if (self.game and self.game.battle_active_player and
          self.game.battle_active_player.name == self.playername):
            self.highlight_mobile_chits()
        self.pickcarry = None

    def create_ui(self):
        ag = gtk.ActionGroup("BattleActions")
        actions = [
          ("PhaseMenu", None, "_Phase"),
          ("Done", gtk.STOCK_APPLY, "_Done", "d", "Done", self.cb_done),
          ("Undo", gtk.STOCK_UNDO, "_Undo", "u", "Undo", self.cb_undo),
          ("Undo All", gtk.STOCK_DELETE, "Undo _All", "a", "Undo All",
            self.cb_undo_all),
          ("Redo", gtk.STOCK_REDO, "_Redo", "r", "Redo", self.cb_redo),
          ("Concede Battle", None, "_Concede Battle", "<control>C",
            "Concede Battle", self.cb_concede),

          ("HelpMenu", None, "_Help"),
          ("About", gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)

    def compute_scale(self):
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        # Fudge factor to leave room on the sides.
        xscale = width / (2 * self.battlemap.hex_width) - 18
        # Fudge factor for menus and toolbars.
        yscale = height / (2 * SQRT3 * self.battlemap.hex_height) - 22
        return int(min(xscale, yscale))

    def compute_width(self):
        """Return the width of the map in pixels."""
        return int(math.ceil(self.scale * (self.battlemap.hex_width + 1) *
          3.2))

    def compute_height(self):
        """Return the height of the map in pixels."""
        return int((math.ceil(self.scale * self.battlemap.hex_height) *
          2 * SQRT3))

    def masterhex_label(self, masterhex, size):
        """Return a gtk.Label describing masterhex, inside a white
        gtk.EventBox."""
        eventbox = gtk.EventBox()
        if masterhex:
            text = '<span size="%s" weight="bold">%s hex %d</span>' % (size,
              masterhex.terrain, masterhex.label)
        else:
            text = ""
        label = gtk.Label()
        label.set_markup(text)
        eventbox.add(label)
        gtkcolor = gtk.gdk.color_parse("white")
        eventbox.modify_bg(gtk.STATE_NORMAL, gtkcolor)
        return eventbox

    def spacer(self):
        """Return a white gtk.EventBox."""
        eventbox = gtk.EventBox()
        gtkcolor = gtk.gdk.color_parse("white")
        eventbox.modify_bg(gtk.STATE_NORMAL, gtkcolor)
        return eventbox

    def unselect_all(self):
        """Unselect all guihexes."""
        for hexlabel, guihex in self.guihexes.iteritems():
            if guihex.selected:
                guihex.selected = False
                self.repaint_hexlabels.add(hexlabel)
        self.repaint()

    def highlight_mobile_chits(self):
        """Highlight the hexes containing all creatures that can move now."""
        if not self.game:
            return
        if (not self.game.battle_active_player or
          self.game.battle_active_player.name != self.playername):
            self.unselect_all()
            return
        hexlabels = set()
        for creature in self.game.battle_active_legion.mobile_creatures:
            hexlabels.add(creature.hexlabel)
        self.unselect_all()
        for hexlabel in hexlabels:
            self.guihexes[hexlabel].selected = True
        self.repaint(hexlabels)

    def highlight_strikers(self):
        """Highlight the hexes containing creatures that can strike now."""
        if not self.game:
            return
        if (not self.game.battle_active_player or
          self.game.battle_active_player.name != self.playername):
            self.unselect_all()
            return
        hexlabels = set()
        for creature in self.game.battle_active_legion.strikers:
            hexlabels.add(creature.hexlabel)
        self.unselect_all()
        for hexlabel in hexlabels:
            self.guihexes[hexlabel].selected = True
        self.repaint(hexlabels)

    def strike(self, striker, target, num_dice, strike_number):
        """Have striker strike target."""
        def1 = self.user.callRemote("strike", self.game.name, striker.name,
          striker.hexlabel, target.name, target.hexlabel, num_dice,
          strike_number)
        def1.addErrback(self.failure)

    def _do_auto_strike(self):
        """Do an automatic strike if appropriate.

        Return True iff we did one.
        """
        auto_strike = prefs.load_bool_option(self.playername,
          prefs.AUTO_STRIKE_SINGLE_TARGET)
        auto_rangestrike = prefs.load_bool_option(self.playername,
          prefs.AUTO_RANGESTRIKE_SINGLE_TARGET)
        if auto_strike or auto_rangestrike:
            strikers = self.game.battle_active_legion.strikers
            for striker in strikers:
                hexlabels = striker.find_target_hexlabels()
                if len(hexlabels) == 1:
                    hexlabel = hexlabels.pop()
                    if ((auto_strike and hexlabel in
                      striker.find_adjacent_target_hexlabels()) or
                      (auto_rangestrike and hexlabel in
                      striker.find_rangestrike_target_hexlabels())):
                        chits = self.chits_in_hex(hexlabel)
                        assert len(chits) == 1
                        chit = chits[0]
                        target = chit.creature
                        num_dice = striker.number_of_dice(target)
                        strike_number = striker.strike_number(target)
                        self.strike(striker, target, num_dice, strike_number)
                        return True
        return False

    def _do_auto_carry(self, striker, target, num_dice, strike_number,
      carries):
        """Automatically carry if appropriate.

        Return True iff we carried.
        """
        auto_carry = prefs.load_bool_option(self.playername,
          prefs.AUTO_CARRY_TO_SINGLE_TARGET)
        if auto_carry:
            carry_targets = striker.carry_targets(target, num_dice,
              strike_number)
            if len(carry_targets) == 1:
                carry_target = carry_targets.pop()
                def1 = self.user.callRemote("carry", self.game.name,
                  carry_target.name, carry_target.hexlabel, carries)
                def1.addErrback(self.failure)
                return True
        return False

    def cb_area_expose(self, area, event):
        self.update_gui(event=event)
        return True

    def cb_click(self, area, event):
        for chit in self.chits:
            if chit.point_inside((event.x, event.y)):
                self.clicked_on_chit(area, event, chit)
                return True
        for guihex in self.guihexes.itervalues():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                hexlabel = guihex.battlehex.label
                chits = self.chits_in_hex(hexlabel)
                if len(chits) == 1:
                    chit = chits[0]
                    self.clicked_on_chit(area, event, chit)
                else:
                    self.clicked_on_hex(area, event, guihex)
                return True
        self.clicked_on_background(area, event)
        return True

    def clicked_on_background(self, area, event):
        self.selected_chit = None
        self.unselect_all()
        if not self.game or not self.game.battle_active_player:
            return
        if self.game.battle_phase == Phase.MANEUVER:
            if self.game.battle_active_player.name == self.playername:
                self.highlight_mobile_chits()
        elif (self.game.battle_phase == Phase.STRIKE
          or self.game.battle_phase == Phase.COUNTERSTRIKE):
            if self.game.battle_active_player.name == self.playername:
                self.highlight_strikers()

    def clicked_on_hex(self, area, event, guihex):
        if not self.game:
            guihex.selected = not guihex.selected
            self.repaint(hexlabels=[guihex.battlehex.label])
            return
        phase = self.game.battle_phase
        if phase == Phase.MANEUVER:
            if self.selected_chit is not None and guihex.selected:
                creature = self.selected_chit.creature
                def1 = self.user.callRemote("move_creature",
                  self.game.name, creature.name, creature.hexlabel,
                  guihex.battlehex.label)
                def1.addErrback(self.failure)
            self.selected_chit = None
            self.unselect_all()
            if (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                self.highlight_mobile_chits()

        elif phase == Phase.STRIKE or phase == Phase.COUNTERSTRIKE:
            self.highlight_strikers()

    def clicked_on_chit(self, area, event, chit):
        phase = self.game.battle_phase
        if phase == Phase.MANEUVER:
            creature = chit.creature
            legion = creature.legion
            player = legion.player
            if player.name != self.playername:
                return
            elif player != self.game.battle_active_player:
                return
            self.selected_chit = chit
            self.unselect_all()
            hexlabels = self.game.find_battle_moves(creature)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.repaint(hexlabels)

        elif phase == Phase.STRIKE or phase == Phase.COUNTERSTRIKE:
            creature = chit.creature
            legion = creature.legion
            player = legion.player
            guihex = self.guihexes[creature.hexlabel]

            if (player.name != self.playername and guihex.selected and
              self.pickcarry):
                # carrying to enemy creature
                self.picked_carry((creature, self.pickcarry.carries))

            elif (self.selected_chit is not None and player.name !=
              self.playername and guihex.selected):
                # striking enemy creature
                target = creature
                striker = self.selected_chit.creature
                if striker.can_take_strike_penalty(target):
                    _, def1 = PickStrikePenalty.new(self.playername,
                      self.game.name, striker, target, self.parent_window)
                    def1.addCallback(self.picked_strike_penalty)
                else:
                    num_dice = striker.number_of_dice(target)
                    strike_number = striker.strike_number(target)
                    self.strike(striker, target, num_dice, strike_number)

            else:
                # picking a striker
                if player.name != self.playername:
                    return
                if player != self.game.battle_active_player:
                    return
                self.selected_chit = chit
                self.unselect_all()
                hexlabels = creature.find_target_hexlabels()
                for hexlabel in hexlabels:
                    guihex = self.guihexes[hexlabel]
                    guihex.selected = True
                self.repaint(hexlabels)

    def _add_missing_chits(self):
        """Add chits for any creatures that lack them."""
        chit_creatures = set(chit.creature for chit in self.chits)
        for (legion, rotate) in [
          (self.game.attacker_legion, gtk.gdk.PIXBUF_ROTATE_CLOCKWISE),
          (self.game.defender_legion, gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)]:
            if legion:
                for creature in legion.creatures:
                    if creature not in chit_creatures and not creature.dead:
                        chit = Chit.Chit(creature, legion.player.color,
                          self.scale / 2, rotate=rotate)
                        self.chits.append(chit)

    def _remove_dead_chits(self):
        for chit in reversed(self.chits):
            if (chit.creature.dead or
              chit.creature.hexlabel in ["ATTACKER", "DEFENDER"]):
                self.chits.remove(chit)
                hexlabel = (chit.creature.hexlabel or
                  chit.creature.previous_hexlabel)
                chit.hexlabel = None
                if hexlabel is not None:
                    self.repaint([hexlabel])
        self.attacker_graveyard.update_gui()
        self.defender_graveyard.update_gui()

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

    def _render_chit(self, chit, ctx):
        ctx.set_source_surface(chit.surface, int(round(chit.location[0])),
          int(round(chit.location[1])))
        ctx.paint()

    def chits_in_hex(self, hexlabel):
        """Return a list of all Chits found in the hex with hexlabel."""
        return [chit for chit in self.chits
          if chit.creature.hexlabel == hexlabel]

    def draw_chits(self, ctx):
        if not self.game:
            return
        self._add_missing_chits()
        hexlabels = set([chit.creature.hexlabel for chit in self.chits])
        for hexlabel in hexlabels:
            if hexlabel is not None:
                self._compute_chit_locations(hexlabel)
                chits = self.chits_in_hex(hexlabel)
                for chit in chits:
                    self._render_chit(chit, ctx)

    def cb_undo(self, action):
        if self.game:
            history = self.game.history
            if history.can_undo(self.playername):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action",
                  last_action.undo_action())
                def1.addErrback(self.failure)

    def cb_undo_all(self, action):
        if self.game:
            history = self.game.history
            if history.can_undo(self.playername):
                last_action = history.actions[-1]
                def1 = self.user.callRemote("apply_action",
                  last_action.undo_action())
                def1.addCallback(self.cb_undo_all)
                def1.addErrback(self.failure)

    def cb_redo(self, action):
        if self.game:
            history = self.game.history
            if history.can_redo(self.playername):
                action = history.undone[-1]
                def1 = self.user.callRemote("apply_action", action)
                def1.addErrback(self.failure)

    def cb_done(self, action):
        if not self.game:
            return
        player = self.game.get_player_by_name(self.playername)
        if player == self.game.battle_active_player:
            if self.game.battle_phase == Phase.REINFORCE:
                def1 = self.user.callRemote("done_with_reinforcements",
                  self.game.name)
                def1.addErrback(self.failure)
            elif self.game.battle_phase == Phase.MANEUVER:
                def1 = self.user.callRemote("done_with_maneuvers",
                  self.game.name)
                def1.addErrback(self.failure)
            elif self.game.battle_phase == Phase.STRIKE:
                if not self.game.battle_active_legion.forced_strikes:
                    def1 = self.user.callRemote("done_with_strikes",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(self.parent_window, "Info",
                      "Forced strikes remain")
            elif self.game.battle_phase == Phase.COUNTERSTRIKE:
                if not self.game.battle_active_legion.forced_strikes:
                    def1 = self.user.callRemote("done_with_counterstrikes",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(self.parent_window, "Info",
                      "Forced strikes remain")

    def cb_concede(self, event):
        for legion in self.game.battle_legions:
            if legion.player.name == self.playername:
                confirm_dialog, def1 = ConfirmDialog.new(self.parent_window,
                  "Confirm", "Are you sure you want to concede?")
                def1.addCallback(self.cb_concede2)
                def1.addErrback(self.failure)

    def cb_concede2(self, confirmed):
        logging.info("cb_concede2 %s", confirmed)
        if confirmed:
            for legion in self.game.battle_legions:
                if legion.player.name == self.playername:
                    friend = legion
                else:
                    enemy = legion
            def1 = self.user.callRemote("concede", self.game.name,
              friend.markerid, enemy.markerid, friend.hexlabel)
            def1.addErrback(self.failure)

    def cb_about(self, action):
        About.About(self.parent_window)

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
        if not self.area or not self.area.get_window():
            return
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
        ctx.set_line_width(round(0.2 * self.scale))
        ctx.rectangle(*clip_rect)
        ctx.clip()
        # white background, only when we get an event
        if event is not None:
            ctx.set_source_rgb(1, 1, 1)
            width, height = self.area.size_request()
            # Overdraw to avoid gray if window is enlarged.
            ctx.rectangle(0, 0, 2 * width, 2 * height)
            ctx.fill()
        for hexlabel in self.repaint_hexlabels:
            ctx.set_source_rgb(1, 1, 1)
            guihex = self.guihexes[hexlabel]
            x, y, width, height = guihex.bounding_rect
            ctx.rectangle(x, y, width, height)
            ctx.fill()
        for guihex in self.guihexes.itervalues():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)
        self.draw_chits(ctx)

        ctx2 = self.area.get_window().cairo_create()
        ctx2.set_source_surface(surface)
        ctx2.paint()

        self.repaint_hexlabels.clear()

    def repaint_all(self):
        for hexlabel in self.guihexes:
            self.repaint_hexlabels.add(hexlabel)
        self.update_gui()

    def repaint(self, hexlabels=None):
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)

    def build_chit_image(self, hexlabel):
        for chit in self.chits:
            if chit.creature.hexlabel == hexlabel:
                chit.build_image()
        self.repaint([hexlabel])

    def update(self, observed, action, names):
        logging.info("GUIBattleMap.update %s %s %s", observed, action, names)

        if isinstance(action, Action.MoveCreature) or isinstance(action,
          Action.UndoMoveCreature):
            for hexlabel in [action.old_hexlabel, action.new_hexlabel]:
                if hexlabel is not None:
                    self.repaint_hexlabels.add(hexlabel)
            self.repaint([action.old_hexlabel, action.new_hexlabel])
            self.highlight_mobile_chits()

        elif isinstance(action, Action.StartManeuverBattlePhase):
            self.highlight_mobile_chits()
            if (self.game and self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                if not self.game.battle_active_legion.mobile_creatures:
                    def1 = self.user.callRemote("done_with_maneuvers",
                      self.game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.StartStrikeBattlePhase):
            self.highlight_strikers()
            if (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    def1 = self.user.callRemote("done_with_strikes",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.Strike):
            if self.pickcarry is not None:
                self.pickcarry.destroy()
                self.pickcarry = None
            if action.hits > 0:
                self.build_chit_image(action.target_hexlabel)
            self.highlight_strikers()
            if (action.carries and self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                striker = self.game.creatures_in_battle_hex(
                  action.striker_hexlabel).pop()
                assert striker.name == action.striker_name
                target = self.game.creatures_in_battle_hex(
                  action.target_hexlabel).pop()
                assert target.name == action.target_name
                num_dice = action.num_dice
                strike_number = action.strike_number
                carries = action.carries

                if self._do_auto_carry(striker, target, num_dice,
                  strike_number, carries):
                    return
                self.pickcarry, def1 = PickCarry.new(self.playername,
                  self.game.name, striker, target, num_dice, strike_number,
                  carries, self.parent_window)
                def1.addCallback(self.picked_carry)
                self.unselect_all()
                for creature in striker.carry_targets(target, num_dice,
                  strike_number):
                    self.guihexes[creature.hexlabel].selected = True
                    self.repaint([creature.hexlabel])
            elif (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    if self.game.battle_phase == Phase.STRIKE:
                        def1 = self.user.callRemote("done_with_strikes",
                          self.game.name)
                        def1.addErrback(self.failure)
                    else:
                        def1 = self.user.callRemote("done_with_counterstrikes",
                          self.game.name)
                        def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.DriftDamage):
            self.build_chit_image(action.target_hexlabel)

        elif isinstance(action, Action.Carry):
            if self.pickcarry is not None:
                self.pickcarry.destroy()
                self.pickcarry = None
            if action.carries > 0:
                self.build_chit_image(action.carry_target_hexlabel)
            self.highlight_strikers()
            if (action.carries_left and self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                striker = self.game.creatures_in_battle_hex(
                  action.striker_hexlabel).pop()
                assert striker.name == action.striker_name
                target = self.game.creatures_in_battle_hex(
                  action.target_hexlabel).pop()
                carry_target = self.game.creatures_in_battle_hex(
                  action.carry_target_hexlabel).pop()
                assert carry_target.name == action.carry_target_name
                num_dice = action.num_dice
                strike_number = action.strike_number
                carries_left = action.carries_left
                if self._do_auto_carry(striker, target, num_dice,
                  strike_number, carries_left):
                    return
                self.pickcarry, def1 = PickCarry.new(self.playername,
                  self.game.name, striker, target, num_dice, strike_number,
                  carries_left, self.parent_window)
                def1.addCallback(self.picked_carry)
                self.unselect_all()
                for creature in striker.carry_targets(target, num_dice,
                  strike_number):
                    self.guihexes[creature.hexlabel].selected = True
                    self.repaint([creature.hexlabel])
            elif (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    if self.game.battle_phase == Phase.STRIKE:
                        def1 = self.user.callRemote("done_with_strikes",
                          self.game.name)
                        def1.addErrback(self.failure)
                    else:
                        def1 = self.user.callRemote("done_with_counterstrikes",
                          self.game.name)
                        def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            self.highlight_strikers()
            if (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                if not self.game.battle_active_legion.strikers:
                    def1 = self.user.callRemote("done_with_counterstrikes",
                      self.game.name)
                    def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.StartReinforceBattlePhase):
            self._remove_dead_chits()
            if (self.game.battle_turn == 4 and
              self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername and
              self.game.battle_active_legion == self.game.defender_legion):
                legion = self.game.defender_legion
                caretaker = self.game.caretaker
                hexlabel = legion.hexlabel
                mterrain = self.game.board.hexes[hexlabel].terrain
                if legion.can_recruit:
                    logging.info("PickRecruit.new (battle turn 4)")
                    _, def1 = PickRecruit.new(self.playername, legion,
                      mterrain, caretaker, self.parent_window)
                    def1.addCallback(self.picked_reinforcement)
                else:
                    def1 = self.user.callRemote("done_with_reinforcements",
                      self.game.name)
                    def1.addErrback(self.failure)

            elif (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername and
              self.game.battle_active_legion == self.game.attacker_legion):
                legion = self.game.attacker_legion
                if (legion.can_summon and self.game.first_attacker_kill in
                  [self.game.battle_turn - 1, self.game.battle_turn]):
                    self.game.first_attacker_kill = -1
                    _, def1 = SummonAngel.new(self.playername, legion,
                      self.parent_window)
                    def1.addCallback(self.picked_summon)
                else:
                    def1 = self.user.callRemote("done_with_reinforcements",
                      self.game.name)
                    def1.addErrback(self.failure)

            elif (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                def1 = self.user.callRemote("done_with_reinforcements",
                  self.game.name)
                def1.addErrback(self.failure)

        elif (isinstance(action, Action.BattleOver) or
          isinstance(action, Action.ResolvingEngagement) or
          isinstance(action, Action.StartMusterPhase)):
            self.destroy()

        elif isinstance(action, Action.RecruitCreature):
            if (self.game.defender_legion and
              self.game.defender_legion.creatures):
                self.game.defender_legion.creatures[-1].hexlabel = "DEFENDER"
                self.repaint(["DEFENDER"])
                if (self.game.battle_active_player and
                  self.game.battle_active_player.name == self.playername):
                    def1 = self.user.callRemote("done_with_reinforcements",
                      self.game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotReinforce):
            if (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                def1 = self.user.callRemote("done_with_reinforcements",
                  self.game.name)
                def1.addErrback(self.failure)

        elif isinstance(action, Action.SummonAngel):
            if (self.game.attacker_legion and
              self.game.attacker_legion.creatures):
                self.game.attacker_legion.creatures[-1].hexlabel = "ATTACKER"
                self.repaint(["ATTACKER"])
                if (self.game.battle_active_player and
                  self.game.battle_active_player.name == self.playername):
                    def1 = self.user.callRemote("done_with_reinforcements",
                      self.game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotSummonAngel):
            if (self.game.battle_active_player and
              self.game.battle_active_player.name == self.playername):
                def1 = self.user.callRemote("done_with_reinforcements",
                  self.game.name)
                def1.addErrback(self.failure)

        elif isinstance(action, Action.Concede):
            for legion in self.game.battle_legions:
                if legion.markerid == action.markerid:
                    break
            self.repaint([creature.hexlabel for creature in legion.creatures])

        elif isinstance(action, Action.UnReinforce):
            self.repaint(["DEFENDER"])

        elif isinstance(action, Action.UnsummonAngel):
            self.repaint(["ATTACKER"])

    def picked_reinforcement(self, (legion, creature, recruiter_names)):
        if legion and creature:
            def1 = self.user.callRemote("recruit_creature", self.game.name,
              legion.markerid, creature.name, recruiter_names)
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("done_with_reinforcements",
              self.game.name)
            def1.addErrback(self.failure)

    def picked_summon(self, (legion, donor, creature)):
        if legion and donor and creature:
            def1 = self.user.callRemote("summon_angel", self.game.name,
              legion.markerid, donor.markerid, creature.name)
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("done_with_reinforcements",
              self.game.name)
            def1.addErrback(self.failure)

    def picked_carry(self, (carry_target, carries)):
        logging.info("picked_carry %s %s", carry_target, carries)
        if self.pickcarry is not None:
            self.pickcarry.destroy()
        self.pickcarry = None
        def1 = self.user.callRemote("carry", self.game.name,
          carry_target.name, carry_target.hexlabel, carries)
        def1.addErrback(self.failure)

    def picked_strike_penalty(self, (striker, target, num_dice,
      strike_number)):
        logging.info("picked_strike_penalty %s %s %s %s", striker, target,
          num_dice, strike_number)
        if striker is None:
            # User cancelled the strike.
            self.unselect_all()
            self.highlight_strikers()
            self.repaint_all()
        else:
            def1 = self.user.callRemote("strike", self.game.name, striker.name,
              striker.hexlabel, target.name, target.hexlabel, num_dice,
              strike_number)
            def1.addErrback(self.failure)

    def failure(self, arg):
        log.err(arg)


if __name__ == "__main__":
    import random
    from slugathon.game import BattleMap
    from slugathon.data import battlemapdata

    window = gtk.Window()
    window.set_default_size(1024, 768)

    entry_side = None
    if len(argv) > 1:
        terrain = argv[1].title()
        if len(argv) > 2:
            entry_side = int(argv[2])
    else:
        terrain = random.choice(battlemapdata.data.keys())
    if entry_side is None:
        if terrain == "Tower":
            entry_side = 5
        else:
            entry_side = random.choice([1, 3, 5])
    battlemap = BattleMap.BattleMap(terrain, entry_side)
    guimap = GUIBattleMap(battlemap)
    window.add(guimap)
    window.show_all()
    guimap.connect("destroy", lambda x: reactor.stop())
    reactor.run()
