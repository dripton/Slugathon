#!/usr/bin/env python3


from __future__ import annotations

import logging
import math
from sys import maxsize
from typing import Any, Optional, Set, Tuple

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
from twisted.internet import defer, reactor

from slugathon.game import BattleMap, MasterBoard, MasterHex
from slugathon.gui import GUIBattleHex, icon
from slugathon.util import guiutils, prefs


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


SQRT3 = math.sqrt(3.0)

hexlabel_to_entry_side = {
    "F1": 1,
    "F2": 1,
    "F3": 1,
    "F4": 1,
    "A3": 3,
    "B4": 3,
    "C5": 3,
    "D6": 3,
    "A1": 5,
    "B1": 5,
    "C1": 5,
    "D1": 5,
}


def new(
    board: MasterBoard.MasterBoard,
    masterhex: MasterHex.MasterHex,
    entry_sides: Set[int],
    parent: Gtk.Window,
    playername: Optional[str] = None,
    scale: Optional[int] = None,
) -> Tuple[PickEntrySide, defer.Deferred]:
    """Create a PickEntrySide dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pick_entry_side = PickEntrySide(
        board, masterhex, entry_sides, def1, parent, playername, scale
    )
    return pick_entry_side, def1


class PickEntrySide(Gtk.Dialog):

    """Dialog to pick a masterhex entry side."""

    def __init__(
        self,
        board: MasterBoard.MasterBoard,
        masterhex: MasterHex.MasterHex,
        entry_sides: Set[int],
        def1: defer.Deferred,
        parent: Gtk.Window,
        playername: Optional[str] = None,
        scale: Optional[int] = None,
    ):
        GObject.GObject.__init__(
            self, title=f"Pick Entry Side - {playername}", parent=parent
        )

        terrain = masterhex.terrain
        # We always orient the map as if for entry side 5.
        self.battlemap = BattleMap.BattleMap(terrain, 5)
        self.entry_sides = entry_sides
        self.deferred = def1
        self.playername = playername
        self.board = board

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title(f"PickEntrySide - Slugathon - {self.playername}")

        self.hbox1 = Gtk.HBox(homogeneous=True)
        self.hbox2 = Gtk.HBox()
        self.hbox3 = Gtk.HBox()
        self.vbox.pack_start(self.hbox1, False, True, 0)
        self.vbox.pack_start(self.hbox2, True, True, 0)
        self.vbox.pack_start(self.hbox3, False, True, 0)

        if scale is None:
            self.scale = self.compute_scale()
        else:
            self.scale = scale
        self.area = Gtk.DrawingArea()
        self.area.set_size_request(self.compute_width(), self.compute_height())

        if self.playername:
            tup = prefs.load_window_position(
                self.playername, self.__class__.__name__
            )
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(
                self.playername, self.__class__.__name__
            )
            if tup:
                width, height = tup
                self.resize(width, height)

        own_hex_label = self.masterhex_label(masterhex)
        left_hex = masterhex.neighbors[4] or masterhex.neighbors[5]
        left_hex_label = self.masterhex_label(left_hex)
        top_hex = masterhex.neighbors[0] or masterhex.neighbors[1]
        top_hex_label = self.masterhex_label(top_hex)
        bottom_hex = masterhex.neighbors[2] or masterhex.neighbors[3]
        bottom_hex_label = self.masterhex_label(bottom_hex)
        spacer_label = self.masterhex_label(None)
        self.hbox1.pack_start(own_hex_label, True, True, 0)
        self.hbox1.pack_start(top_hex_label, True, True, 0)
        self.hbox2.pack_start(left_hex_label, True, True, 0)
        self.hbox2.pack_start(self.area, True, True, 0)
        self.hbox3.pack_start(spacer_label, True, True, 0)
        self.hbox3.pack_start(bottom_hex_label, True, True, 0)

        self.guihexes = {}
        for hex1 in self.battlemap.hexes.values():
            # Don't show entrances.
            if hex1.label not in ["ATTACKER", "DEFENDER"]:
                self.guihexes[hex1.label] = GUIBattleHex.GUIBattleHex(
                    hex1, self
                )
        self.repaint_hexlabels = set()  # type: Set[str]
        # Hexes that need their bounding rectangles cleared, too.
        # This fixes chits.
        self.clear_hexlabels = set()  # type: Set[str]

        self.area.connect("draw", self.cb_area_expose)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.area.connect("button-press-event", self.cb_click)

        self.connect("destroy", self.callback_with_none)

        for hexlabel, entry_side in hexlabel_to_entry_side.items():
            if entry_side in self.entry_sides:
                self.guihexes[hexlabel].selected = True
        self.show_all()

    def compute_scale(self) -> int:
        """Return the approximate maximum scale that lets the map fit on the
        screen."""
        width = Gdk.Screen.width()
        height = Gdk.Screen.height()
        # Fudge factor to leave room on the sides.
        xscale = math.floor(width / (2 * self.battlemap.hex_width)) - 5
        # Fudge factor for menus and toolbars.
        yscale = (
            math.floor(height / (2 * SQRT3 * self.battlemap.hex_height)) - 11
        )
        return int(min(xscale, yscale))

    def compute_width(self) -> int:
        """Return the width of the map in pixels."""
        return int(math.ceil(self.scale * self.battlemap.hex_width * 3.2))

    def compute_height(self) -> int:
        """Return the height of the map in pixels."""
        return int(
            math.ceil(self.scale * self.battlemap.hex_height * 2 * SQRT3)
        )

    def masterhex_label(
        self, masterhex: Optional[MasterHex.MasterHex]
    ) -> Gtk.EventBox:
        """Return a Gtk.Label describing masterhex, inside a white
        Gtk.EventBox."""
        eventbox = Gtk.EventBox()
        if masterhex:
            text = (
                f"<span size='large' weight='bold'>{masterhex.terrain} "
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

    def cb_area_expose(
        self, area: Gtk.DrawingArea, event: cairo.Context
    ) -> bool:
        self.update_gui(event=event)
        return True

    def cb_click(self, area: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        for guihex in self.guihexes.values():
            if guiutils.point_in_polygon((event.x, event.y), guihex.points):
                self.clicked_on_hex(area, event, guihex)
                return True
        return True

    def clicked_on_hex(
        self,
        area: Gtk.DrawingArea,
        event: Gdk.EventButton,
        guihex: GUIBattleHex.GUIBattleHex,
    ) -> None:
        if guihex.selected:
            entry_side = hexlabel_to_entry_side[guihex.battlehex.label]
            self.deferred.callback(entry_side)
            self.destroy()

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

        ctx = self.area.get_window().cairo_create()
        ctx.set_line_width(round(0.2 * self.scale))
        ctx.rectangle(*clip_rect)
        ctx.clip()
        # white background, only when we get an event
        if event is not None:
            ctx.set_source_rgb(1, 1, 1)
            requisition = self.area.get_size_request()
            width = requisition.width
            height = requisition.height
            ctx.rectangle(0, 0, width, height)
            ctx.fill()
        for hexlabel in self.clear_hexlabels:
            ctx.set_source_rgb(1, 1, 1)
            guihex = self.guihexes[hexlabel]
            x, y, width, height = guihex.bounding_rect
            ctx.rectangle(x, y, width, height)
            ctx.fill()
        for guihex in self.guihexes.values():
            if guiutils.rectangles_intersect(clip_rect, guihex.bounding_rect):
                guihex.update_gui(ctx)
        self.repaint_hexlabels.clear()
        self.clear_hexlabels.clear()

    def repaint(self, hexlabels: Set[str] = None) -> None:
        if hexlabels:
            self.repaint_hexlabels.update(hexlabels)
        reactor.callLater(0, self.update_gui)  # type: ignore

    def callback_with_none(self, *args: Any) -> None:
        """Called if the window is destroyed."""
        logging.debug(f"{args=}")
        if not self.deferred.called:
            self.deferred.callback(None)


if __name__ == "__main__":
    import random

    def my_callback(choice: int) -> None:
        logging.info(f"chose entry side {choice}")
        reactor.stop()  # type: ignore

    board = MasterBoard.MasterBoard()
    masterhex = random.choice(list(board.hexes.values()))
    logging.info(f"masterhex {masterhex}")
    entry_sides = set()
    for side, neighbor in enumerate(masterhex.neighbors):
        if neighbor is not None:
            if side & 1:
                entry_sides.add(side)
            else:
                entry_sides.add(side + 1)
    pick_entry_side, def1 = new(board, masterhex, {1, 3, 5}, None)
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]
