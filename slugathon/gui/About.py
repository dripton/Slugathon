#!/usr/bin/env python3


import os
import logging
from typing import Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk

from slugathon.gui import icon
from slugathon.util import fileutils, guiutils


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Help/About dialog, wrapped around Gtk.AboutDialog"""


class About(Gtk.AboutDialog):
    def __init__(self, parent: Gtk.Window):
        GObject.GObject.__init__(self)
        self.set_icon(icon.pixbuf)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_name("Slugathon")
        self.set_copyright("Copyright (c) 2003-2021 David Ripton")

        license_fn = fileutils.basedir(os.path.join("docs", "COPYING.txt"))
        with open(license_fn) as fil:
            st = fil.read()
        self.set_license(st)
        self.set_wrap_license(False)

        version_fn = fileutils.basedir(os.path.join("docs", "version.txt"))
        try:
            with open(version_fn) as fil:
                version = fil.read().strip()
        except IOError:
            version = "unknown"
        self.set_version(version)

        self.set_authors(
            [
                "David Ripton",
            ]
        )
        self.set_artists(
            [
                "Chris Byler",
                "Keith Carter",
                "Chris Howe",
                "Klint Hull",
                "David Lum",
                "John Lum",
                "Agustin Martin",
                "Tchula Ripton",
                "Jerry Reiger",
                "Josh Smith",
                "Sakis Spyropoulos",
                "D. U. Thibault",
            ]
        )

        self.set_logo(icon.pixbuf)
        self.set_website("http://github.com/dripton/Slugathon")
        self.connect("response", self.cb_response)
        self.show()

    def cb_response(self, widget: Gtk.Widget, event: Any) -> None:
        logging.debug(f"{event=}")
        self.destroy()


if __name__ == "__main__":
    about = About(None)
    about.connect("destroy", guiutils.exit)
    Gtk.main()
