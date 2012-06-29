#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


import tempfile
import os

import gtk
import cairo
import pango
import pangocairo

from slugathon.util import guiutils, fileutils


CHIT_SCALE_FACTOR = 3


class Marker(object):
    """Clickable GUI legion marker"""
    def __init__(self, legion, show_height, scale=15):
        self.legion = legion
        self.name = legion.markerid
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        self.show_height = show_height
        self.image_path = fileutils.basedir("images/legion/%s.png" % self.name)
        self.location = None    # (x, y) of top left corner
        self.build_image()

    def build_image(self):
        self.height = len(self.legion)
        input_surface = cairo.ImageSurface.create_from_png(self.image_path)
        self._render_text(input_surface)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.chit_scale,
          self.chit_scale)
        ctx = cairo.Context(self.surface)
        ctx.scale(float(self.chit_scale) / input_surface.get_width(),
          float(self.chit_scale) / input_surface.get_height())
        ctx.set_source_surface(input_surface)
        ctx.paint()
        with tempfile.NamedTemporaryFile(prefix="slugathon",
          suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        self.surface.write_to_png(tmp_path)
        pixbuf = gtk.gdk.pixbuf_new_from_file(tmp_path)
        os.remove(tmp_path)
        self.event_box = gtk.EventBox()
        self.event_box.marker = self
        self.image = gtk.Image()
        self.image.set_from_pixbuf(pixbuf)
        self.event_box.add(self.image)

    def __repr__(self):
        return "Marker %s in %s" % (self.name, self.legion.hexlabel)

    def point_inside(self, point):
        if not self.location:
            return False
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def update_height(self):
        if self.show_height and self.height != len(self.legion):
            self.build_image()

    def show(self):
        self.event_box.show()
        self.image.show()

    def connect(self, event, method):
        self.event_box.connect(event, method)

    def _render_text(self, surface):
        """Add legion height to a Cairo surface."""
        if not self.show_height:
            return
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        pctx = pangocairo.CairoContext(ctx)
        layout = pctx.create_layout()
        # TODO Vary font size with scale
        desc = pango.FontDescription("Monospace 17")
        layout.set_font_description(desc)
        layout.set_alignment(pango.ALIGN_CENTER)
        size = surface.get_width()

        layout.set_text(str(self.height))
        width, height = layout.get_pixel_size()
        x = 0.65 * size
        y = 0.55 * size
        pctx.set_source_rgb(1, 1, 1)
        pctx.rectangle(x, y + 0.15 * height, 0.9 * width, 0.7 * height)
        pctx.fill()

        pctx.set_source_rgb(0, 0, 0)
        pctx.move_to(x, y)
        pctx.show_layout(layout)


if __name__ == "__main__":
    import time
    from slugathon.data import creaturedata
    from slugathon.game import Creature, Player, Game, Legion

    now = time.time()
    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]
    playername = "test"
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    marker = Marker(legion, True, scale=45)
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)
    window.add(marker.event_box)
    window.show_all()
    gtk.main()
