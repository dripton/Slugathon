from __future__ import annotations
import os
import math
from sys import maxsize
from typing import List, Optional, Tuple

import cairo
import gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

from slugathon.game import BattleHex
from slugathon.gui import GUIBattleMap
from slugathon.util import guiutils, colors, sliceborder, fileutils


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180.0 / math.pi

# Where to place the label, by hexside.  Derived experimentally.
x_font_position = [0.5, 0.7, 0.7, 0.5, 0.35, 0.35]
y_font_position = [0.2, 0.2, 0.8, 0.8, 0.8, 0.2]

rp = guiutils.roundpoint

IMAGE_DIR = fileutils.basedir("images/battlehex")


class GUIBattleHex(object):
    def __init__(
        self, battlehex: BattleHex.BattleHex, guimap: GUIBattleMap.GUIBattleMap
    ):
        self.battlehex = battlehex
        self.guimap = guimap
        scale = self.guimap.scale
        # Leftmost point
        self.cx = (battlehex.x + 1) * 3 * scale
        # Uppermost point
        self.cy = battlehex.y * 2 * SQRT3 * scale
        if battlehex.down:
            self.cy += SQRT3 * scale
        self.fillcolor = self.find_fillcolor()
        self.selected = False

        self.init_vertexes()
        self.center = rp(guiutils.midpoint(self.vertexes[0], self.vertexes[3]))
        self.bboxsize = rp(
            (
                self.vertexes[2][0] - self.vertexes[5][0],
                self.vertexes[3][1] - self.vertexes[0][1],
            )
        )
        self.hex_surface = None  # type: Optional[cairo.ImageSurface]
        self.hex_surface_x = None  # type: Optional[int]
        self.hex_surface_y = None  # type: Optional[int]
        self.border_surfaces = []  # type: List[Optional[cairo.Surface]]
        self.border_surface_x = None  # type: Optional[float]
        self.border_surface_y = None  # type: Optional[float]
        self.init_hex_overlay()
        self.init_border_overlays()

    def find_fillcolor(self) -> Tuple[float, ...]:
        terrain = self.battlehex.terrain
        color = colors.battle_terrain_colors.get(
            (terrain, self.battlehex.elevation), None
        )
        if not color:
            color = colors.battle_terrain_colors[terrain]
        return guiutils.rgb_to_float(colors.rgb_colors[color])

    def init_vertexes(self) -> None:
        """Setup the hex vertexes.

        Each vertex is the midpoint between the vertexes of the two
        bordering hexes.
        """
        self.vertexes = []  # type: List[Tuple[float, float]]
        for unused in range(6):
            self.vertexes.append((0.0, 0.0))
        cx = self.cx
        cy = self.cy
        scale = self.guimap.scale

        if self.battlehex.entrance:
            self.vertexes[0] = rp((cx + 1.5 * scale, cy - 3 * scale))
            self.vertexes[1] = rp((cx + 3 * scale, cy - 3 * scale))
            self.vertexes[2] = rp((cx + 3 * scale, cy + 3 * scale))
            self.vertexes[3] = rp((cx + 3 * scale, cy + 9 * scale))
            self.vertexes[4] = rp((cx + 1.5 * scale, cy + 9 * scale))
            self.vertexes[5] = rp((cx + 1.5 * scale, cy + 3 * scale))
        else:
            self.vertexes[0] = rp((cx + scale, cy))
            self.vertexes[1] = rp((cx + 3 * scale, cy))
            self.vertexes[2] = rp((cx + 4 * scale, cy + SQRT3 * scale))
            self.vertexes[3] = rp((cx + 3 * scale, cy + 2 * SQRT3 * scale))
            self.vertexes[4] = rp((cx + scale, cy + 2 * SQRT3 * scale))
            self.vertexes[5] = rp((cx, cy + SQRT3 * scale))

        self.points = []
        iv = guiutils.scale_polygon(self.vertexes, 0.9)
        for point in iv:
            self.points.append(rp(point))

    @property
    def bounding_rect(self):
        """Return the bounding rectangle (x, y, width, height) of this hex."""
        min_x = float(maxsize)
        max_x = float(-maxsize)
        min_y = float(maxsize)
        max_y = float(-maxsize)
        for x, y in self.vertexes:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        return min_x, min_y, max_x - min_x, max_y - min_y

    def draw_hexagon(self, ctx: cairo.Context):
        """Create the polygon, filled with the terrain color."""
        # inner hex
        ctx.set_source_rgb(*self.fillcolor)
        guiutils.draw_polygon(ctx, self.points)
        ctx.fill()

    def draw_selection(self, ctx: cairo.Context):
        """If the hex is selected, draw the red outline."""
        if self.selected:
            ctx.set_source_rgba(1, 0, 0, 0.8)
            guiutils.draw_polygon(ctx, self.points)
            ctx.stroke()

    def init_hex_overlay(self) -> None:
        """Setup the overlay with terrain name and image."""
        overlay_filename = f"{self.battlehex.terrain}.png"
        image_path = os.path.join(IMAGE_DIR, overlay_filename)
        if not os.path.exists(image_path):
            return
        myboxsize = [int(round(0.85 * mag)) for mag in self.bboxsize]
        self.hex_surface_x = int(round(self.center[0] - myboxsize[0] / 2.0))
        self.hex_surface_y = int(round(self.center[1] - myboxsize[1] / 2.0))
        input_surface = cairo.ImageSurface.create_from_png(image_path)
        input_width = input_surface.get_width()
        input_height = input_surface.get_height()
        output_width = int(myboxsize[0])
        output_height = int(myboxsize[1])
        self.hex_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, output_width, output_height
        )
        ctx = cairo.Context(self.hex_surface)
        ctx.scale(
            float(output_width) / input_width,
            float(output_height) / input_height,
        )
        ctx.move_to(0, 0)
        ctx.set_source_surface(input_surface)
        ctx.paint()

    def init_border_overlays(self) -> None:
        """Setup the overlays for each border."""
        myboxsize = [int(round(0.97 * mag)) for mag in self.bboxsize]
        self.border_surface_x = int(round(self.center[0] - myboxsize[0] / 2.0))
        self.border_surface_y = int(round(self.center[1] - myboxsize[1] / 2.0))
        for hexside, border in enumerate(self.battlehex.borders):
            border_surface = None
            overlay_filename = f"{border}.png"
            image_path = os.path.join(IMAGE_DIR, overlay_filename)
            if os.path.exists(image_path):
                assert border is not None
                hexsides = self.battlehex.hexsides_with_border(border)
                hexsides_str = "".join(map(str, sorted(hexsides)))
                border_filename = f"{border}-{hexsides_str}.png"
                border_path = os.path.join(IMAGE_DIR, border_filename)
                if not os.path.exists(border_path):
                    sliceborder.slice_border_image(
                        image_path, border_path, hexsides
                    )
                input_surface = cairo.ImageSurface.create_from_png(border_path)
                input_width = input_surface.get_width()
                input_height = input_surface.get_height()
                output_width = int(myboxsize[0])
                output_height = int(myboxsize[1])
                border_surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, output_width, output_height
                )
                ctx = cairo.Context(border_surface)
                ctx.scale(
                    float(output_width) / input_width,
                    float(output_height) / input_height,
                )
                ctx.move_to(0, 0)
                ctx.set_source_surface(input_surface)
                ctx.paint()
            self.border_surfaces.append(border_surface)

    def draw_hex_overlay(self, ctx: cairo.Context):
        """Draw the main terrain overlay for the hex."""
        if self.hex_surface is None:
            return
        assert self.hex_surface_x is not None
        assert self.hex_surface_y is not None
        ctx.set_source_surface(
            self.hex_surface, self.hex_surface_x, self.hex_surface_y
        )
        ctx.paint()

    def draw_border_overlays(self, ctx: cairo.Context):
        """Draw the overlays for all borders that have them."""
        for hexside, border in enumerate(self.battlehex.borders):
            if border:
                border_surface = self.border_surfaces[hexside]
                assert border_surface is not None
                assert self.border_surface_x is not None
                assert self.border_surface_y is not None
                ctx.set_source_surface(
                    border_surface,
                    self.border_surface_x,
                    self.border_surface_y,
                )
                ctx.paint()

    def draw_label(self, ctx: cairo.Context, label, side):
        """Display the hex label."""
        layout = PangoCairo.create_layout(ctx)
        # TODO Vary font size with scale
        desc = Pango.FontDescription("Monospace 14")
        layout.set_font_description(desc)
        layout.set_alignment(Pango.Alignment.CENTER)
        layout.set_text(label)
        width, height = layout.get_pixel_size()
        x = int(
            round(
                (
                    self.cx
                    + self.bboxsize[0] * x_font_position[side]
                    - width / 2.0
                )
            )
        )
        y = int(
            round(
                (
                    self.cy
                    + self.bboxsize[1] * y_font_position[side]
                    - height / 2.0
                )
            )
        )
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(x, y)
        PangoCairo.show_layout(ctx, layout)

    def update_gui(self, ctx: cairo.Context) -> None:
        self.draw_hexagon(ctx)
        if not self.battlehex.entrance:
            self.draw_hex_overlay(ctx)
            self.draw_border_overlays(ctx)
            self.draw_label(
                ctx, self.battlehex.label, self.battlehex.label_side
            )
            self.draw_label(
                ctx, self.battlehex.terrain, self.battlehex.terrain_side
            )
        self.draw_selection(ctx)

    def __repr__(self) -> str:
        return f"GUIBattleHex {self.battlehex.label}"
