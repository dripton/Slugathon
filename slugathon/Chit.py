try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import guiutils

CHIT_SCALE_FACTOR = 3

class Chit(object):
    """Clickable GUI creature chit"""
    def __init__(self, creature, scale=15):
        self.creature = creature
        if creature is None:
            self.name = "QuestionMarkMask"
        else:
            self.name = creature.name
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file("../images/creature/%s.png" %
          self.name)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
        self.location = None    # (x, y) of top left corner

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def show(self):
        self.image.show()
