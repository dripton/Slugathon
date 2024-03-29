#!/usr/bin/env python3

from __future__ import annotations

import logging
import math
from sys import maxsize
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import cairo
import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implementer

from slugathon.game import Action, Creature, Game, Legion, Phase
from slugathon.gui import (
    About,
    AcquireAngels,
    Chit,
    ConfirmDialog,
    Die,
    EventLog,
    Flee,
    GUIBattleMap,
    GUICaretaker,
    GUIMasterHex,
    InfoDialog,
    Inspector,
    Marker,
    Negotiate,
    PickEntrySide,
    PickMarker,
    PickMoveType,
    PickRecruit,
    PickTeleportingLord,
    Proposal,
    SplitLegion,
    StatusScreen,
    SummonAngel,
)
from slugathon.net import User
from slugathon.util import guiutils, prefs
from slugathon.util.bag import bag
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


SQRT3 = math.sqrt(3.0)


ui_string = f"""<ui>
  <menubar name="Menubar">
    <menu action="GameMenu">
      <menuitem action="Save"/>
      <menuitem action="Quit"/>
      <menuitem action="Withdraw"/>
    </menu>
    <menu action="PhaseMenu">
      <menuitem action="Done"/>
      <menuitem action="Undo"/>
      <menuitem action="Undo All"/>
      <menuitem action="Redo"/>
      <separator/>
      <menuitem action="Mulligan"/>
      <menuitem action="Clear Recruit Chits"/>
      <menuitem action="Pause AI"/>
      <menuitem action="Resume AI"/>
    </menu>
    <menu name="OptionsMenu" action="OptionsMenu">
      <menuitem action="{prefs.AUTO_STRIKE_SINGLE_TARGET}"/>
      <menuitem action="{prefs.AUTO_RANGESTRIKE_SINGLE_TARGET}"/>
      <menuitem action="{prefs.AUTO_CARRY_TO_SINGLE_TARGET}"/>
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
    <toolitem action="Pause AI"/>
    <toolitem action="Resume AI"/>
  </toolbar>
</ui>"""


