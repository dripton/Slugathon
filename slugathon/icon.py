"""Just a place to load the icon image."""

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk

pixbuf = gtk.gdk.pixbuf_new_from_file("../images/creature/Serpent.png")
