#!/usr/bin/env python

__copyright__ = "Copyright (c) 2004-2009 David Ripton"
__license__ = "GNU GPL v2"


# TODO This dialog should always be on top.

import gtk

from slugathon.data.playercolordata import colors
from slugathon.gui import icon
from slugathon.util import guiutils


class PickColor(gtk.Dialog):
    """Dialog to pick a player color."""
    def __init__(self, user, username, game_name, colors_left, parent):
        gtk.Dialog.__init__(self, "Pick Color - %s" % username, parent)
        self.user = user
        self.username = username
        self.game_name = game_name

        self.vbox.set_spacing(9)
        label1 = gtk.Label("Pick a color")
        self.vbox.pack_start(label1)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_has_separator(False)

        hbox = gtk.HBox(len(colors), spacing=3)
        self.vbox.pack_start(hbox)
        for button_name in colors_left:
            button = gtk.Button(button_name)
            hbox.pack_start(button)
            button.connect("button-press-event", self.cb_click)
            color = button_name.lower()
            gtk_color = button.get_colormap().alloc_color(color)
            button.modify_bg(gtk.STATE_NORMAL, gtk_color)
            if color in ["black", "blue", "brown", "red"]:
                white = button.get_colormap().alloc_color("white")
                label = button.get_child()
                label.modify_fg(gtk.STATE_NORMAL, white)

        self.show_all()

    def cb_click(self, widget, event):
        color = widget.get_label()
        def1 = self.user.callRemote("pick_color", self.game_name, color)
        def1.addErrback(self.failure)
        self.destroy()

    def failure(self, error):
        print "PickColor.failure", error

if __name__ == "__main__":
    from twisted.internet import defer

    class NullUser(object):
        def callRemote(*args):
            return defer.Deferred()

    user = NullUser()
    username = "test user"
    game_name = "test game"
    colors_left = colors[:]
    colors_left.remove("Black")
    pickcolor = PickColor(user, username, game_name, colors_left, None)
    pickcolor.connect("destroy", guiutils.exit)
    gtk.main()
