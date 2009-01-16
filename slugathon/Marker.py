__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

# TODO show titan power

import tempfile
import os

import gtk
import cairo

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
        cr = cairo.Context(surface)
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
          cairo.FONT_WEIGHT_NORMAL)
        # TODO Vary font size with scale
        cr.set_font_size(20)
        size = surface.get_width()

        label = str(self.height)
        x_bearing, y_bearing, width, height = cr.text_extents(label)[:4]
        x = 0.65 * size - width - x_bearing
        y = 0.55 * size - height - y_bearing
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x - 0.1 * width, y - 0.1 * height, 1.2 * width,
          1.2 * height)
        cr.fill()

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(x, y + height)
        cr.text_path(label)
        cr.stroke_preserve()
        cr.fill()
