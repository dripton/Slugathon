try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk

CHIT_SCALE_FACTOR = 3

class Marker(object):
    """Clickable GUI legion marker"""
    def __init__(self, name, scale=15):
        self.name = name
        raw_pixbuf = gtk.gdk.pixbuf_new_from_file("../images/legion/%s.png" % 
          name)
        chit_scale = CHIT_SCALE_FACTOR * scale
        self.pixbuf = raw_pixbuf.scale_simple(chit_scale, chit_scale, 
          gtk.gdk.INTERP_BILINEAR)
