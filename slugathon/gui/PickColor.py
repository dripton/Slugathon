#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, List, Tuple

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from twisted.internet import defer

from slugathon.data.playercolordata import colors
from slugathon.game import Game
from slugathon.gui import icon
from slugathon.util.colors import contrasting_colors


__copyright__ = "Copyright (c) 2004-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    playername: str,
    game: Game.Game,
    colors_left: List[str],
    parent: Gtk.Window,
) -> Tuple[PickColor, defer.Deferred]:
    """Return a PickColor dialog and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pickcolor = PickColor(playername, game, colors_left, parent, def1)
    return pickcolor, def1


class PickColor(Gtk.Dialog):
    """Dialog to pick a player color."""

    def __init__(
        self,
        playername: str,
        game: Game.Game,
        colors_left: List[str],
        parent: Gtk.Window,
        def1: defer.Deferred,
    ):
        GObject.GObject.__init__(
            self, title=f"Pick Color - {playername}", parent=parent
        )
        self.playername = playername
        self.game = game
        self.deferred = def1

        self.vbox.set_spacing(9)
        label1 = Gtk.Label(label="Pick a color")
        self.vbox.pack_start(label1, True, True, 0)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_keep_above(True)

        hbox = Gtk.HBox(homogeneous=True, spacing=3)
        self.vbox.pack_start(hbox, True, True, 0)
        for button_name in colors_left:
            button = Gtk.Button(label=button_name)
            hbox.pack_start(button, True, True, 0)
            button.connect("button-press-event", self.cb_click)
            color = button_name
            bg_gtkcolor = Gdk.color_parse(color)
            button.modify_bg(Gtk.StateType.NORMAL, bg_gtkcolor)
            fg_name = contrasting_colors[color]
            fg_gtkcolor = Gdk.color_parse(fg_name)
            label = button.get_child()
            label.modify_fg(Gtk.StateType.NORMAL, fg_gtkcolor)

        self.connect("destroy", self.cb_destroy)
        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Gdk.EventButton) -> None:
        color = widget.get_label()
        self.deferred.callback((self.game, color))
        self.destroy()

    def cb_destroy(self, widget: Gtk.Widget) -> None:
        if not self.deferred.called:
            self.deferred.callback((self.game, None))


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils

    def my_callback(tup: Tuple[Game.Game, str]) -> None:
        (game, color) = tup
        logging.info(f"picked {color}")
        guiutils.exit()

    now = time.time()
    playername = "test user"
    game = Game.Game("test game", playername, now, now, 2, 6)
    colors_left = colors[:]
    colors_left.remove("Black")
    pickcolor, def1 = new(playername, game, colors_left, None)
    def1.addCallback(my_callback)
    pickcolor.connect("destroy", guiutils.exit)
    Gtk.main()
