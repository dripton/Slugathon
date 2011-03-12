#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"


import os
import tempfile

import gtk
import cairo

from slugathon.util import fileutils


CHIT_SCALE_FACTOR = 3


class Die(object):
    """Visible die image"""

    IMAGE_DIR = "dice"

    def __init__(self, number, hit=True, scale=15):
        self.name = "%s%d" % (("Miss", "Hit")[hit], number)
        self.chit_scale = CHIT_SCALE_FACTOR * scale

        path = fileutils.basedir("images/%s/%s.png" % (self.IMAGE_DIR,
          self.name))
        input_surface = cairo.ImageSurface.create_from_png(path)
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
        self.event_box.chit = self
        self.image = gtk.Image()
        self.image.set_from_pixbuf(pixbuf)
        self.event_box.add(self.image)
        self.location = None    # (x, y) of top left corner

    def show(self):
        self.event_box.show()
        self.image.show()

if __name__ == "__main__":
    from slugathon.util import Dice

    die = Die(Dice.roll()[0], scale=45)
    window = gtk.Window()
    window.connect("destroy", gtk.main_quit)
    window.add(die.event_box)
    window.show()
    die.show()
    gtk.main()
