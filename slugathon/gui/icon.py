"""Just a place to load the icon image."""

__copyright__ = "Copyright (c) 2005-2008 David Ripton"
__license__ = "GNU GPL v2"

import os

import gtk

from slugathon.util import guiutils

pixbuf = gtk.gdk.pixbuf_new_from_file(guiutils.basedir(
  "images/creature/Serpent.png"))
