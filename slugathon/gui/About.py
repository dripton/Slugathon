#!/usr/bin/env python

"""Help/About dialog, wrapped around gtk.AboutDialog"""

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.gui import icon
from slugathon.util import guiutils


class About(object):
    def __init__(self):
        ad = self.ad = gtk.AboutDialog()
        ad.set_icon(icon.pixbuf)
        ad.set_position(gtk.WIN_POS_MOUSE)
        ad.set_name("Slugathon")
        ad.set_copyright("Copyright (c) 2003-2009 David Ripton")

        license_fn = guiutils.basedir("docs/COPYING.txt")
        with open(license_fn) as fil:
            st = fil.read()
        ad.set_license(st)

        version_fn = guiutils.basedir("docs/version.txt")
        try:
            with open(version_fn) as fil:
                version = fil.read().strip()
        except IOError:
            version = "unknown"
        ad.set_version(version)

        ad.set_authors(["David Ripton",])
        ad.set_artists(["Chris Byler", "Keith Carter", "Chris Howe",
          "Klint Hull", "David Lum", "John Lum", "Agustin Martin",
          "Tchula Ripton", "Jerry Reiger", "Josh Smith",
          "Sakis Spyropoulos", "D. U. Thibault",])

        ad.set_logo(icon.pixbuf)
        ad.set_website("http://github.com/dripton/Slugathon")
        ad.show()
        self.ad = ad


if __name__ == "__main__":
    about = About()
    about.ad.connect("response", guiutils.exit)
    gtk.main()
