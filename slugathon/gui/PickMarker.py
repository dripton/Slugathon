#!/usr/bin/env python3

from __future__ import annotations

import collections
import logging
from typing import Any, DefaultDict, List, Tuple

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import defer, reactor

from slugathon.gui import icon
from slugathon.util import fileutils


__copyright__ = "Copyright (c) 2004-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    playername: str,
    game_name: str,
    markers_left: List[str],
    parent: Gtk.Window,
) -> Tuple[PickMarker, defer.Deferred]:
    """Create a PickMarker dialog and return it and a Deferred."""
    def1 = defer.Deferred()  # type: defer.Deferred
    pickmarker = PickMarker(playername, game_name, markers_left, def1, parent)
    return pickmarker, def1


def sorted_markers(markers: List[str]) -> List[str]:
    """Return a copy of markers sorted so that the colors that have the
    fewest markers left come first.

    The intent is to have the player's own color first, then the color
    of captured markers that he's actually been using next.
    """
    color_count = collections.defaultdict(int)  # type: DefaultDict[str, int]
    for marker in markers:
        color = marker[:2]
        color_count[color] += 1
    augmented = []
    for marker in markers:
        color = marker[:2]
        count = color_count[color]
        augmented.append((count, marker))
    augmented.sort()
    return [marker for unused, marker in augmented]


class PickMarker(Gtk.Dialog):

    """Dialog to pick a legion marker."""

    def __init__(
        self,
        playername: str,
        game_name: str,
        markers_left: List[str],
        def1: defer.Deferred,
        parent: Gtk.Window,
    ):
        title = f"PickMarker - {playername}"
        GObject.GObject.__init__(self, title=title, parent=parent)
        self.playername = playername
        self.game_name = game_name
        self.deferred = def1
        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)

        previous_color = ""
        hbox = None
        for ii, button_name in enumerate(sorted_markers(markers_left)):
            button = Gtk.Button()
            button.tag = button_name
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(
                fileutils.basedir(f"images/legion/{button_name}.png")
            )
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            button.add(image)
            button.connect("button-press-event", self.cb_click)
            if button_name[:2] != previous_color:
                previous_color = button_name[:2]
                hbox = Gtk.HBox()
                self.vbox.add(hbox)
            if hbox is not None:
                hbox.add(button)

        self.connect("destroy", self.cb_destroy)
        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Gdk.EventButton) -> None:
        markerid = widget.tag
        self.deferred.callback((self.game_name, self.playername, markerid))
        self.destroy()

    def cb_destroy(self, widget: Gtk.Widget) -> None:
        if not self.deferred.called:
            self.deferred.callback((self.game_name, self.playername, None))


if __name__ == "__main__":

    def my_callback(tup: Tuple[str, str, str]) -> None:
        (game_name, playername, markerid) = tup
        logging.info(f"picked {markerid}")
        reactor.stop()  # type: ignore

    playername = "test user"
    game_name = "test game"
    markers_left = [f"Rd{ii:02d}" for ii in range(1, 12 + 1)] + [
        f"Bu{ii:02d}" for ii in range(1, 8 + 1)
    ]
    pickmarker, def1 = new(playername, game_name, markers_left, None)
    def1.addCallback(my_callback)
    reactor.run()  # type: ignore[attr-defined]
