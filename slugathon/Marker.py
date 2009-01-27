__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

# TODO show titan power

import tempfile
import os

import gtk
import cairo
import pango
import pangocairo

import guiutils

CHIT_SCALE_FACTOR = 3


class Marker(object):
    """Clickable GUI legion marker"""
    def __init__(self, legion, show_height, scale=15):
        self.legion = legion
        self.name = legion.markername
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        self.show_height = show_height
        self.image_path = "../images/legion/%s.png" % self.name
        self.location = None    # (x, y) of top left corner
        self.build_image()

    def build_image(self):
        self.height = len(self.legion)
        surface = cairo.ImageSurface.create_from_png(self.image_path)
        self._render_text(surface)
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="slugathon", suffix=".png")
        tmp_file = os.fdopen(tmp_fd, "wb")
        tmp_file.close()
        surface.write_to_png(tmp_path)
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file(tmp_path)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.event_box = gtk.EventBox()
        self.event_box.marker = self
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
        self.event_box.add(self.image)
        os.remove(tmp_path)

    def __repr__(self):
        return "Marker %s in %s" % (self.name, self.legion.hexlabel)

    def point_inside(self, point):
        assert self.location
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
        desc = pango.FontDescription("Monospace 18")
        layout.set_font_description(desc)
        layout.set_alignment(pango.ALIGN_CENTER)
        size = surface.get_width()

        layout.set_text(str(self.height))
        width, height = layout.get_pixel_size()
        x = 0.65 * size
        y = 0.55 * size
        pctx.set_source_rgb(1, 1, 1)
        pctx.rectangle(x, y, width, height)
        pctx.fill()

        pctx.set_source_rgb(0, 0, 0)
        pctx.move_to(x, y)
        pctx.show_layout(layout)
