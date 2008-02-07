import gtk
import Image

import guiutils

CHIT_SCALE_FACTOR = 3

class Die(object):
    """Visible die image"""

    IMAGE_DIR = "dice"

    def __init__(self, number, hit=True, scale=15):
        self.name = "%s%d" % (("Miss", "Hit")[hit], number)
        self.chit_scale = CHIT_SCALE_FACTOR * scale

        path = "../images/%s/%s.png" % (self.IMAGE_DIR, self.name)
        im = Image.open(path).convert("RGBA")

        raw_pixbuf = guiutils.pil_image_to_gdk_pixbuf(im)
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
