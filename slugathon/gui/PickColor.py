#!/usr/bin/env python

__copyright__ = "Copyright (c) 2004-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

import gtk
from twisted.internet import defer

from slugathon.data.playercolordata import colors
from slugathon.gui import icon
from slugathon.util.colors import contrasting_colors


def new(playername, game, colors_left, parent):
    """Return a PickColor dialog and a Deferred."""
    def1 = defer.Deferred()
    pickcolor = PickColor(playername, game, colors_left, parent, def1)
    return pickcolor, def1


class PickColor(gtk.Dialog):
    """Dialog to pick a player color."""
    def __init__(self, playername, game, colors_left, parent, def1):
        gtk.Dialog.__init__(self, "Pick Color - %s" % playername, parent)
        self.playername = playername
        self.game = game
        self.deferred = def1

        self.vbox.set_spacing(9)
        label1 = gtk.Label("Pick a color")
        self.vbox.pack_start(label1)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_has_separator(False)
        self.set_keep_above(True)

        hbox = gtk.HBox(len(colors), spacing=3)
        self.vbox.pack_start(hbox)
        for button_name in colors_left:
            button = gtk.Button(button_name)
            hbox.pack_start(button)
            button.connect("button-press-event", self.cb_click)
            color = button_name
            gtk_color = button.get_colormap().alloc_color(color)
            button.modify_bg(gtk.STATE_NORMAL, gtk_color)
            fg_name = contrasting_colors[color]
            fg_color = button.get_colormap().alloc_color(fg_name)
            label = button.get_child()
            label.modify_fg(gtk.STATE_NORMAL, fg_color)

        self.connect("destroy", self.cb_destroy)
        self.show_all()

    def cb_click(self, widget, event):
        color = widget.get_label()
        self.deferred.callback((self.game, color))
        self.destroy()

    def cb_destroy(self, widget):
        if not self.deferred.called:
            self.deferred.callback((self.game, None))

if __name__ == "__main__":
    import time
    from slugathon.game import Game
    from slugathon.util import guiutils

    def my_callback((game, color)):
        logging.info("picked %s", color)
        guiutils.exit()

    now = time.time()
    playername = "test user"
    game = Game.Game("test game", playername, now, now, 2, 6)
    colors_left = colors[:]
    colors_left.remove("Black")
    pickcolor, def1 = new(playername, game, colors_left, None)
    def1.addCallback(my_callback)
    pickcolor.connect("destroy", guiutils.exit)
    gtk.main()
