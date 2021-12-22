#!/usr/bin/env python3


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

from slugathon.gui import icon


__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"


class InfoDialog(Gtk.MessageDialog):
    def __init__(self, parent: Gtk.Window, title: str, message: str):
        GObject.GObject.__init__(
            self, parent=parent, buttons=Gtk.ButtonsType.OK
        )
        self.set_title(title)
        self.set_markup(message)
        self.set_icon(icon.pixbuf)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.connect("response", self.cb_response)
        self.show_all()

    def cb_response(self, widget: Gtk.Widget, response_id: int) -> None:
        self.destroy()


if __name__ == "__main__":
    from slugathon.util import guiutils

    info_dialog = InfoDialog(
        parent=None, title="Info", message="Look out behind you!"
    )
    info_dialog.connect("destroy", guiutils.exit)
    Gtk.main()