@implementer(IObserver)
class GUIMasterBoard(Gtk.EventBox):

    """GUI representation of the masterboard."""

    def __init__(
        self,
        board: MasterBoard.MasterBoard,
        game: Optional[Game.Game] = None,
        user: Optional[User.User] = None,
        playername: Optional[str] = None,
        scale: Optional[int] = None,
        parent_window: Optional[Gtk.Window] = None,
    ):
        GObject.GObject.__init__(self)

        self.board = board
        self.user = user
        self.playername = playername
        self.game = game
        self.parent_window = parent_window

        self.connect("delete-event", self.cb_delete_event)
        self.connect("destroy", self.cb_destroy)

        self.hbox = Gtk.HBox()
        self.add(self.hbox)

        self.vbox = Gtk.VBox()
        self.hbox.pack_start(self.vbox, False, True, 0)
        self.vbox2 = Gtk.VBox()
        self.hbox.pack_start(self.vbox2, True, True, 0)

        self.create_ui()
        self.enable_pause_ai()
        self.vbox.pack_start(self.ui.get_widget("/Menubar"), False, False, 0)
        self.vbox.pack_start(self.ui.get_widget("/Toolbar"), False, False, 0)

        if scale is None:
            self.scale = self.compute_scale()  # type: int
        else:
            self.scale = scale
        self.area = Gtk.DrawingArea()
        self.area.set_size_request(self.compute_width(), self.compute_height())
        self.vbox.pack_start(self.area, False, True, 0)
        self.markers = []  # type: List[Marker.Marker]
        self.guihexes = {}  # type: Dict[int, GUIMasterHex.GUIMasterHex]
        # list of tuples (Chit, hexlabel)
        self.recruitchits = []  # type: List[Tuple[Chit.Chit, int]]
        for hex1 in self.board.hexes.values():
            self.guihexes[hex1.label] = GUIMasterHex.GUIMasterHex(hex1, self)
        self.selected_marker = None  # type: Optional[Marker.Marker]
        self.negotiate = None  # type: Optional[Negotiate.Negotiate]
        self.proposals = set()  # type: Set[Proposal.Proposal]
        self.guimap = None  # type: Optional[GUIBattleMap.GUIBattleMap]
        self.acquire_angels = (
            None
        )  # type: Optional[AcquireAngels.AcquireAngels]
        self.game_over = None  # type: Optional[InfoDialog.InfoDialog]
        self.guicaretaker = None  # type: Optional[GUICaretaker.GUICaretaker]
        self.status_screen = None  # type: Optional[StatusScreen.StatusScreen]
        self.inspector = None  # type: Optional[Inspector.Inspector]
        self.event_log = None  # type: Optional[EventLog.EventLog]
        self.destroyed = False

        # Set of hexlabels of hexes to redraw.
        # If set to all hexlabels then we redraw the whole window.
        # Used to combine nearly simultaneous redraws into one.
        self.repaint_hexlabels = set()  # type: Set[int]

        self.area.connect("draw", self.cb_area_expose)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)
        self.area.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.area.connect("motion-notify-event", self.cb_motion)
        self.show_all()

    def create_ui(self) -> None:
        ag = Gtk.ActionGroup(name="MasterActions")
        actions = [
            ("GameMenu", None, "_Game"),
            ("Save", Gtk.STOCK_SAVE, "_Save", "s", "Save", self.cb_save),
            (
                "Quit",
                Gtk.STOCK_QUIT,
                "_Quit",
                "<control>Q",
                "Quit program",
                self.cb_quit,
            ),
            (
                "Withdraw",
                Gtk.STOCK_DISCONNECT,
                "_Withdraw",
                "<control>W",
                "Withdraw from the game",
                self.cb_withdraw,
            ),
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
                "Mulligan",
                Gtk.STOCK_MEDIA_REWIND,
                "_Mulligan",
                "m",
                "Mulligan",
                self.cb_mulligan,
            ),
            (
                "Clear Recruit Chits",
                Gtk.STOCK_CLEAR,
                "_Clear Recruit Chits",
                "c",
                "Clear Recruit Chits",
                self.clear_all_recruitchits,
            ),
            (
                "Pause AI",
                Gtk.STOCK_MEDIA_PAUSE,
                "_Pause AI",
                "p",
                "Pause AI",
                self.pause_ai,
            ),
            (
                "Resume AI",
                Gtk.STOCK_MEDIA_PLAY,
                "_Resume AI",
                "",
                "Resume AI",
                self.resume_ai,
            ),
            ("OptionsMenu", None, "_Options"),
            ("HelpMenu", None, "_Help"),
            ("About", Gtk.STOCK_ABOUT, "_About", None, "About", self.cb_about),
        ]
        ag.add_actions(actions)
        toggle_actions = [
            (
                prefs.AUTO_STRIKE_SINGLE_TARGET,
                None,
                prefs.AUTO_STRIKE_SINGLE_TARGET,
                None,
                None,
                self.cb_auto_strike_single,
                False,
            ),
            (
                prefs.AUTO_RANGESTRIKE_SINGLE_TARGET,
                None,
                prefs.AUTO_RANGESTRIKE_SINGLE_TARGET,
                None,
                None,
                self.cb_auto_rangestrike_single,
                False,
            ),
            (
                prefs.AUTO_CARRY_TO_SINGLE_TARGET,
                None,
                prefs.AUTO_CARRY_TO_SINGLE_TARGET,
                None,
                None,
                self.cb_auto_carry_single,
                False,
            ),
        ]
        ag.add_toggle_actions(toggle_actions)
        self.ui = Gtk.UIManager()
        self.ui.insert_action_group(ag, 0)
        self.ui.add_ui_from_string(ui_string)

        for tup in toggle_actions:
            option = tup[0]
            if self.playername is not None:
                value = prefs.load_bool_option(self.playername, option)
                if value:
                    checkmenuitem = self.ui.get_widget(
                        f"/Menubar/OptionsMenu/{option}"
                    )
                    checkmenuitem.set_active(True)

    def enable_resume_ai(self) -> None:
        """Enable Resume AI and disable Pause AI."""
        pause_ai_button = self.ui.get_widget("/Toolbar/Pause AI")
        pause_ai_button.set_sensitive(False)
        pause_ai_menuitem = self.ui.get_widget("/Menubar/PhaseMenu/Pause AI")
        pause_ai_menuitem.set_sensitive(False)
        resume_ai_button = self.ui.get_widget("/Toolbar/Resume AI")
        resume_ai_button.set_sensitive(True)
        resume_ai_menuitem = self.ui.get_widget("/Menubar/PhaseMenu/Resume AI")
        resume_ai_menuitem.set_sensitive(True)

    def enable_pause_ai(self) -> None:
        """Enable Pause AI and disable Resume AI."""
        pause_ai_button = self.ui.get_widget("/Toolbar/Pause AI")
        pause_ai_button.set_sensitive(True)
        pause_ai_menuitem = self.ui.get_widget("/Menubar/PhaseMenu/Pause AI")
        pause_ai_menuitem.set_sensitive(True)
        resume_ai_button = self.ui.get_widget("/Toolbar/Resume AI")
        resume_ai_button.set_sensitive(False)
        resume_ai_menuitem = self.ui.get_widget("/Menubar/PhaseMenu/Resume AI")
        resume_ai_menuitem.set_sensitive(False)

    def disable_mulligan(self) -> None:
        """Disable taking mulligans."""
        mulligan_button = self.ui.get_widget("/Toolbar/Mulligan")
        mulligan_button.set_sensitive(False)
        mulligan_menuitem = self.ui.get_widget("/Menubar/PhaseMenu/Mulligan")
        mulligan_menuitem.set_sensitive(False)

    def _init_caretaker(self) -> None:
        if not self.guicaretaker:
            assert self.game is not None
            assert self.playername is not None
            self.guicaretaker = GUICaretaker.GUICaretaker(
                self.game, self.playername
            )
            self.vbox2.pack_start(self.guicaretaker, True, True, 0)
            self.game.add_observer(self.guicaretaker)

    def _init_status_screen(self) -> None:
        if not self.status_screen:
            assert self.game is not None
            assert self.playername is not None
            self.status_screen = StatusScreen.StatusScreen(
                self.game, self.playername
            )
            self.vbox2.pack_start(Gtk.HSeparator(), True, True, 0)
            self.vbox2.pack_start(self.status_screen, True, True, 0)
            self.game.add_observer(self.status_screen)

    def _init_inspector(self) -> None:
        if not self.inspector:
            assert self.playername is not None
            self.inspector = Inspector.Inspector(self.playername)
            self.vbox2.pack_start(Gtk.HSeparator(), True, True, 0)
            self.vbox2.pack_start(self.inspector, True, True, 0)

    def _init_event_log(self) -> None:
        if not self.event_log:
            assert self.game is not None
            self.event_log = EventLog.EventLog(self.game, self.playername)
            self.game.add_observer(self.event_log)
            self.vbox.pack_start(self.event_log, True, True, 0)

    def cb_delete_event(self, widget: Gtk.Widget, event: Any) -> bool:
        logging.debug(f"{event=}")
        if self.game is None or self.game.over:
            self.cb_destroy(True)
        else:
            confirm_dialog, def1 = ConfirmDialog.new(
                self, "Confirm", "Are you sure you want to quit?"
            )
            def1.addCallback(self.cb_destroy)
            def1.addErrback(self.failure)
        return True

    def cb_destroy(self, confirmed: bool) -> None:
        """Withdraw from the game, and destroy the GUIMasterBoard."""
        if confirmed:
            self.destroyed = True
            if self.game:
                def1 = self.user.callRemote("withdraw", self.game.name)  # type: ignore
                def1.addErrback(self.failure)
            if self.guimap is not None:
                self.guimap.destroy()
            self.destroy()

    def cb_withdraw2(self, confirmed: bool) -> None:
        """Withdraw from the game, but do not destroy the GUIMasterBoard."""
        if confirmed:
            if self.game:
                def1 = self.user.callRemote("withdraw", self.game.name)  # type: ignore
                def1.addErrback(self.failure)

    def cb_area_expose(
        self, area: Gtk.DrawingArea, event: cairo.Context
    ) -> bool:
        self.update_gui(event=event)
        return True

    def cb_click(self, area: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        for marker in self.markers:
            if marker.point_inside((event.x, event.y)):
                self.clicked_on_marker(area, event, marker)
                return True
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                self.clicked_on_hex(area, event, guihex)
                return True
        self.clicked_on_background(area, event)
        return True

    def cb_motion(self, area: Gtk.DrawingArea, event: Gdk.EventMotion) -> bool:
        """Callback for mouse motion."""
        for marker in self.markers:
            if marker.point_inside((event.x, event.y)):
                if self.inspector:
                    self.inspector.show_legion(marker.legion)
                return True
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                if self.game:
                    assert self.playername is not None
                    player = self.game.get_player_by_name(self.playername)
                    assert player is not None
                    player_color = player.color
                    assert player_color is not None
                else:
                    player_color = "Black"
                if self.inspector:
                    self.inspector.show_recruit_tree(
                        guihex.masterhex.terrain, player_color
                    )
                return True
        return True

    def _all_teleports(self, moves: List[Tuple[int, int]]) -> bool:
        """Return True iff all the move tuples in moves are teleports"""
        for move in moves:
            if move[1] != Game.TELEPORT:
                return False
        return True

    def _no_teleports(self, moves: List[Tuple[int, int]]) -> bool:
        """Return True iff none of the move tuples in moves are teleports"""
        for move in moves:
            if move[1] == Game.TELEPORT:
                return False
        return True

    def clicked_on_background(
        self, area: Gtk.DrawingArea, event: Gdk.EventButton
    ) -> None:
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

    def clicked_on_hex(
        self,
        area: Gtk.DrawingArea,
        event: Gdk.EventButton,
        guihex: GUIMasterHex.GUIMasterHex,
    ) -> None:
        if not self.game:
            return
        if event.button == 1:
            phase = self.game.phase
            if phase == Phase.SPLIT:
                self.highlight_tall_legions()
            elif phase == Phase.MOVE and self.selected_marker:
                if guihex.selected:
                    legion = self.selected_marker.legion
                    assert legion.player is not None
                    assert legion.player.movement_roll is not None
                    all_moves = self.game.find_all_moves(
                        legion,
                        self.board.hexes[legion.hexlabel],
                        legion.player.movement_roll,
                    )
                    moves = [
                        m for m in all_moves if m[0] == guihex.masterhex.label
                    ]
                    self._pick_move_type(legion, moves)
                self.selected_marker = None
                self.clear_all_recruitchits()
                self.unselect_all()
                self.highlight_unmoved_legions()
            elif phase == Phase.MOVE:
                self.highlight_unmoved_legions()
            elif phase == Phase.FIGHT:
                if guihex.selected:
                    def1 = self.user.callRemote(  # type: ignore
                        "resolve_engagement",
                        self.game.name,
                        guihex.masterhex.label,
                    )
                    def1.addErrback(self.failure)
            elif phase == Phase.MUSTER:
                self.highlight_recruits()

    def _pick_move_type(
        self, legion: Legion.Legion, moves: List[Tuple[int, int]]
    ) -> None:
        """Figure out whether to teleport, then call _pick_entry_side."""
        if self._all_teleports(moves):
            self._pick_entry_side(True, legion, moves)
        elif self._no_teleports(moves):
            self._pick_entry_side(False, legion, moves)
        else:
            hexlabel = moves[0][0]
            assert self.playername is not None
            _, def1 = PickMoveType.new(
                self.playername, legion, hexlabel, self.parent_window
            )
            def1.addCallback(self._pick_entry_side, legion, moves)

    def _pick_entry_side(
        self,
        teleport: Optional[bool],
        legion: Legion.Legion,
        moves: List[Tuple[int, int]],
    ) -> None:
        """Pick an entry side, then call _pick_teleporting_lord.

        teleport can be True, False, or None (cancel the move).
        """
        if teleport is None:
            self.highlight_unmoved_legions()
            return
        assert self.game is not None
        hexlabel = moves[0][0]
        masterhex = self.game.board.hexes[hexlabel]
        terrain = masterhex.terrain
        entry_sides = set()  # type: Set[Union[int, str]]
        if terrain == "Tower":
            entry_sides = {5}
        elif teleport:
            entry_sides = {1, 3, 5}
        else:
            entry_sides = {m[1] for m in moves}
            entry_sides.discard("TELEPORT")
        if len(entry_sides) == 1 or not legion.player.enemy_legions(hexlabel):
            self._pick_teleporting_lord(
                entry_sides.pop(), legion, moves, teleport  # type: ignore
            )
        else:
            if teleport:
                entry_sides = {1, 3, 5}
            else:
                entry_sides = {move[1] for move in moves}
            _, def1 = PickEntrySide.new(
                self.board,
                masterhex,
                entry_sides,  # type: ignore
                self.parent_window,
            )
            def1.addCallback(
                self._pick_teleporting_lord, legion, moves, teleport
            )

    def _pick_teleporting_lord(
        self,
        entry_side: int,
        legion: Legion.Legion,
        moves: List[Tuple[int, Union[int, str]]],
        teleport: bool,
    ) -> None:
        """Pick a teleporting lord, then call _do_move_legion."""
        if entry_side is None:
            self.highlight_unmoved_legions()
            return
        hexlabel = moves[0][0]
        lord_name = None  # type: Optional[str]
        if teleport:
            if legion.player.enemy_legions(hexlabel):
                assert legion.has_titan
                lord_name = "Titan"
            else:
                lord_types = legion.lord_types
                if len(lord_types) == 1:
                    lord_name = lord_types.pop()
                else:
                    assert self.playername is not None
                    _, def1 = PickTeleportingLord.new(
                        self.playername, legion, self.parent_window
                    )
                    def1.addCallback(
                        self._do_move_legion,
                        legion,
                        moves,
                        teleport,
                        entry_side,
                    )
                    return
        else:
            lord_name = None
        self._do_move_legion(lord_name, legion, moves, teleport, entry_side)

    def _do_move_legion(
        self,
        lord_name: Optional[str],
        legion: Legion.Legion,
        moves: List[Tuple[int, Union[str, int]]],
        teleport: bool,
        entry_side: int,
    ) -> None:
        """Call the server to request a legion move."""
        assert self.game is not None
        hexlabel = moves[0][0]
        def1 = self.user.callRemote(  # type: ignore
            "move_legion",
            self.game.name,
            legion.markerid,
            hexlabel,
            entry_side,
            teleport,
            lord_name,
        )
        def1.addErrback(self.failure)

    def clicked_on_marker(
        self,
        area: Gtk.DrawingArea,
        event: Gdk.EventButton,
        marker: Marker.Marker,
    ) -> None:
        assert self.game is not None
        phase = self.game.phase
        if phase == Phase.SPLIT:
            legion = marker.legion
            player = legion.player
            # Make sure it's this player's legion and turn.
            if player.name != self.playername:
                return
            elif player != self.game.active_player:
                return
            # Ensure that the legion can legally be split.
            elif not legion.can_be_split(self.game.turn):
                return
            elif player.selected_markerid:
                self.split_legion(legion)
            else:
                if not player.markerids_left:
                    InfoDialog.InfoDialog(
                        self.parent_window, "Info", "No markers available"
                    )
                    return
                _, def1 = PickMarker.new(
                    self.playername,
                    self.game.name,
                    sorted(player.markerids_left),
                    self.parent_window,
                )
                def1.addCallback(self.picked_marker_presplit, legion)

        elif phase == Phase.MOVE:
            legion = marker.legion
            player = legion.player
            if player.name != self.playername:
                # Not my marker; ignore it and click on the hex
                guihex = self.guihexes[legion.hexlabel]
                self.clicked_on_hex(area, event, guihex)
                return
            self.unselect_all()
            self.clear_all_recruitchits()
            if legion.moved:
                moves = set()  # type: Set[Tuple[int, int]]
            else:
                if player.movement_roll is None:
                    logging.warning("movement_roll is None; timing problem?")
                    moves = set()
                else:
                    moves = self.game.find_all_moves(
                        legion,
                        self.board.hexes[legion.hexlabel],
                        player.movement_roll,
                    )
            if moves:
                self.selected_marker = marker
                for move in moves:
                    hexlabel = move[0]
                    guihex = self.guihexes[hexlabel]
                    guihex.selected = True
                    self.repaint_hexlabels.add(hexlabel)
                    recruit_names = legion.available_recruits(
                        self.board.hexes[hexlabel].terrain, self.game.caretaker
                    )
                    if recruit_names:
                        self.create_recruitchits(
                            legion, hexlabel, recruit_names
                        )
            self.repaint()

        elif phase == Phase.FIGHT:
            legion = marker.legion
            guihex = self.guihexes[legion.hexlabel]
            if guihex.selected:
                def1 = self.user.callRemote(  # type: ignore
                    "resolve_engagement",
                    self.game.name,
                    guihex.masterhex.label,
                )
                def1.addErrback(self.failure)

        elif phase == Phase.MUSTER:
            self.unselect_all()
            legion = marker.legion
            if legion.moved:
                masterhex = self.board.hexes[legion.hexlabel]
                mterrain = masterhex.terrain
                caretaker = self.game.caretaker
                if legion.can_recruit:
                    assert self.playername is not None
                    logging.info("PickRecruit.new (muster)")
                    _, def1 = PickRecruit.new(
                        self.playername,
                        legion,
                        mterrain,
                        caretaker,
                        self.parent_window,
                    )
                    def1.addCallback(self.picked_recruit)
            self.highlight_recruits()

    def picked_marker_presplit(
        self, tup: Tuple[str, str, str], legion: Legion.Legion
    ) -> None:
        (game_name, playername, markerid) = tup
        assert self.game is not None
        player = self.game.get_player_by_name(playername)
        assert player is not None
        player.pick_marker(markerid)
        if markerid:
            self.split_legion(legion)

    def split_legion(self, legion: Legion.Legion) -> None:
        if legion is not None:
            assert self.playername is not None
            _, def1 = SplitLegion.new(
                self.playername, legion, self.parent_window
            )
            def1.addCallback(self.try_to_split_legion)

    def try_to_split_legion(
        self, tup1: Tuple[Legion.Legion, Legion.Legion, Legion.Legion]
    ) -> None:
        (old_legion, new_legion1, new_legion2) = tup1
        assert self.game is not None
        if old_legion is None:
            # canceled
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            player.selected_markerid = None
            return
        def1 = self.user.callRemote(  # type: ignore
            "split_legion",
            self.game.name,
            new_legion1.markerid,
            new_legion2.markerid,
            new_legion1.creature_names,
            new_legion2.creature_names,
        )
        def1.addErrback(self.failure)

    def picked_recruit(
        self, tup2: Tuple[Legion.Legion, Creature.Creature, List[str]]
    ) -> None:
        """Callback from PickRecruit"""
        (legion, creature, recruiter_names) = tup2
        assert self.game is not None
        if creature is not None:
            def1 = self.user.callRemote(  # type: ignore
                "recruit_creature",
                self.game.name,
                legion.markerid,
                creature.name,
                recruiter_names,
            )
            def1.addErrback(self.failure)
        elif self.game.phase == Phase.FIGHT:
            def1 = self.user.callRemote(  # type: ignore
                "do_not_reinforce", self.game.name, legion.markerid
            )
            def1.addErrback(self.failure)

    def picked_summon(
        self, tup3: Tuple[Legion.Legion, Legion.Legion, Creature.Creature]
    ) -> None:
        """Callback from SummonAngel"""
        (legion, donor, creature) = tup3
        assert self.game is not None
        if donor is None or creature is None:
            def1 = self.user.callRemote(  # type: ignore
                "do_not_summon_angel", self.game.name, legion.markerid
            )
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote(  # type: ignore
                "summon_angel",
                self.game.name,
                legion.markerid,
                donor.markerid,
                creature.name,
            )
            def1.addErrback(self.failure)

    def picked_angels(
        self, tup4: Tuple[Legion.Legion, List[Creature.Creature]]
    ) -> None:
        """Callback from AcquireAngels"""
        (legion, angels) = tup4
        logging.info(f"{legion=} {angels=}")
        assert self.game is not None
        self.acquire_angels = None
        if not angels:
            logging.info(f"calling do_not_acquire_angels {legion}")
            def1 = self.user.callRemote(  # type: ignore
                "do_not_acquire_angels", self.game.name, legion.markerid
            )
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote(  # type: ignore
                "acquire_angels",
                self.game.name,
                legion.markerid,
                [angel.name for angel in angels],
            )
            def1.addErrback(self.failure)

    def compute_scale(self) -> int:
        """Return the approximate maximum scale that let the board fit on
        the screen."""
        width = Gdk.Screen.width()
        height = Gdk.Screen.height()
        xscale = width / (self.board.hex_width * 4.0 + 2)
        # Fudge factor to leave room for menus and toolbars and EventLog.
        yscale = height / (self.board.hex_height * 4 * SQRT3) - 5
        return int(min(xscale, yscale))

    def compute_width(self) -> int:
        """Return the width of the board in pixels."""
        return int(math.ceil(self.scale * (self.board.hex_width * 4 + 2)))

    def compute_height(self) -> int:
        """Return the height of the board in pixels."""
        return int(math.ceil(self.scale * self.board.hex_height * 4 * SQRT3))

    def markers_in_hex(self, hexlabel: int) -> List[Marker.Marker]:
        return [
            marker
            for marker in self.markers
            if marker.legion.hexlabel == hexlabel
        ]

    def _add_missing_markers(self) -> None:
        """Add markers for any legions that lack them."""
        markerids = {marker.name for marker in self.markers}
        assert self.game is not None
        for legion in self.game.all_legions():
            if legion.markerid not in markerids:
                marker = Marker.Marker(legion, True, self.scale)
                self.markers.append(marker)

    def _remove_extra_markers(self) -> None:
        """Remove markers for any legions that are no longer there."""
        assert self.game is not None
        all_markerids = {legion.markerid for legion in self.game.all_legions()}
        hitlist = [
            marker
            for marker in self.markers
            if marker.name not in all_markerids
        ]
        for marker in hitlist:
            self.markers.remove(marker)

    def _place_chits(
        self,
        chits: Sequence[Union[Chit.Chit, Marker.Marker]],
        guihex: GUIMasterHex.GUIMasterHex,
    ) -> None:
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
        base_location = (
            guihex.center[0] - chit_scale / 2,
            guihex.center[1] - chit_scale / 2,
        )
        starting_offset = (num - 1) / 2.0
        first_location = (
            base_location[0] - starting_offset * increment,
            base_location[1] - starting_offset * increment,
        )
        for ii, chit in enumerate(chits):
            chit.location = (
                first_location[0] + ii * increment,
                first_location[1] + ii * increment,
            )

    def _render_marker(
        self, marker: Union[Marker.Marker, Chit.Chit], ctx: cairo.Context
    ) -> None:
        if marker.location is not None:
            ctx.set_source_surface(
                marker.surface,
                int(round(marker.location[0])),
                int(round(marker.location[1])),
            )
        ctx.paint()

    def draw_markers(self, ctx: cairo.Context) -> None:
        if not self.game:
            return
        self._add_missing_markers()
        self._remove_extra_markers()
        hexlabels = {marker.legion.hexlabel for marker in self.markers}
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            mih = self.markers_in_hex(hexlabel)
            self._place_chits(mih, guihex)
            # Draw in reverse order so that the markers that come earlier
            # in self.markers are on top.
            for marker in reversed(mih):
                marker.update_height()
                self._render_marker(marker, ctx)

    def create_recruitchits(
        self, legion: Legion.Legion, hexlabel: int, recruit_names: List[str]
    ) -> None:
        player = legion.player
        guihex = self.guihexes[hexlabel]
        recruitchit_scale = self.scale * Chit.CHIT_SCALE_FACTOR / 4
        # If there are already recruitchits here (because we reinforced
        # without clearing them), use a bag and take the maximum number
        # of each creature.
        chits = []
        old_names = bag()  # type: bag[str]
        for (chit, hexlabel2) in self.recruitchits:
            if hexlabel == hexlabel2:
                chits.append(chit)
                assert chit.creature is not None
                old_names.add(chit.creature.name)
        new_names = bag()  # type: bag[str]
        for name in recruit_names:
            new_names.add(name)
        diff = new_names.difference(old_names)
        for name, number in diff.items():
            for unused in range(number):
                recruit = Creature.Creature(name)
                chit = Chit.Chit(recruit, player.color, int(recruitchit_scale))
                chits.append(chit)
                self.recruitchits.append((chit, hexlabel))
        self._place_chits(chits, guihex)

    def draw_recruitchits(self, ctx: cairo.Context) -> None:
        # Draw in forward order so the last recruitchit in the list is on top.
        for (chit, unused) in self.recruitchits:
            self._render_marker(chit, ctx)

    def draw_movement_die(self, ctx: cairo.Context) -> None:
        if self.game is None or self.game.active_player is None:
            return
        phase = self.game.phase
        if phase == Phase.MOVE:
            roll = self.game.active_player.movement_roll
        else:
            roll = None
        if roll:
            die = Die.Die(roll, scale=self.scale)
            ctx.set_source_surface(die.surface, 0, 0)
            ctx.paint()
        else:
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(
                0,
                0,
                Chit.CHIT_SCALE_FACTOR * self.scale,
                Chit.CHIT_SCALE_FACTOR * self.scale,
            )
            ctx.fill()

    def bounding_rect_for_hexlabels(
        self, hexlabels: Set[int]
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
        return int(min_x), int(min_y), int(width), int(height)

    def update_gui(self, event: Optional[cairo.Context] = None) -> None:
        """Repaint the amount of the GUI that needs repainting.

        Compute the dirty rectangle from the union of
        self.repaint_hexlabels and the event's area.
        """
        if self.destroyed or not self.area or not self.area.get_window():
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
        ctx.rectangle(*clip_rect)
        ctx.clip()

        # black background
        if event is not None:
            ctx.set_source_rgb(0, 0, 0)
            requisition = self.area.get_size_request()
            width = requisition.width
            height = requisition.height
            # Overdraw in case window is enlarged.
            ctx.rectangle(0, 0, 2 * width, 2 * height)
            ctx.fill()
        for hexlabel in self.repaint_hexlabels:
            if hexlabel:
                ctx.set_source_rgb(0, 0, 0)
                guihex = self.guihexes[hexlabel]
                x, y, width, height = guihex.bounding_rect
                ctx.rectangle(x, y, width, height)
                ctx.fill()
        for guihex in self.guihexes.values():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)

        self.draw_markers(ctx)
        self.draw_recruitchits(ctx)
        self.draw_movement_die(ctx)

        ctx2 = self.area.get_window().cairo_create()
        ctx2.set_source_surface(surface)
        ctx2.paint()

        self.repaint_hexlabels.clear()

    def repaint(self, hexlabels: Set[int] = None) -> None:
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)  # type: ignore

    def unselect_all(self) -> None:
        for guihex in self.guihexes.values():
            if guihex.selected:
                guihex.selected = False
                self.repaint_hexlabels.add(guihex.masterhex.label)
        self.repaint()

    def clear_all_recruitchits(self, *unused: Any) -> None:
        if self.recruitchits:
            hexlabels = {tup[1] for tup in self.recruitchits}
            self.recruitchits = []
            self.repaint(hexlabels)

    def clear_recruitchits(self, hexlabel: int) -> None:
        """Clear recruitchits in one hex."""
        self.recruitchits = [
            (chit, hexlabel2)
            for (chit, hexlabel2) in self.recruitchits
            if hexlabel2 != hexlabel
        ]
        self.repaint({hexlabel})

    def clear_stray_recruitchits(self) -> None:
        """Clear recruitchits in all empty hexes."""
        occupied_hexlabels = set()
        stray_hexlabels = set()
        new_recruitchits = []
        assert self.game is not None
        for legion in self.game.all_legions():
            occupied_hexlabels.add(legion.hexlabel)
        for chit, hexlabel in self.recruitchits:
            if hexlabel in occupied_hexlabels:
                new_recruitchits.append((chit, hexlabel))
            else:
                stray_hexlabels.add(hexlabel)
        if stray_hexlabels:
            self.recruitchits = new_recruitchits
            self.repaint(stray_hexlabels)

    def highlight_tall_legions(self) -> None:
        """Highlight all hexes containing a legion of height 7 or more
        belonging to the active, current player."""
        assert self.game is not None
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        if player == self.game.active_player:
            self.unselect_all()
            if player.markerids_left:
                for legion in player.legions:
                    if len(legion) >= 7:
                        self.repaint_hexlabels.add(legion.hexlabel)
                        guihex = self.guihexes[legion.hexlabel]
                        guihex.selected = True
            self.repaint()

    def highlight_unmoved_legions(self) -> None:
        """Highlight all hexes containing an unmoved legion belonging to the
        active, current player."""
        assert self.game is not None
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        if player == self.game.active_player:
            self.clear_all_recruitchits()
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions:
                if not legion.moved:
                    hexlabels.add(legion.hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.repaint(hexlabels)

    def highlight_engagements(self) -> None:
        """Highlight all hexes with engagements."""
        self.unselect_all()
        assert self.game is not None
        hexlabels = self.game.engagement_hexlabels
        for hexlabel in hexlabels:
            guihex = self.guihexes[hexlabel]
            guihex.selected = True
        self.repaint(hexlabels)

    def highlight_hex(self, hexlabel: int) -> None:
        """Highlight one hex."""
        self.unselect_all()
        guihex = self.guihexes[hexlabel]
        guihex.selected = True
        self.repaint({hexlabel})

    def highlight_recruits(self) -> None:
        """Highlight all hexes in which the active player can recruit."""
        assert self.game is not None
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        if player == self.game.active_player:
            self.unselect_all()
            hexlabels = set()
            for legion in player.legions:
                hexlabel = legion.hexlabel
                if legion.moved and legion.can_recruit:
                    hexlabels.add(hexlabel)
            for hexlabel in hexlabels:
                guihex = self.guihexes[hexlabel]
                guihex.selected = True
            self.repaint(hexlabels)

    def cb_save(self, action: Action.Action) -> None:
        def1 = self.user.callRemote("save", self.game.name)  # type: ignore
        def1.addErrback(self.failure)

    def cb_done(self, action: Action.Action) -> None:
        if not self.game:
            return
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        if player == self.game.active_player:
            if self.game.phase == Phase.SPLIT:
                if player.can_exit_split_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_splits", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(
                        self.parent_window,
                        "Info",
                        "Must split initial legion 4-4",
                    )
            elif self.game.phase == Phase.MOVE:
                if player.can_exit_move_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_moves", self.game.name
                    )
                    def1.addErrback(self.failure)
                elif not player.moved_legions:
                    InfoDialog.InfoDialog(
                        self.parent_window,
                        "Info",
                        "Must move at least one legion",
                    )
                else:
                    InfoDialog.InfoDialog(
                        self.parent_window,
                        "Info",
                        "Must separate split legions",
                    )
            elif self.game.phase == Phase.FIGHT:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    InfoDialog.InfoDialog(
                        self.parent_window, "Info", "Must resolve engagements"
                    )
            elif self.game.phase == Phase.MUSTER:
                player.forget_enemy_legions()
                def1 = self.user.callRemote(  # type: ignore
                    "done_with_recruits", self.game.name
                )
                def1.addErrback(self.failure)

    def cb_mulligan(self, action: Action.Action) -> None:
        if not self.game:
            return
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        if player.can_take_mulligan:
            history = self.game.history
            assert history is not None
            assert self.playername is not None
            if history.can_undo(self.playername):
                last_action = history.actions[-1]
                def1 = self.user.callRemote(  # type: ignore
                    "apply_action", last_action.undo_action()
                )
                def1.addCallback(self.cb_mulligan)
                def1.addErrback(self.failure)
            else:
                def1 = self.user.callRemote("take_mulligan", self.game.name)  # type: ignore
                def1.addErrback(self.failure)

    def _cb_checkbox_helper(self, option: str) -> None:
        checkmenuitem = self.ui.get_widget(f"/Menubar/OptionsMenu/{option}")
        active = checkmenuitem.get_active()
        assert self.playername is not None
        prev = prefs.load_bool_option(self.playername, option)
        if active != prev:
            prefs.save_bool_option(self.playername, option, active)

    def cb_auto_strike_single(self, action: Action.Action) -> None:
        logging.info("cb_auto_strike_single")
        option = prefs.AUTO_STRIKE_SINGLE_TARGET
        self._cb_checkbox_helper(option)

    def cb_auto_rangestrike_single(self, action: Action.Action) -> None:
        logging.info("cb_auto_rangestrike_single")
        option = prefs.AUTO_RANGESTRIKE_SINGLE_TARGET
        self._cb_checkbox_helper(option)

    def cb_auto_carry_single(self, action: Action.Action) -> None:
        logging.info("cb_auto_carry_single")
        option = prefs.AUTO_CARRY_TO_SINGLE_TARGET
        self._cb_checkbox_helper(option)

    def cb_about(self, action: Action.Action) -> None:
        About.About(self.parent_window)

    def cb_undo(self, action: Action.Action) -> None:
        if self.game:
            history = self.game.history
            assert history is not None
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
            assert history is not None
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
            assert history is not None
            assert self.playername is not None
            if history.can_redo(self.playername):
                action = history.undone[-1]
                def1 = self.user.callRemote("apply_action", action)  # type: ignore
                def1.addErrback(self.failure)

    def cb_quit(self, action: Action.Action) -> None:
        """Quit the game, destroy the board and map, and unsubscribe from this
        game's events."""
        if self.game and (
            self.game.over
            or self.playername not in self.game.living_playernames
        ):
            self.cb_destroy(True)
        else:
            confirm_dialog, def1 = ConfirmDialog.new(
                self, "Confirm", "Are you sure you want to quit?"
            )
            def1.addCallback(self.cb_destroy)
            def1.addErrback(self.failure)

    def cb_withdraw(self, action: Action.Action) -> None:
        """Withdraw from the game but keep watching it."""
        if self.game and self.game.over:
            self.cb_destroy(True)
        else:
            confirm_dialog, def1 = ConfirmDialog.new(
                self, "Confirm", "Are you sure you want to withdraw?"
            )
            def1.addCallback(self.cb_withdraw2)
            def1.addErrback(self.failure)

    def cb_maybe_flee(
        self, tup5: Tuple[Legion.Legion, Legion.Legion, bool]
    ) -> None:
        assert self.game is not None
        (attacker, defender, fled) = tup5
        if fled:
            def1 = self.user.callRemote(  # type: ignore
                "flee", self.game.name, defender.markerid
            )
        else:
            def1 = self.user.callRemote(  # type: ignore
                "do_not_flee", self.game.name, defender.markerid
            )
        def1.addErrback(self.failure)

    def cb_negotiate(
        self,
        tup6: Tuple[Legion.Legion, List[str], Legion.Legion, List[str], int],
    ) -> None:
        """Callback from Negotiate dialog."""
        (
            attacker_legion,
            attacker_creature_names,
            defender_legion,
            defender_creature_names,
            response_id,
        ) = tup6
        assert self.game is not None
        assert self.playername is not None
        player = self.game.get_player_by_name(self.playername)
        assert player is not None
        hexlabel = attacker_legion.hexlabel
        for legion in player.friendly_legions(hexlabel):
            friendly_legion = legion
        if attacker_legion == friendly_legion:
            enemy_legion = defender_legion
        else:
            enemy_legion = attacker_legion
        if response_id == Negotiate.CONCEDE:
            def1 = self.user.callRemote(  # type: ignore
                "concede",
                self.game.name,
                friendly_legion.markerid,
                enemy_legion.markerid,
                hexlabel,
            )
            def1.addErrback(self.failure)
        elif response_id == Negotiate.MAKE_PROPOSAL:
            assert self.game is not None
            def1 = self.user.callRemote(  # type: ignore
                "make_proposal",
                self.game.name,
                attacker_legion.markerid,
                attacker_creature_names,
                defender_legion.markerid,
                defender_creature_names,
            )
            def1.addErrback(self.failure)
        elif response_id == Negotiate.DONE_PROPOSING:
            assert self.game is not None
            def1 = self.user.callRemote(  # type: ignore
                "no_more_proposals",
                self.game.name,
                attacker_legion.markerid,
                defender_legion.markerid,
            )
            def1.addErrback(self.failure)
        elif response_id == Negotiate.FIGHT:
            assert self.game is not None
            def1 = self.user.callRemote(  # type: ignore
                "fight",
                self.game.name,
                attacker_legion.markerid,
                defender_legion.markerid,
            )
            def1.addErrback(self.failure)

    def cb_proposal(
        self,
        tup7: Tuple[Legion.Legion, List[str], Legion.Legion, List[str], int],
    ) -> None:
        """Callback from Proposal dialog."""
        (
            attacker_legion,
            attacker_creature_names,
            defender_legion,
            defender_creature_names,
            response_id,
        ) = tup7
        assert self.game is not None
        if response_id == Proposal.ACCEPT:
            def1 = self.user.callRemote(  # type: ignore
                "accept_proposal",
                self.game.name,
                attacker_legion.markerid,
                attacker_creature_names,
                defender_legion.markerid,
                defender_creature_names,
            )
            def1.addErrback(self.failure)
        elif response_id == Proposal.REJECT:
            def1 = self.user.callRemote(  # type: ignore
                "reject_proposal",
                self.game.name,
                attacker_legion.markerid,
                attacker_creature_names,
                defender_legion.markerid,
                defender_creature_names,
            )
            def1.addErrback(self.failure)
        elif response_id == Proposal.FIGHT:
            def1 = self.user.callRemote(  # type: ignore
                "fight",
                self.game.name,
                attacker_legion.markerid,
                defender_legion.markerid,
            )
            def1.addErrback(self.failure)

    def pause_ai(self, arg: Any) -> None:
        logging.debug(f"{arg=}")
        def1 = self.user.callRemote("pause_ai", self.game.name)  # type: ignore
        def1.addErrback(self.failure)

    def resume_ai(self, arg: Any) -> None:
        logging.debug(f"{arg=}")
        def1 = self.user.callRemote("resume_ai", self.game.name)  # type: ignore
        def1.addErrback(self.failure)

    def destroy_negotiate(self) -> None:
        if self.negotiate is not None:
            self.negotiate.destroy()
            self.negotiate = None
        for proposal in self.proposals:
            proposal.destroy()
        self.proposals.clear()

    def failure(self, arg: Any) -> None:
        log.err(arg)  # type: ignore

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: List[str] = None,
    ) -> None:
        attacker = None  # type: Optional[Legion.Legion]
        defender = None  # type: Optional[Legion.Legion]

        if isinstance(action, Action.PickedColor):
            self._init_caretaker()
            self._init_status_screen()
            self._init_inspector()
            self._init_event_log()
            # Needed to show the HSeparators
            self.show_all()

        elif isinstance(action, Action.CreateStartingLegion):
            assert self.game is not None
            legion = self.game.find_legion(action.markerid)
            if legion:
                self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.SplitLegion):
            assert self.game is not None
            legion = self.game.find_legion(action.parent_markerid)
            assert legion is not None
            self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.UndoSplit):
            assert self.game is not None
            legion = self.game.find_legion(action.parent_markerid)
            assert legion is not None
            for hexlabel in [legion.hexlabel, legion.previous_hexlabel]:
                if hexlabel is not None:
                    self.repaint_hexlabels.add(hexlabel)
            self.highlight_tall_legions()

        elif isinstance(action, Action.RollMovement):
            # show movement die
            self.repaint_hexlabels.update(list(self.board.hexes.keys()))
            assert self.playername is not None
            if action.playername == self.playername:
                if action.mulligans_left == 0:
                    self.disable_mulligan()
                self.highlight_unmoved_legions()
            else:
                self.repaint()

        elif isinstance(action, Action.MoveLegion) or isinstance(
            action, Action.UndoMoveLegion
        ):
            assert self.game is not None
            self.selected_marker = None
            self.unselect_all()
            legion = self.game.find_legion(action.markerid)
            assert legion is not None
            for hexlabel in [legion.hexlabel, legion.previous_hexlabel]:
                if hexlabel is not None:
                    self.repaint_hexlabels.add(hexlabel)
            if legion.previous_hexlabel:
                self.clear_recruitchits(legion.previous_hexlabel)
            if action.playername == self.playername:
                self.highlight_unmoved_legions()
            else:
                self.repaint()

        elif isinstance(action, Action.StartFightPhase):
            assert self.game is not None
            # clear movement die
            self.repaint_hexlabels.update(list(self.board.hexes.keys()))
            assert self.playername is not None
            if action.playername == self.playername:
                self.clear_all_recruitchits()
            self.highlight_engagements()
            player = self.game.active_player
            assert player is not None
            if self.playername == player.name:
                if not self.game.engagement_hexlabels:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.StartMusterPhase):
            assert self.game is not None
            # clear movement die
            self.repaint_hexlabels.update(self.board.hexes.keys())
            self.highlight_recruits()
            player = self.game.active_player
            assert player is not None
            if self.playername == player.name:
                if not player.can_recruit:
                    player.forget_enemy_legions()
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_recruits", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.ResolvingEngagement):
            assert self.game is not None
            hexlabel = action.hexlabel
            self.highlight_hex(hexlabel)
            for legion in self.game.all_legions(hexlabel):
                if legion.player == self.game.active_player:
                    attacker = legion
                else:
                    defender = legion
            assert attacker is not None
            assert defender is not None
            if defender.player.name == self.playername:
                if defender.can_flee:
                    _, def1 = Flee.new(
                        self.playername, attacker, defender, self.parent_window
                    )
                    def1.addCallback(self.cb_maybe_flee)
                else:
                    # Can't flee, so we always send the do_not_flee.
                    # (Others may not know that we have a lord here.)
                    self.cb_maybe_flee((attacker, defender, False))

        elif isinstance(action, Action.Flee):
            assert self.game is not None
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotFlee):
            assert self.game is not None
            markerid = action.markerid
            defender = self.game.find_legion(markerid)
            assert defender is not None
            hexlabel = defender.hexlabel
            attacker = None
            for legion in self.game.all_legions(hexlabel=hexlabel):
                if legion != defender:
                    attacker = legion
            if attacker is not None and (
                defender.player.name == self.playername
                or attacker.player.name == self.playername
            ):
                self.negotiate, def1 = Negotiate.new(
                    self.playername, attacker, defender, self.parent_window
                )
                def1.addCallback(self.cb_negotiate)

        elif isinstance(action, Action.Concede):
            assert self.game is not None
            self.destroy_negotiate()
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.MakeProposal):
            assert self.game is not None
            attacker_markerid = action.attacker_markerid
            attacker = self.game.find_legion(attacker_markerid)
            defender_markerid = action.defender_markerid
            defender = self.game.find_legion(defender_markerid)
            assert self.playername is not None
            if attacker is not None and defender is not None:
                proposal, def1 = Proposal.new(
                    self.playername,
                    attacker,
                    list(action.attacker_creature_names),
                    defender,
                    list(action.defender_creature_names),
                    self.parent_window,
                )
                def1.addCallback(self.cb_proposal)
                self.proposals.add(proposal)

        elif isinstance(action, Action.AcceptProposal):
            assert self.game is not None
            self.destroy_negotiate()
            self.repaint_hexlabels.add(action.hexlabel)
            self.highlight_engagements()
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.RejectProposal):
            assert self.game is not None
            attacker_markerid = action.attacker_markerid
            attacker = self.game.find_legion(attacker_markerid)
            assert attacker is not None
            defender_markerid = action.defender_markerid
            defender = self.game.find_legion(defender_markerid)
            assert defender is not None
            assert self.playername is not None
            if action.other_playername == self.playername:
                self.negotiate, def1 = Negotiate.new(
                    self.playername, attacker, defender, self.parent_window
                )
                def1.addCallback(self.cb_negotiate)

        elif isinstance(action, Action.RecruitCreature):
            assert self.game is not None
            legion = self.game.find_legion(action.markerid)
            if legion:
                self.repaint_hexlabels.add(legion.hexlabel)
                creature_names = list(action.recruiter_names)
                creature_names.append(action.creature_name)
                self.create_recruitchits(
                    legion, legion.hexlabel, creature_names
                )
            self.highlight_recruits()

        elif isinstance(action, Action.UndoRecruit) or isinstance(
            action, Action.UnReinforce
        ):
            assert self.game is not None
            legion = self.game.find_legion(action.markerid)
            if legion:
                self.repaint_hexlabels.add(legion.hexlabel)
                self.clear_recruitchits(legion.hexlabel)
            self.highlight_recruits()

        elif isinstance(action, Action.StartSplitPhase):
            assert self.game is not None
            player = self.game.active_player
            assert player is not None
            if self.playername == player.name:
                self.unselect_all()
                self.highlight_tall_legions()
                if not player.can_split:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_splits", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.SummonAngel):
            assert self.game is not None
            legion = self.game.find_legion(action.markerid)
            donor = self.game.find_legion(action.donor_markerid)
            hexlabels = set()
            if legion and legion.hexlabel:
                hexlabels.add(legion.hexlabel)
                self.create_recruitchits(
                    legion, legion.hexlabel, [action.creature_name]
                )
            if donor and donor.hexlabel:
                hexlabels.add(donor.hexlabel)
            self.repaint(hexlabels)
            self.highlight_engagements()
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotSummonAngel):
            assert self.game is not None
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    self.highlight_engagements()

        elif isinstance(action, Action.UnsummonAngel):
            assert self.game is not None
            legion = self.game.find_legion(action.markerid)
            donor = self.game.find_legion(action.donor_markerid)
            hexlabels = set()
            if legion and legion.hexlabel:
                hexlabels.add(legion.hexlabel)
                self.clear_recruitchits(legion.hexlabel)
            if donor and donor.hexlabel:
                hexlabels.add(donor.hexlabel)
            self.repaint(hexlabels)
            self.highlight_engagements()

        elif isinstance(action, Action.CanAcquireAngels):
            assert self.game is not None
            if (
                self.acquire_angels is None
                and action.playername == self.playername
            ):
                markerid = action.markerid
                legion = self.game.find_legion(markerid)
                assert legion is not None
                angels = action.angels
                archangels = action.archangels
                caretaker = self.game.caretaker
                assert caretaker is not None
                if angels or archangels:
                    self.acquire_angels, def1 = AcquireAngels.new(
                        self.playername,
                        legion,
                        archangels,
                        angels,
                        caretaker,
                        self.parent_window,
                    )
                    def1.addCallback(self.picked_angels)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.AcquireAngels):
            assert self.game is not None
            markerid = action.markerid
            legion = self.game.find_legion(markerid)
            if legion and legion.hexlabel and action.angel_names:
                self.create_recruitchits(
                    legion, legion.hexlabel, list(action.angel_names)
                )
                self.repaint_hexlabels.add(legion.hexlabel)
            self.highlight_engagements()
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotAcquireAngels):
            assert self.game is not None
            assert self.playername is not None
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)
                else:
                    self.highlight_engagements()

        elif isinstance(action, Action.Fight):
            assert self.game is not None
            self.destroy_negotiate()
            self.unselect_all()
            if self.guimap is None and not self.destroyed:
                assert self.game.battlemap is not None
                self.guimap = GUIBattleMap.GUIBattleMap(
                    self.game.battlemap,
                    self.game,
                    self.user,
                    self.playername,
                    parent_window=self.parent_window,
                )
                assert self.parent_window is not None
                self.parent_window.add_guimap(self.guimap)
                self.game.add_observer(self.guimap)

        elif isinstance(action, Action.BattleOver):
            assert self.game is not None
            assert self.playername is not None
            legion = self.game.find_legion(action.winner_markerid)
            if legion:
                player = legion.player
                if (
                    player.name == self.playername
                    and self.game.phase == Phase.FIGHT
                ):
                    if player == self.game.active_player:
                        # attacker can possibly summon
                        if legion.can_summon:
                            _, def1 = SummonAngel.new(
                                self.playername, legion, self.parent_window
                            )
                            def1.addCallback(self.picked_summon)
                        else:
                            logging.info("calling do_not_summon_angel")
                            def1 = self.user.callRemote(  # type: ignore
                                "do_not_summon_angel",
                                self.game.name,
                                legion.markerid,
                            )
                            def1.addErrback(self.failure)
                    else:
                        # defender can possibly reinforce
                        masterhex = self.game.board.hexes[legion.hexlabel]
                        caretaker = self.game.caretaker
                        mterrain = masterhex.terrain
                        if legion.can_recruit:
                            logging.info("PickRecruit.new (after)")
                            _, def1 = PickRecruit.new(
                                self.playername,
                                legion,
                                mterrain,
                                caretaker,
                                self.parent_window,
                            )
                            def1.addCallback(self.picked_recruit)
                        else:
                            logging.info("calling do_not_reinforce")
                            def1 = self.user.callRemote(  # type: ignore
                                "do_not_reinforce",
                                self.game.name,
                                legion.markerid,
                            )
                            def1.addErrback(self.failure)
            if self.guimap is not None:
                self.game.remove_observer(self.guimap)
                del self.guimap
                self.guimap = None
            hexlabel = action.hexlabel
            self.clear_recruitchits(hexlabel)
            if legion:
                self.create_recruitchits(
                    legion, hexlabel, legion.living_creature_names
                )
            self.repaint_hexlabels.add(hexlabel)
            self.highlight_engagements()
            player = self.game.get_player_by_name(self.playername)
            assert player is not None
            if player == self.game.active_player:
                if player.can_exit_fight_phase:
                    def1 = self.user.callRemote(  # type: ignore
                        "done_with_engagements", self.game.name
                    )
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.EliminatePlayer):
            assert self.game is not None
            player = self.game.get_player_by_name(action.loser_playername)
            assert player is not None
            for legion in player.legions:
                self.repaint_hexlabels.add(legion.hexlabel)
            self.clear_stray_recruitchits()
            self.repaint()

        elif isinstance(action, Action.GameOver):
            if self.game_over is None:
                if action.winner_names:
                    message = f"Game over.  {action.winner_names[0]} wins."
                else:
                    message = "Game over.  Draw."
                self.game_over = InfoDialog.InfoDialog(
                    self.parent_window, "Info", message
                )
            self.destroy()

        elif isinstance(action, Action.PauseAI):
            self.enable_resume_ai()

        elif isinstance(action, Action.ResumeAI):
            self.enable_pause_ai()


if __name__ == "__main__":
    from slugathon.game import MasterBoard

    window = Gtk.Window()
    window.set_default_size(1024, 768)
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(board, parent_window=window)
    window.add(guiboard)
    window.show_all()
    window.connect("destroy", lambda x: reactor.stop())  # type: ignore[attr-defined]
    reactor.run()  # type: ignore[attr-defined]
