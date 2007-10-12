#!/usr/bin/env python

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
from twisted.internet import defer

from playercolordata import colors
import icon
import guiutils


class PickColor(object):
    """Dialog to pick a player color."""
    def __init__(self, user, username, game_name, colors_left, parent):
        print "PickColor.__init__", self, user, username, colors_left
        self.user = user
        self.username = username
        self.game_name = game_name
        self.glade = gtk.glade.XML("../glade/pickcolor.glade")
        self.widget_names = ["pick_color_dialog", "label1"] + colors
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.glade.get_widget(widget_name))
        print("dir(PickColor) is %s" % dir(self))

        self.pick_color_dialog.set_icon(icon.pixbuf)
        self.pick_color_dialog.set_title("%s - %s" % (
          self.pick_color_dialog.get_title(), self.username))
        self.pick_color_dialog.set_transient_for(parent)

        for button_name in colors:
            button = getattr(self, button_name)
            if button_name in colors_left: 
                button.connect("button-press-event", self.cb_click)
            else:
                button.set_label("")

    def cb_click(self, widget, event):
        print "PickColor.cb_click", self, widget, event
        print("dir(PickColor) is %s" % dir(self))
        color = widget.get_label()
        print color
        def1 = self.user.callRemote("pick_color", self.game_name, color)
        def1.addErrback(self.failure)
        self.pick_color_dialog.destroy()

    def failure(self, error):
        print "PickColor.failure", error

if __name__ == "__main__":
    class NullUser(object):
        def callRemote(*args):
            return defer.Deferred()

    user = NullUser()
    username = "test user"
    game_name = "test game"
    colors_left = colors[:]
    pickcolor = PickColor(user, username, game_name, colors_left, None)
    pickcolor.pick_color_dialog.connect("destroy", guiutils.exit)
    gtk.main()
