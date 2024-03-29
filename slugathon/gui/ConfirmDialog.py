#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()  # type: ignore
except AssertionError:
    pass
from twisted.internet import defer, reactor

from slugathon.gui import icon


__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    parent: Gtk.Window, title: str, message: str
) -> Tuple[ConfirmDialog, defer.Deferred]:
    def1 = defer.Deferred()  # type: defer.Deferred
    confirm_dialog = ConfirmDialog(parent, title, message, def1)
    return confirm_dialog, def1


class ConfirmDialog(Gtk.MessageDialog):
    """Yes / No confirmation dialog.

    The deferred fires True on Yes, False on No.
    """

    def __init__(
        self,
        parent: Gtk.Window,
        title: str,
        message: str,
        def1: defer.Deferred,
    ):
        Gtk.MessageDialog.__init__(
            self, parent=parent, buttons=Gtk.ButtonsType.YES_NO
        )
        self.deferred = def1
        self.set_title(title)
        self.set_markup(message)
        self.set_icon(icon.pixbuf)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.connect("response", self.cb_response)
        self.show_all()

    def cb_response(self, widget: Gtk.Widget, response_id: int) -> None:
        retval = response_id == Gtk.ResponseType.YES
        self.deferred.callback(retval)
        self.destroy()


if __name__ == "__main__":
    window = Gtk.Window()
    confirm_dialog, def1 = new(
        parent=window, title="Info", message="Are we having fun yet?"
    )

    def print_arg(arg: Any) -> None:
        print(arg)
        reactor.stop()  # type: ignore

    def1.addCallback(print_arg)
    def1.addErrback(print_arg)
    reactor.run()  # type: ignore[attr-defined]
