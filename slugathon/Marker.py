try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import guiutils

CHIT_SCALE_FACTOR = 3

class Marker(object):
    """Clickable GUI legion marker"""
    def __init__(self, legion, scale=15):
        self.legion = legion
        self.name = legion.marker
        self.hex = legion.hex
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file("../images/legion/%s.png" % 
          self.name)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.location = None    # (x, y) of top left corner

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)
