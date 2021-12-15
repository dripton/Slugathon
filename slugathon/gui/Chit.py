#!/usr/bin/env python3


import tempfile
import os
import math
from typing import Optional, Tuple

import gi

gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
gi.require_version("PangoCairo", "1.0")
import cairo
from gi.repository import Gtk, Pango, PangoCairo, GdkPixbuf

from slugathon.game import Creature
from slugathon.util import guiutils, colors, fileutils


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


CHIT_SCALE_FACTOR = 3

red = colors.rgb_colors["red"]
white = colors.rgb_colors["white"]


class Chit(object):

    """Clickable GUI creature chit"""

    IMAGE_DIR = "creature"

    def __init__(
        self,
        creature: Optional[Creature.Creature],
        playercolor: Optional[str],
        scale: int = 15,
        dead: bool = False,
        rotate: int = 0,
        outlined: bool = False,
        name: Optional[str] = None,
    ):
        self.creature = creature
        if creature is None:
            if name is None:
                self.name = "QuestionMark"
            else:
                self.name = name
        else:
            self.name = creature.name
        self.dead = dead
        # Convert from degrees to radians, and from GTK rotation direction
        # to Cairo.
        self.rotate = -rotate * math.pi / 180
        self.outlined = outlined
        # (x, y) of top left corner
        self.location = None  # type: Optional[Tuple[float, float]]
        self.chit_scale = CHIT_SCALE_FACTOR * scale

        if (
            creature
            and creature.name in ["Titan", "Angel"]
            and playercolor is not None
        ):
            self.bases = [self.name + playercolor]
        else:
            self.bases = [self.name]
        if creature:
            color_name = creature.color_name
            if creature.flies and creature.rangestrikes:
                self.bases.append("FlyingRangestrikeBase")
            elif creature.flies:
                self.bases.append("FlyingBase")
            elif creature.rangestrikes:
                self.bases.append("RangestrikeBase")
        else:
            color_name = "black"
        if color_name == "by_player":
            assert playercolor is not None
            color_name = f"titan_{playercolor.lower()}"
        self.rgb = guiutils.rgb_to_float(colors.rgb_colors[color_name])

        self.paths = [
            fileutils.basedir(f"images/{self.IMAGE_DIR}/{base}.png")
            for base in self.bases
        ]

        self.event_box = Gtk.EventBox()
        self.event_box.chit = self
        self.image = Gtk.Image()
        self.event_box.add(self.image)
        self.build_image()

    def build_image(self):
        path = self.paths[0]
        input_surface = cairo.ImageSurface.create_from_png(path)
        ctx = cairo.Context(input_surface)
        for path in self.paths[1:]:
            mask = cairo.ImageSurface.create_from_png(path)
            ctx.set_source_rgb(*self.rgb)
            ctx.mask_surface(mask, 0, 0)
        self._render_text(input_surface)
        if self.dead or (self.creature and self.creature.dead):
            self._render_x(input_surface)
        elif self.creature and self.creature.hits > 0:
            self._render_hits(input_surface)
        if self.outlined:
            self._render_outline(input_surface)
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, int(self.chit_scale), int(self.chit_scale)
        )
        ctx2 = cairo.Context(self.surface)
        if self.rotate:
            ctx2.translate(self.chit_scale / 2.0, self.chit_scale / 2.0)
            ctx2.rotate(self.rotate)
            ctx2.translate(-self.chit_scale / 2.0, -self.chit_scale / 2.0)
        ctx2.scale(
            float(self.chit_scale) / input_surface.get_width(),
            float(self.chit_scale) / input_surface.get_height(),
        )
        ctx2.set_source_surface(input_surface)
        ctx2.paint()
        with tempfile.NamedTemporaryFile(
            prefix="slugathon", suffix=".png", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name
        self.surface.write_to_png(tmp_path)
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(tmp_path)
        os.remove(tmp_path)
        self.image.set_from_pixbuf(self.pixbuf)

    def point_inside(self, point: Tuple[float, float]) -> bool:
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def show(self) -> None:
        self.event_box.show()
        self.image.show()

    def connect(self, event, method):
        self.event_box.connect(event, method)

    def _render_text(self, surface):
        """Add creature name, power, and toughness to a Cairo surface"""
        if not self.creature:
            return
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        layout = PangoCairo.create_layout(ctx)
        # TODO Vary font size with scale
        desc = Pango.FontDescription("monospace 9")
        layout.set_font_description(desc)
        ctx.set_source_rgb(*self.rgb)
        ctx.set_line_width(1)
        size = surface.get_width()
        layout.set_width(size)
        layout.set_alignment(Pango.Alignment.CENTER)

        # Name
        if self.name != "Titan":
            label = self.name.upper()
            # TODO If width is too big, try a smaller font
            x = 0.5 * size
            y = 0
            ctx.move_to(x, y)
            layout.set_text(label)
            PangoCairo.show_layout(ctx, layout)

        # Power
        if not self.creature.is_unknown:
            label = str(self.creature.power)
            x = 0.14 * size
            y = 0.77 * size
            ctx.move_to(x, y)
            layout.set_text(label)
            PangoCairo.show_layout(ctx, layout)

        # Skill
        if not self.creature.is_unknown:
            label = str(self.creature.skill)
            x = 0.9 * size
            y = 0.77 * size
            ctx.move_to(x, y)
            layout.set_text(label)
            PangoCairo.show_layout(ctx, layout)

    def _render_x(self, surface):
        """Add a big red X through a Cairo surface"""
        ctx = cairo.Context(surface)
        size = surface.get_width()
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(2)
        ctx.move_to(0, 0)
        ctx.line_to(size, size)
        ctx.move_to(0, size)
        ctx.line_to(size, 0)
        ctx.stroke()

    def _render_outline(self, surface):
        """Add a red rectangle around a Cairo surface"""
        ctx = cairo.Context(surface)
        size = surface.get_width()
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(4)
        ctx.move_to(0, 0)
        ctx.line_to(size, 0)
        ctx.line_to(size, size)
        ctx.line_to(0, size)
        ctx.line_to(0, 0)
        ctx.stroke()

    def _render_hits(self, surface):
        """Add the number of hits to a Cairo surface"""
        if not self.creature or not self.creature.hits:
            return
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        layout = PangoCairo.create_layout(ctx)
        layout.set_alignment(Pango.Alignment.CENTER)

        # TODO Vary font size with scale
        desc = Pango.FontDescription("monospace 20")
        layout.set_font_description(desc)
        layout.set_text(str(self.creature.hits))
        size = surface.get_width()
        layout.set_width(size)
        ctx.set_source_rgb(1, 0, 0)

        x = 0.5 * size
        y = 0.2 * size
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(1)
        width, height = layout.get_pixel_size()
        ctx.rectangle(x - 0.5 * width, y, 0.9 * width, 0.8 * height)
        ctx.fill()

        ctx.set_source_rgb(1, 0, 0)
        ctx.move_to(x, y)
        PangoCairo.show_layout(ctx, layout)


if __name__ == "__main__":
    creature = Creature.Creature("Ogre")
    creature.hits = 3
    chit = Chit(creature, "Red", scale=45, rotate=90)
    window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit)
    window.add(chit.event_box)
    window.show()
    chit.show()
    Gtk.main()
