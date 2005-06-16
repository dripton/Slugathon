#!/usr/bin/env python

import sys
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk

import guiutils
import icon

class About(object):
    def __init__(self):
        ad = self.ad = gtk.AboutDialog()
        ad.set_name("Slugathon")
        ad.set_version("")
        ad.set_copyright("Copyright 2003-2005 David Ripton")
        ad.set_comments("""Very very prerelease""")

        license_fn = "../docs/gpl.txt"
        fil = open(license_fn)
        st = fil.read()
        fil.close()
        ad.set_license(st)

        ad.set_authors(["David Ripton",])
        ad.set_logo(icon.pixbuf)
        ad.set_website("http://slugathon.sf.net")
        ad.show()
        self.ad = ad


if __name__ == "__main__":
    about = About()
    about.ad.connect("destroy", guiutils.die)
    about.ad.connect("response", guiutils.die)
    gtk.main()
