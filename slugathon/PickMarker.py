try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk


class PickMarker(object):
    """Dialog to pick a legion marker."""
    def __init__(self, client, username, game_name, markers_left):
        print "PickMarker.__init__", client, username, game_name, markers_left
        self.client = client
        self.username = username
        self.game_name = game_name
        self.pick_marker_dialog = gtk.Dialog()

        pixbuf = gtk.gdk.pixbuf_new_from_file(
          "../images/creature/Colossus.png")
        self.pick_marker_dialog.set_icon(pixbuf)
        self.pick_marker_dialog.set_title("PickMarker - %s" % (self.username))

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
        print "PickMarker.cb_click", self, widget, event
        marker = widget.tag
        self.client.pick_marker(self.game_name, self.username, marker)
        self.pick_marker_dialog.destroy()
