#!/usr/bin/env python

"""Help/About dialog, wrapped around gtk.AboutDialog"""

__copyright__ = "Copyright (c) 2005-2008 David Ripton"
__license__ = "GNU GPL v2"

import gtk

import guiutils
import icon

class About(object):
    def __init__(self):
        ad = self.ad = gtk.AboutDialog()
        ad.set_icon(icon.pixbuf)
        ad.set_position(gtk.WIN_POS_MOUSE)
        ad.set_name("Slugathon")
        ad.set_version("")
        ad.set_copyright("Copyright 2003-2008 David Ripton")
        ad.set_comments("""Very very prerelease""")

        license_fn = "../docs/COPYING.txt"
        fil = open(license_fn)
        st = fil.read()
        fil.close()
        ad.set_license(st)

        ad.set_authors(["David Ripton",])
        ad.set_artists(["Chris Byler", "Keith Carter", "Chris Howe",
          "Klint Hull", "David Lum", "John Lum", "Agustin Martin",
          "Tchula Ripton", "Jerry Reiger", "Josh Smith",
          "Sakis Spyropoulos", "D. U. Thibault",])

        ad.set_logo(icon.pixbuf)
        ad.set_website("http://slugathon.sf.net")
        ad.show()
        self.ad = ad


if __name__ == "__main__":
    about = About()
    about.ad.connect("response", guiutils.exit)
    gtk.main()
