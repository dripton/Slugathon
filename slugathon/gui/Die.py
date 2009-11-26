#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2008 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.util import guiutils


CHIT_SCALE_FACTOR = 3


class Die(object):
    """Visible die image"""

    IMAGE_DIR = "dice"

    def __init__(self, number, hit=True, scale=15):
        self.name = "%s%d" % (("Miss", "Hit")[hit], number)
        self.chit_scale = CHIT_SCALE_FACTOR * scale

        path = guiutils.basedir("images/%s/%s.png" % (self.IMAGE_DIR,
          self.name))
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.event_box = gtk.EventBox()
        self.event_box.chit = self
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
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
