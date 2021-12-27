#!/usr/bin/env python3

from __future__ import annotations

import logging
import math
from sys import argv, maxsize
from typing import Any, List, Optional, Set, Tuple

import cairo
import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implementer

from slugathon.game import (
    Action,
    BattleMap,
    Creature,
    Game,
    Legion,
    MasterHex,
    Phase,
)
from slugathon.gui import (
    About,
    BattleDice,
    Chit,
    ConfirmDialog,
    EventLog,
    Graveyard,
    GUIBattleHex,
    InfoDialog,
    Marker,
    PickCarry,
    PickRecruit,
    PickStrikePenalty,
    SummonAngel,
    TurnTrack,
)
from slugathon.net import User
from slugathon.util import guiutils, prefs
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


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
class GUIBattleMap(Gtk.EventBox):

    """GUI representation of a battlemap."""

    def __init__(
        self,
        battlemap: BattleMap.BattleMap,
        game: Optional[Game.Game] = None,
        user: Optional[User.User] = None,
        playername: Optional[str] = None,
        scale: Optional[int] = None,
        parent_window: Optional[Gtk.Window] = None,
    ):
        GObject.GObject.__init__(self)

        self.battlemap = battlemap
        self.game = game
        self.user = user
        self.playername = playername
        self.parent_window = parent_window

        self.chits = []  # type: List[Chit.Chit]
        self.selected_chit = None  # type: Optional[Chit.Chit]

        self.vbox = Gtk.VBox(spacing=1)
        self.add(self.vbox)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = Gtk.DrawingArea()
        self.area.set_size_request(self.compute_width(), self.compute_height())

        gtkcolor = Gdk.color_parse("white")
        self.modify_bg(Gtk.StateType.NORMAL, gtkcolor)

        if game and game.attacker_legion and game.defender_legion:
            self.turn_track = TurnTrack.TurnTrack(
                game.attacker_legion, game.defender_legion, game, self.scale
            )  # type: Optional[TurnTrack.TurnTrack]
            game.add_observer(self.turn_track)
            self.battle_dice = BattleDice.BattleDice(
                self.scale
            )  # type: Optional[BattleDice.BattleDice]
            game.add_observer(self.battle_dice)
            event_log = EventLog.EventLog(game, self.playername)
            game.add_observer(event_log)
            self.attacker_graveyard = Graveyard.Graveyard(
                game.attacker_legion
            )  # type: Optional[Graveyard.Graveyard]
            self.defender_graveyard = Graveyard.Graveyard(
                game.defender_legion
            )  # type: Optional[Graveyard.Graveyard]
        else:
            self.turn_track = None
            self.battle_dice = None
            self.attacker_graveyard = None
            self.defender_graveyard = None

        self.create_ui()
        self.vbox.pack_start(self.ui.get_widget("/Menubar"), True, True, 0)
        self.vbox.pack_start(self.ui.get_widget("/Toolbar"), True, True, 0)
        self.hbox1 = Gtk.HBox()
        self.hbox2 = Gtk.HBox()
        self.hbox3 = Gtk.HBox()
        self.hbox4 = Gtk.HBox()
        self.hbox5 = Gtk.HBox(homogeneous=True)
        self.vbox.pack_start(self.hbox1, False, True, 0)
        self.vbox.pack_start(self.hbox2, True, True, 0)
        self.vbox.pack_start(self.hbox3, False, True, 0)
        self.vbox.pack_start(self.hbox4, False, True, 0)
        self.vbox.pack_start(self.hbox5, False, True, 0)
        if game:
            self.vbox.pack_start(event_log, True, True, 0)
            gtkcolor = Gdk.color_parse("white")
            assert game.attacker_legion is not None
            attacker_marker = Marker.Marker(
                game.attacker_legion, True, self.scale // 2
            )
            attacker_marker.event_box.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
            assert game.defender_legion is not None
            defender_marker = Marker.Marker(
                game.defender_legion, True, self.scale // 2
            )
            defender_marker.event_box.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
            board = game.board
            hexlabel = game.defender_legion.hexlabel
            masterhex = board.hexes[hexlabel]
            own_hex_label = self.masterhex_label(masterhex, "xx-large")
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(own_hex_label, True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox1.pack_start(self.build_spacer(), True, True, 0)
            self.hbox3.pack_start(self.turn_track, False, True, 0)
            self.hbox3.pack_start(self.battle_dice, True, True, 0)
            self.hbox2.pack_start(attacker_marker.event_box, True, True, 0)
        self.hbox2.pack_start(self.area, True, True, 0)
        if game:
            self.hbox2.pack_start(defender_marker.event_box, True, True, 0)
            self.hbox5.pack_start(self.attacker_graveyard, True, True, 0)
            self.hbox5.pack_start(self.defender_graveyard, True, True, 0)

        self.guihexes = {}
        for hex1 in self.battlemap.hexes.values():
            self.guihexes[hex1.label] = GUIBattleHex.GUIBattleHex(hex1, self)
        self.repaint_hexlabels = set()  # type: Set[str]

        self.area.connect("draw", self.cb_area_expose)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)
        self.show_all()
        if (
            self.game
            and self.game.battle_active_player
            and self.game.battle_active_player.name == self.playername
        ):
            self.highlight_mobile_chits()
        self.pickcarry = None  # type: Optional[PickCarry.PickCarry]

    def create_ui(self) -> None:
        ag = Gtk.ActionGroup(name="BattleActions")
        actions = [
            ("PhaseMenu", None, "_Phase"),
            ("Done", Gtk.STOCK_APPLY, "_Done", "d", "Done", self.cb_done),
            ("Undo", Gtk.STOCK_UNDO, "_Undo", "u", "Undo", self.cb_undo),
            (
                "Undo All",
                Gtk.STOCK_DELETE,
                "Undo _All",
                "a",
                "Undo All",
                self.cb_undo_all,
            ),
            ("Redo", Gtk.STOCK_REDO, "_Redo", "r", "Redo", self.cb_redo),
            (
                "Concede Battle",
                None,
                "_Concede Battle",
                "<control>C",
                "Concede Battle",
                self.cb_concede,
            ),
            ("HelpMenu", None, "_Help"),
            ("About", Gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        self.ui = Gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)

    def compute_scale(self) -> int:
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = Gdk.Screen.width()
        height = Gdk.Screen.height()
        # Fudge factor to leave room on the sides.
        xscale = width / (2 * self.battlemap.hex_width) - 18
        # Fudge factor for menus and toolbars.
        yscale = height / (2 * SQRT3 * self.battlemap.hex_height) - 22
        return int(min(xscale, yscale))

    def compute_width(self) -> int:
        """Return the width of the map in pixels."""
        return int(
            math.ceil(self.scale * (self.battlemap.hex_width + 1) * 3.2)
        )

    def compute_height(self) -> int:
        """Return the height of the map in pixels."""
        return int(
            (math.ceil(self.scale * self.battlemap.hex_height) * 2 * SQRT3)
        )

    def masterhex_label(
        self, masterhex: MasterHex.MasterHex, size: str
    ) -> Gtk.EventBox:
        """Return a Gtk.Label describing masterhex, inside a white
        Gtk.EventBox."""
        eventbox = Gtk.EventBox()
        if masterhex:
            text = (
                f"<span size='{size}' weight='bold'>{masterhex.terrain} "
                f"hex {masterhex.label}</span>"
            )
        else:
            text = ""
        label = Gtk.Label()
        label.set_markup(text)
        eventbox.add(label)
        gtkcolor = Gdk.color_parse("white")
        eventbox.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
        return eventbox

    def build_spacer(self) -> Gtk.EventBox:
        """Return a white Gtk.EventBox."""
        eventbox = Gtk.EventBox()
        gtkcolor = Gdk.color_parse("white")
        eventbox.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
        return eventbox

    def unselect_all(self) -> None:
        """Unselect all guihexes."""
        for hexlabel, guihex in self.guihexes.items():
            if guihex.selected:
                guihex.selected = False
                self.repaint_hexlabels.add(hexlabel)
        self.repaint()

    def highlight_mobile_chits(self) -> None:
        """Highlight the hexes containing all creatures that can move now."""
        if not self.game:
            return
        if (
            not self.game.battle_active_player
            or self.game.battle_active_player.name != self.playername
            or self.game.battle_active_legion is None
        ):
            self.unselect_all()
            return
        hexlabels = set()
        for creature in self.game.battle_active_legion.mobile_creatures:
            assert creature.hexlabel is not None
            hexlabels.add(creature.hexlabel)
        self.unselect_all()
        for hexlabel in hexlabels:
            self.guihexes[hexlabel].selected = True
        self.repaint(hexlabels)

    def highlight_strikers(self) -> None:
        """Highlight the hexes containing creatures that can strike now."""
        if not self.game:
            return
        if (
            not self.game.battle_active_player
            or self.game.battle_active_player.name != self.playername
        ):
            self.unselect_all()
            return
        hexlabels = set()
        assert self.game.battle_active_legion is not None
        for creature in self.game.battle_active_legion.strikers:
            if creature.hexlabel is not None:
                hexlabels.add(creature.hexlabel)
        self.unselect_all()
        for hexlabel in hexlabels:
            self.guihexes[hexlabel].selected = True
        self.repaint(hexlabels)

    def strike(
        self,
        striker: Creature.Creature,
        target: Creature.Creature,
        num_dice: int,
        strike_number: int,
    ) -> None:
        """Have striker strike target."""
        assert self.game is not None
        def1 = self.user.callRemote(  # type: ignore
            "strike",
            self.game.name,
            striker.name,
            striker.hexlabel,
            target.name,
            target.hexlabel,
            num_dice,
            strike_number,
        )
        def1.addErrback(self.failure)

    def _do_auto_strike(self) -> bool:
        """Do an automatic strike if appropriate.

        Return True iff we did one.
        """
        assert self.game is not None
        assert self.playername is not None
        auto_strike = prefs.load_bool_option(
            self.playername, prefs.AUTO_STRIKE_SINGLE_TARGET
        )
        auto_rangestrike = prefs.load_bool_option(
            self.playername, prefs.AUTO_RANGESTRIKE_SINGLE_TARGET
        )
        assert self.game.battle_active_legion is not None
        if auto_strike or auto_rangestrike:
            strikers = self.game.battle_active_legion.strikers
            for striker in strikers:
                hexlabels = striker.find_target_hexlabels()
                if len(hexlabels) == 1:
                    hexlabel = hexlabels.pop()
                    if (
                        auto_strike
                        and hexlabel
                        in striker.find_adjacent_target_hexlabels()
                    ) or (
                        auto_rangestrike
                        and hexlabel
                        in striker.find_rangestrike_target_hexlabels()
                    ):
                        chits = self.chits_in_hex(hexlabel)
                        assert len(chits) == 1
                        chit = chits[0]
                        target = chit.creature
                        assert target is not None
                        num_dice = striker.number_of_dice(target)
                        strike_number = striker.strike_number(target)
                        self.strike(striker, target, num_dice, strike_number)
                        return True
        return False

    def _do_auto_carry(
        self,
        striker: Creature.Creature,
        target: Creature.Creature,
        num_dice: int,
        strike_number: int,
        carries: int,
    ) -> bool:
        """Automatically carry if appropriate.

        Return True iff we carried.
        """
        assert self.game is not None
        assert self.playername is not None
        auto_carry = prefs.load_bool_option(
            self.playername, prefs.AUTO_CARRY_TO_SINGLE_TARGET
        )
        if auto_carry:
            carry_targets = striker.carry_targets(
                target, num_dice, strike_number
            )
            if len(carry_targets) == 1:
                carry_target = carry_targets.pop()
                def1 = self.user.callRemote(  # type: ignore
                    "carry",
                    self.game.name,
                    carry_target.name,
                    carry_target.hexlabel,
                    carries,
                )
                def1.addErrback(self.failure)
                return True
        return False

    def cb_area_expose(
        self, area: Gtk.DrawingArea, event: cairo.Context
    ) -> bool:
        self.update_gui(event=event)
        return True

    def cb_click(self, area: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        for chit in self.chits:
            if chit.point_inside((event.x, event.y)):
                self.clicked_on_chit(area, event, chit)
                return True
        for guihex in self.guihexes.values():
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

    def clicked_on_background(
        self, area: Gtk.DrawingArea, event: Gdk.EventButton
    ) -> None:
        self.selected_chit = None
        self.unselect_all()
        if not self.game or not self.game.battle_active_player:
            return
        if self.game.battle_phase == Phase.MANEUVER:
            if self.game.battle_active_player.name == self.playername:
                self.highlight_mobile_chits()
        elif (
            self.game.battle_phase == Phase.STRIKE
            or self.game.battle_phase == Phase.COUNTERSTRIKE
        ):
            if self.game.battle_active_player.name == self.playername:
                self.highlight_strikers()

    def clicked_on_hex(
        self,
        area: Gtk.DrawingArea,
        event: Gdk.EventButton,
        guihex: GUIBattleHex.GUIBattleHex,
    ) -> None:
        if not self.game:
            guihex.selected = not guihex.selected
            self.repaint(hexlabels={guihex.battlehex.label})
            return
        phase = self.game.battle_phase
        if phase == Phase.MANEUVER:
            if self.selected_chit is not None and guihex.selected:
                creature = self.selected_chit.creature
                if creature is not None:
                    def1 = self.user.callRemote(  # type: ignore
                        "move_creature",
                        self.game.name,
                        creature.name,
                        creature.hexlabel,
                        guihex.battlehex.label,
                    )
                    def1.addErrback(self.failure)
            self.selected_chit = None
            self.unselect_all()
            if (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                self.highlight_mobile_chits()

        elif phase == Phase.STRIKE or phase == Phase.COUNTERSTRIKE:
            self.highlight_strikers()

    def clicked_on_chit(
        self, area: Gtk.DrawingArea, event: Gdk.EventButton, chit: Chit.Chit
    ) -> None:
        assert self.game is not None
        phase = self.game.battle_phase
        if phase == Phase.MANEUVER:
            creature = chit.creature
            assert creature is not None
            legion = creature.legion
            assert legion is not None
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
            assert creature is not None
            assert creature.hexlabel is not None
            legion = creature.legion
            assert legion is not None
            player = legion.player
            guihex = self.guihexes[creature.hexlabel]

            if (
                player.name != self.playername
                and guihex.selected
                and self.pickcarry
            ):
                # carrying to enemy creature
                self.picked_carry((creature, self.pickcarry.carries))

            elif (
                self.selected_chit is not None
                and player.name != self.playername
                and guihex.selected
            ):
                # striking enemy creature
                target = creature
                striker = self.selected_chit.creature
                if striker is not None:
                    assert self.playername is not None
                    if striker.can_take_strike_penalty(target):
                        _, def1 = PickStrikePenalty.new(
                            self.playername,
                            self.game.name,
                            striker,
                            target,
                            self.parent_window,
                        )
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

    def _add_missing_chits(self) -> None:
        """Add chits for any creatures that lack them."""
        chit_creatures = set(chit.creature for chit in self.chits)
        assert self.game is not None
        for (legion, rotate) in [
            (self.game.attacker_legion, GdkPixbuf.PixbufRotation.CLOCKWISE),
            (
                self.game.defender_legion,
                GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE,
            ),
        ]:
            if legion:
                for creature in legion.creatures:
                    if creature not in chit_creatures and not creature.dead:
                        chit = Chit.Chit(
                            creature,
                            legion.player.color,
                            self.scale // 2,
                            rotate=rotate,
                        )
                        self.chits.append(chit)

    def _remove_dead_chits(self) -> None:
        for chit in reversed(self.chits):
            assert chit.creature is not None
            if (
                (chit.creature.dead)
                or (chit.creature.hexlabel in {"ATTACKER", "DEFENDER"})
                and self.game is not None
                and chit.creature.legion is not None
                and self.game.battle_active_player
                != chit.creature.legion.player
            ):
                self.chits.remove(chit)
                hexlabel = (
                    chit.creature.hexlabel or chit.creature.previous_hexlabel
                )
                chit.creature.hexlabel = None
                if hexlabel is not None:
                    self.repaint({hexlabel})
        assert self.attacker_graveyard is not None
        self.attacker_graveyard.update_gui()
        assert self.defender_graveyard is not None
        self.defender_graveyard.update_gui()

    def _compute_chit_locations(self, hexlabel: str) -> None:
        chits = self.chits_in_hex(hexlabel)
        num = len(chits)
        guihex = self.guihexes[hexlabel]
        chit_scale = self.chits[0].chit_scale
        bl = (
            guihex.center[0] - chit_scale / 2,
            guihex.center[1] - chit_scale / 2,
        )

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

    def _render_chit(self, chit: Chit.Chit, ctx: cairo.Context) -> None:
        assert chit.location is not None
        ctx.set_source_surface(
            chit.surface,
            int(round(chit.location[0])),
            int(round(chit.location[1])),
        )
        ctx.paint()

    def chits_in_hex(self, hexlabel: str) -> List[Chit.Chit]:
        """Return a list of all Chits found in the hex with hexlabel."""
        return [
            chit
            for chit in self.chits
            if chit.creature is not None and chit.creature.hexlabel == hexlabel
        ]

    def draw_chits(self, ctx: cairo.Context) -> None:
        if not self.game:
            return
        self._add_missing_chits()
        hexlabels = {
            chit.creature.hexlabel
            for chit in self.chits
            if chit.creature is not None
        }
        for hexlabel in hexlabels:
            if hexlabel is not None:
                self._compute_chit_locations(hexlabel)
                chits = self.chits_in_hex(hexlabel)
                for chit in chits:
                    self._render_chit(chit, ctx)

    def cb_undo(self, action: Action.Action) -> None:
        if self.game:
            history = self.game.history
            assert self.playername is not None
            if history.can_undo(self.playername):
                last_action = history.actions[-1]
                def1 = self.user.callRemote(  # type: ignore
                    "apply_action", last_action.undo_action()
                )
                def1.addErrback(self.failure)

    def cb_undo_all(self, action: Action.Action) -> None:
        if self.game:
            history = self.game.history
            assert self.playername is not None
            if history.can_undo(self.playername):
                last_action = history.actions[-1]
                def1 = self.user.callRemote(  # type: ignore
                    "apply_action", last_action.undo_action()
                )
                def1.addCallback(self.cb_undo_all)
                def1.addErrback(self.failure)

    def cb_redo(self, action: Action.Action) -> None:
        if self.game:
            history = self.game.history
            assert self.playername is not None
            if history.can_redo(self.playername):
                action = history.undone[-1]
                def1 = self.user.callRemote("apply_action", action)  # type: ignore
                def1.addErrback(self.failure)

    def cb_done(self, action: Action.Action) -> None:
        if not self.game:
            return
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        if player == self.game.battle_active_player:
            assert self.game.battle_active_legion is not None
            if self.game.battle_phase == Phase.REINFORCE:
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_reinforcements", self.game.name
                )
                def1.addErrback(self.failure)
            elif self.game.battle_phase == Phase.MANEUVER:
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_maneuvers", self.game.name
                )
                def1.addErrback(self.failure)
            elif self.game.battle_phase == Phase.STRIKE:
                if not self.game.battle_active_legion.forced_strikes:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_strikes", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(
                        self.parent_window, "Info", "Forced strikes remain"
                    )
            elif self.game.battle_phase == Phase.COUNTERSTRIKE:
                if not self.game.battle_active_legion.forced_strikes:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_counterstrikes", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(
                        self.parent_window, "Info", "Forced strikes remain"
                    )

    def cb_concede(self, event: Any) -> None:
        logging.debug(f"{event=}")
        if self.game:
            for legion in self.game.battle_legions:
                if legion.player.name == self.playername:
                    confirm_dialog, def1 = ConfirmDialog.new(
                        self.parent_window,
                        "Confirm",
                        "Are you sure you want to concede?",
                    )
                    def1.addCallback(self.cb_concede2)
                    def1.addErrback(self.failure)

    def cb_concede2(self, confirmed: bool) -> None:
        logging.info(f"cb_concede2 {confirmed}")
        assert self.game is not None
        if confirmed:
            for legion in self.game.battle_legions:
                if legion.player.name == self.playername:
                    friend = legion
                else:
                    enemy = legion
            def1 = self.user.callRemote(  # type: ignore
                "concede",
                self.game.name,
                friend.markerid,
                enemy.markerid,
                friend.hexlabel,
            )
            def1.addErrback(self.failure)

    def cb_about(self, action: Action.Action) -> None:
        About.About(self.parent_window)

    def bounding_rect_for_hexlabels(
        self, hexlabels: Set[str]
    ) -> Tuple[float, float, float, float]:
        """Return the minimum bounding rectangle that encloses all
        GUIMasterHexes whose hexlabels are given, as a tuple
        (x, y, width, height)
        """
        min_x = float(maxsize)
        max_x = float(-maxsize)
        min_y = float(maxsize)
        max_y = float(-maxsize)
        for hexlabel in hexlabels:
            try:
                guihex = self.guihexes[hexlabel]
                x, y, width, height = guihex.bounding_rect
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
            except KeyError:  # None check
                pass
        width = max_x - min_x
        height = max_y - min_y
        return min_x, min_y, width, height

    def update_gui(self, event: Optional[cairo.Context] = None) -> None:
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
                    self.repaint_hexlabels
                )
        else:
            if self.repaint_hexlabels:
                clip_rect = guiutils.combine_rectangles(
                    event.clip_extents(),
                    self.bounding_rect_for_hexlabels(self.repaint_hexlabels),
                )
            else:
                clip_rect = event.clip_extents()
        allocation = self.get_allocation()
        x = allocation.x
        y = allocation.y
        width = allocation.width
        height = allocation.height
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.set_line_width(round(0.2 * self.scale))
        ctx.rectangle(*clip_rect)
        ctx.clip()
        # white background, only when we get an event
        if event is not None:
            ctx.set_source_rgb(1, 1, 1)
            requisition = self.area.get_size_request()
            width = requisition.width
            height = requisition.height
            # Overdraw to avoid gray if window is enlarged.
            ctx.rectangle(0, 0, 2 * width, 2 * height)
            ctx.fill()
        for hexlabel in self.repaint_hexlabels:
            ctx.set_source_rgb(1, 1, 1)
            guihex = self.guihexes[hexlabel]
            x, y, width, height = guihex.bounding_rect
            ctx.rectangle(x, y, width, height)
            ctx.fill()
        for guihex in self.guihexes.values():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)
        self.draw_chits(ctx)

        ctx2 = self.area.get_window().cairo_create()
        ctx2.set_source_surface(surface)
        ctx2.paint()

        self.repaint_hexlabels.clear()

    def repaint_all(self) -> None:
        for hexlabel in self.guihexes:
            self.repaint_hexlabels.add(hexlabel)
        self.update_gui()

    def repaint(self, hexlabels: Optional[Set[str]] = None) -> None:
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)  # type: ignore

    def build_chit_image(self, hexlabel: str) -> None:
        for chit in self.chits:
            if chit.creature and chit.creature.hexlabel == hexlabel:
                chit.build_image()
        self.repaint({hexlabel})

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        logging.info(f"GUIBattleMap.update {observed} {action} {names}")

        if isinstance(action, Action.MoveCreature) or isinstance(
            action, Action.UndoMoveCreature
        ):
            for bhexlabel in [action.old_hexlabel, action.new_hexlabel]:
                if bhexlabel is not None:
                    self.repaint_hexlabels.add(bhexlabel)
            self.repaint({action.old_hexlabel, action.new_hexlabel})
            self.highlight_mobile_chits()

        elif isinstance(action, Action.StartManeuverBattlePhase):
            self.highlight_mobile_chits()
            if (
                self.game
                and self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
                and self.game.battle_active_legion
            ):
                if not self.game.battle_active_legion.mobile_creatures:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_maneuvers", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.StartStrikeBattlePhase):
            assert self.game is not None
            self.highlight_strikers()
            if (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
                and self.game.battle_active_legion
            ):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_strikes", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.Strike):
            assert self.game is not None
            if self.pickcarry is not None:
                self.pickcarry.destroy()
                self.pickcarry = None
            if action.hits > 0:
                self.build_chit_image(action.target_hexlabel)
            self.highlight_strikers()
            if (
                action.carries
                and self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                striker = self.game.creatures_in_battle_hex(
                    action.striker_hexlabel
                ).pop()
                assert striker.name == action.striker_name
                target = self.game.creatures_in_battle_hex(
                    action.target_hexlabel
                ).pop()
                assert target.name == action.target_name
                num_dice = action.num_dice
                strike_number = action.strike_number
                carries = action.carries

                if self._do_auto_carry(
                    striker, target, num_dice, strike_number, carries
                ):
                    return
                self.pickcarry, def1 = PickCarry.new(
                    self.playername,
                    self.game.name,
                    striker,
                    target,
                    num_dice,
                    strike_number,
                    carries,
                    self.parent_window,
                )
                def1.addCallback(self.picked_carry)
                self.unselect_all()
                for creature in striker.carry_targets(
                    target, num_dice, strike_number
                ):
                    assert creature.hexlabel is not None
                    self.guihexes[creature.hexlabel].selected = True
                    self.repaint({creature.hexlabel})
            elif (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
                and self.game.battle_active_legion is not None
            ):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    if self.game.battle_phase == Phase.STRIKE:
                        def1 = self.user.callRemote(  # type: ignore
                            "done_with_strikes", self.game.name
                        )
                        def1.addErrback(self.failure)
                    else:
                        def1 = self.user.callRemote(  # type: ignore
                            "done_with_counterstrikes", self.game.name
                        )
                        def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.DriftDamage):
            self.build_chit_image(action.target_hexlabel)

        elif isinstance(action, Action.Carry):
            assert self.game is not None
            assert self.game.battle_active_player is not None
            assert self.game.battle_active_legion is not None
            if self.pickcarry is not None:
                self.pickcarry.destroy()
                self.pickcarry = None
            if action.carries > 0:
                self.build_chit_image(action.carry_target_hexlabel)
            self.highlight_strikers()
            if (
                action.carries_left
                and self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                striker = self.game.creatures_in_battle_hex(
                    action.striker_hexlabel
                ).pop()
                assert striker.name == action.striker_name
                target = self.game.creatures_in_battle_hex(
                    action.target_hexlabel
                ).pop()
                carry_target = self.game.creatures_in_battle_hex(
                    action.carry_target_hexlabel
                ).pop()
                assert carry_target.name == action.carry_target_name
                num_dice = action.num_dice
                strike_number = action.strike_number
                carries_left = action.carries_left
                if self._do_auto_carry(
                    striker, target, num_dice, strike_number, carries_left
                ):
                    return
                self.pickcarry, def1 = PickCarry.new(
                    self.playername,
                    self.game.name,
                    striker,
                    target,
                    num_dice,
                    strike_number,
                    carries_left,
                    self.parent_window,
                )
                def1.addCallback(self.picked_carry)
                self.unselect_all()
                for creature in striker.carry_targets(
                    target, num_dice, strike_number
                ):
                    assert creature.hexlabel is not None
                    self.guihexes[creature.hexlabel].selected = True
                    self.repaint({creature.hexlabel})
            elif (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                strikers = self.game.battle_active_legion.strikers
                if not strikers:
                    if self.game.battle_phase == Phase.STRIKE:
                        def1 = self.user.callRemote(  # type: ignore
                            "done_with_strikes", self.game.name
                        )
                        def1.addErrback(self.failure)
                    else:
                        def1 = self.user.callRemote(  # type: ignore
                            "done_with_counterstrikes", self.game.name
                        )
                        def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            assert self.game is not None
            self.highlight_strikers()
            if (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                assert self.game.battle_active_legion is not None
                if not self.game.battle_active_legion.strikers:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_counterstrikes", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    self._do_auto_strike()

        elif isinstance(action, Action.StartReinforceBattlePhase):
            assert self.game is not None
            self._remove_dead_chits()
            if (
                self.game.battle_turn == 4
                and self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
                and self.game.battle_active_legion == self.game.defender_legion
            ):
                legion = self.game.defender_legion
                assert legion is not None
                caretaker = self.game.caretaker
                mhexlabel = legion.hexlabel
                mterrain = self.game.board.hexes[mhexlabel].terrain
                if legion.can_recruit:
                    logging.info("PickRecruit.new (battle turn 4)")
                    _, def1 = PickRecruit.new(
                        self.playername,
                        legion,
                        mterrain,
                        caretaker,
                        self.parent_window,
                    )
                    def1.addCallback(self.picked_reinforcement)
                else:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_reinforcements", self.game.name
                    )
                    def1.addErrback(self.failure)

            elif (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
                and self.game.battle_active_legion == self.game.attacker_legion
            ):
                assert self.game.battle_turn is not None
                legion = self.game.attacker_legion
                assert legion is not None
                if legion.can_summon and self.game.first_attacker_kill in [
                    self.game.battle_turn - 1,
                    self.game.battle_turn,
                ]:
                    self.game.first_attacker_kill = -1
                    _, def1 = SummonAngel.new(
                        self.playername, legion, self.parent_window
                    )
                    def1.addCallback(self.picked_summon)
                else:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_reinforcements", self.game.name
                    )
                    def1.addErrback(self.failure)

            elif (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_reinforcements", self.game.name
                )
                def1.addErrback(self.failure)

        elif (
            isinstance(action, Action.BattleOver)
            or isinstance(action, Action.ResolvingEngagement)
            or isinstance(action, Action.StartMusterPhase)
        ):
            self.destroy()

        elif isinstance(action, Action.RecruitCreature):
            assert self.game is not None
            if (
                self.game.defender_legion
                and self.game.defender_legion.creatures
            ):
                self.game.defender_legion.creatures[-1].hexlabel = "DEFENDER"
                self.repaint({"DEFENDER"})
                if (
                    self.game.battle_active_player
                    and self.game.battle_active_player.name == self.playername
                ):
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_reinforcements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotReinforce):
            assert self.game is not None
            if (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_reinforcements", self.game.name
                )
                def1.addErrback(self.failure)

        elif isinstance(action, Action.SummonAngel):
            assert self.game is not None
            if (
                self.game.attacker_legion
                and self.game.attacker_legion.creatures
            ):
                self.game.attacker_legion.creatures[-1].hexlabel = "ATTACKER"
                self.repaint({"ATTACKER"})
                if (
                    self.game.battle_active_player
                    and self.game.battle_active_player.name == self.playername
                ):
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_reinforcements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotSummonAngel):
            assert self.game is not None
            if (
                self.game.battle_active_player
                and self.game.battle_active_player.name == self.playername
            ):
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_reinforcements", self.game.name
                )
                def1.addErrback(self.failure)

        elif isinstance(action, Action.Concede):
            assert self.game is not None
            for legion in self.game.battle_legions:
                if legion.markerid == action.markerid:
                    break
            self.repaint(
                {
                    creature.hexlabel
                    for creature in legion.creatures
                    if creature.hexlabel is not None
                }
            )

        elif isinstance(action, Action.UnReinforce):
            self.repaint({"DEFENDER"})

        elif isinstance(action, Action.UnsummonAngel):
            self.repaint({"ATTACKER"})

    def picked_reinforcement(
        self, tup: Tuple[Legion.Legion, Creature.Creature, List[str]]
    ) -> None:
        (legion, creature, recruiter_names) = tup
        assert self.game is not None
        if legion and creature:
            def1 = self.user.callRemote(  # type: ignore
                "recruit_creature",
                self.game.name,
                legion.markerid,
                creature.name,
                recruiter_names,
            )
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote(  # type: ignore
                "done_with_reinforcements", self.game.name
            )
            def1.addErrback(self.failure)

    def picked_summon(
        self, tup1: Tuple[Legion.Legion, Legion.Legion, Creature.Creature]
    ) -> None:
        (legion, donor, creature) = tup1
        assert self.game is not None
        if legion and donor and creature:
            def1 = self.user.callRemote(  # type: ignore
                "summon_angel",
                self.game.name,
                legion.markerid,
                donor.markerid,
                creature.name,
            )
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote(  # type: ignore
                "done_with_reinforcements", self.game.name
            )
            def1.addErrback(self.failure)

    def picked_carry(self, tup2: Tuple[Creature.Creature, int]) -> None:
        (carry_target, carries) = tup2
        logging.info(f"picked_carry {carry_target} {carries}")
        assert self.game is not None
        if self.pickcarry is not None:
            self.pickcarry.destroy()
        self.pickcarry = None
        def1 = self.user.callRemote(  # type: ignore
            "carry",
            self.game.name,
            carry_target.name,
            carry_target.hexlabel,
            carries,
        )
        def1.addErrback(self.failure)

    def picked_strike_penalty(
        self, tup3: Tuple[Creature.Creature, Creature.Creature, int, int]
    ) -> None:
        (striker, target, num_dice, strike_number) = tup3
        logging.info(
            f"picked_strike_penalty {striker} {target} {num_dice} "
            "{strike_number}"
        )
        assert self.game is not None
        if striker is None:
            # User cancelled the strike.
            self.unselect_all()
            self.highlight_strikers()
            self.repaint_all()
        else:
            def1 = self.user.callRemote(  # type: ignore
                "strike",
                self.game.name,
                striker.name,
                striker.hexlabel,
                target.name,
                target.hexlabel,
                num_dice,
                strike_number,
            )
            def1.addErrback(self.failure)

    def failure(self, arg: Any) -> None:
        log.err(arg)  # type: ignore


if __name__ == "__main__":
    import random
    from slugathon.data import battlemapdata

    window = Gtk.Window()
    window.set_default_size(1024, 768)

    entry_side = None
    if len(argv) > 1:
        terrain = argv[1].title()
        if len(argv) > 2:
            entry_side = int(argv[2])
    else:
        terrain = random.choice(list(battlemapdata.data.keys()))
    if entry_side is None:
        if terrain == "Tower":
            entry_side = 5
        else:
            entry_side = random.choice([1, 3, 5])
    battlemap = BattleMap.BattleMap(terrain, entry_side)
    guimap = GUIBattleMap(battlemap)
    window.add(guimap)
    window.show_all()
    guimap.connect("destroy", lambda x: reactor.stop())  # type: ignore[attr-defined]
    reactor.run()  # type: ignore[attr-defined]
