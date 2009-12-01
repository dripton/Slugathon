#!/usr/bin/env python

"""Help/About dialog, wrapped around gtk.AboutDialog"""

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import icon
from slugathon.util import guiutils


class About(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        self.set_icon(icon.pixbuf)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_name("Slugathon")
        self.set_copyright("Copyright (c) 2003-2009 David Ripton")

        license_fn = guiutils.basedir("docs/COPYING.txt")
        with open(license_fn) as fil:
            st = fil.read()
        self.set_license(st)

        version_fn = guiutils.basedir("docs/version.txt")
        try:
            with open(version_fn) as fil:
                version = fil.read().strip()
        except IOError:
            version = "unknown"
        self.set_version(version)

        self.set_authors(["David Ripton",])
        self.set_artists(["Chris Byler", "Keith Carter", "Chris Howe",
          "Klint Hull", "David Lum", "John Lum", "Agustin Martin",
          "Tchula Ripton", "Jerry Reiger", "Josh Smith",
          "Sakis Spyropoulos", "D. U. Thibault",])

        self.set_logo(icon.pixbuf)
        self.set_website("http://github.com/dripton/Slugathon")
        self.show()


if __name__ == "__main__":
    about = About()
    about.connect("response", guiutils.exit)
    gtk.main()
