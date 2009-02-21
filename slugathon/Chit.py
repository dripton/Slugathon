#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

import tempfile
import os

import gtk
import cairo
import pango
import pangocairo

import guiutils
import colors
import Creature

CHIT_SCALE_FACTOR = 3

red = colors.rgb_colors["red"]
white = colors.rgb_colors["white"]

class Chit(object):
    """Clickable GUI creature chit"""

    IMAGE_DIR = "creature"

    def __init__(self, creature, playercolor, scale=15, dead=False,
      rotate=None):
        self.creature = creature
        if creature is None:
            self.name = "QuestionMarkMask"
        else:
            self.name = creature.name
        self.dead = dead
        self.rotate = rotate
        self.location = None    # (x, y) of top left corner
        self.chit_scale = CHIT_SCALE_FACTOR * scale

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
            color_name = "titan_%s" % playercolor.lower()
        self.rgb = guiutils.rgb_to_float(colors.rgb_colors[color_name])

        self.paths = ["../images/%s/%s.png" % (self.IMAGE_DIR, base)
          for base in self.bases]

        self.event_box = gtk.EventBox()
        self.event_box.chit = self
        self.image = gtk.Image()
        self.event_box.add(self.image)
        self.build_image()

    def build_image(self):
        path = self.paths[0]
        surface = cairo.ImageSurface.create_from_png(path)
        ctx = cairo.Context(surface)
        for path in self.paths[1:]:
            mask = cairo.ImageSurface.create_from_png(path)
            ctx.set_source_rgb(*self.rgb)
            ctx.mask_surface(mask, 0, 0)
        self._render_text(surface)
        if self.dead or (self.creature and self.creature.dead):
            self._render_x(surface)
        elif self.creature and self.creature.hits > 0:
            self._render_hits(surface)
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="slugathon", suffix=".png")
        tmp_file = os.fdopen(tmp_fd, "wb")
        tmp_file.close()
        surface.write_to_png(tmp_path)
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file(tmp_path)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        if self.rotate:
            self.pixbuf = self.pixbuf.rotate_simple(self.rotate)
        self.image.set_from_pixbuf(self.pixbuf)
        os.remove(tmp_path)

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def show(self):
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
        pctx = pangocairo.CairoContext(ctx)
        layout = pctx.create_layout()
        # TODO Vary font size with scale
        desc = pango.FontDescription("monospace 9")
        layout.set_font_description(desc)
        pctx.set_source_rgb(*self.rgb)
        pctx.set_line_width(1)
        size = surface.get_width()
        layout.set_width(size)
        layout.set_alignment(pango.ALIGN_CENTER)

        # Name
        if self.name != "Titan":
            label = self.name.upper()
            # TODO If width is too big, try a smaller font
            x = 0.5 * size
            y = 0
            pctx.move_to(x, y)
            layout.set_text(label)
            pctx.show_layout(layout)

        # Power
        label = str(self.creature.power)
        x = 0.07 * size
        y = 0.77 * size
        pctx.move_to(x , y)
        layout.set_text(label)
        pctx.show_layout(layout)

        # Skill
        label = str(self.creature.skill)
        x = 0.9 * size
        y = 0.77 * size
        pctx.move_to(x, y)
        layout.set_text(label)
        pctx.show_layout(layout)

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

    def _render_hits(self, surface):
        """Add the number of hits to a Cairo surface"""
        if not self.creature or not self.creature.hits:
            return
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        pctx = pangocairo.CairoContext(ctx)
        layout = pctx.create_layout()
        layout.set_alignment(pango.ALIGN_CENTER)

        # TODO Vary font size with scale
        desc = pango.FontDescription("monospace 20")
        layout.set_font_description(desc)
        layout.set_text(str(self.creature.hits))
        size = surface.get_width()
        layout.set_width(size)
        pctx.set_source_rgb(1, 0, 0)

        x = 0.5 * size
        y = 0.2 * size
        pctx.set_source_rgb(1, 1, 1)
        pctx.set_line_width(1)
        width, height = layout.get_pixel_size()
        pctx.rectangle(x - 0.5 * width, y, 0.9 * width, 0.8 * height)
        pctx.fill()

        pctx.set_source_rgb(1, 0, 0)
        pctx.move_to(x, y)
        pctx.show_layout(layout)


if __name__ == "__main__":
    creature = Creature.Creature("Ogre")
    creature.hits = 3
    chit = Chit(creature, "Red", scale=45)
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)
    window.add(chit.event_box)
    window.show()
    chit.show()
    gtk.main()
