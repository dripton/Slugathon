"""Just a place to load the icon image."""

__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.util import fileutils


pixbuf = gtk.gdk.pixbuf_new_from_file(fileutils.basedir(
  os.path.join("images", "creature", "Serpent.png")))
