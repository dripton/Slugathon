#!/usr/bin/env python

__copyright__ = "Copyright (c) 2004-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor, defer
import gtk

from slugathon.gui import icon
from slugathon.util import guiutils


def new(username, game_name, markers_left, parent):
    """Create a PickMarker dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    pickmarker = PickMarker(username, game_name, markers_left, def1, parent)
    return pickmarker, def1

class PickMarker(gtk.Dialog):
    """Dialog to pick a legion marker."""
    def __init__(self, username, game_name, markers_left, def1, parent):
        title = "PickMarker - %s" % username
        gtk.Dialog.__init__(self, title, parent)
        self.username = username
        self.game_name = game_name
        self.deferred = def1
        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)

        for ii, button_name in enumerate(markers_left):
            button = gtk.Button()
            button.tag = button_name
            pixbuf = gtk.gdk.pixbuf_new_from_file(guiutils.basedir(
              "images/legion/%s.png" % button_name))
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            button.add(image)
            button.connect("button-press-event", self.cb_click)
            self.add_action_widget(button, ii + 1)

        self.connect("destroy", self.cb_destroy)
        self.show_all()

    def cb_click(self, widget, event):
        markername = widget.tag
        self.deferred.callback((self.game_name, self.username, markername))
        self.destroy()

    def cb_destroy(self, widget):
        if not self.deferred.called:
            self.deferred.callback((self.game_name, self.username, None))


if __name__ == "__main__":
    def my_callback((game_name, username, markername)):
        print "picked", markername
        reactor.stop()

    username = "test user"
    game_name = "test game"
    markers_left = ["Rd%02d" % ii for ii in xrange(1, 12+1)]
    pickmarker, def1 = new(username, game_name, markers_left, None)
    def1.addCallback(my_callback)
    reactor.run()
