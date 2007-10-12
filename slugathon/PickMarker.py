#!/usr/bin/env python

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk

import icon
import guiutils


class PickMarker(object):
    """Dialog to pick a legion marker."""
    def __init__(self, username, game_name, markers_left, callback, parent):
        self.username = username
        self.game_name = game_name
        self.callback = callback

        self.pick_marker_dialog = gtk.Dialog()

        self.pick_marker_dialog.set_icon(icon.pixbuf)
        self.pick_marker_dialog.set_title("PickMarker - %s" % (self.username))
        self.pick_marker_dialog.set_transient_for(parent)

        for ii, button_name in enumerate(markers_left):
            button = gtk.Button()
            button.tag = button_name
            pixbuf = gtk.gdk.pixbuf_new_from_file("../images/legion/%s.png" % 
              button_name)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            image.show()
            button.add(image)
            button.show()
            button.connect("button-press-event", self.cb_click)
            self.pick_marker_dialog.add_action_widget(button, ii + 1)

        self.pick_marker_dialog.show()

    def cb_click(self, widget, event):
        markername = widget.tag
        self.callback(self.game_name, self.username, markername)
        self.pick_marker_dialog.destroy()

if __name__ == "__main__":
    username = "test user"
    game_name = "test game"
    markers_left = ["Rd%02d" % ii for ii in xrange(1, 12+1)]
    pickmarker = PickMarker(username, game_name, markers_left, guiutils.exit, 
      None)
    pickmarker.pick_marker_dialog.connect("destroy", guiutils.exit)
    gtk.main()
