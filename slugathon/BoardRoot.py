try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade


class BoardRoot(object):
    """Root Window for GUIMasterBoard."""
    def __init__(self, username):
        print "BoardRoot.__init__(%s)" % username
        self.username = username

        self.glade = gtk.glade.XML("../glade/boardroot.glade")
        self.widgets = ["root"]
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          "../images/creature/Colossus.png")
        self.root.set_icon(pixbuf)
        self.root.set_title("%s - %s" % (self.root.get_title(), self.username))
