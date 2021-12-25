import os

from gi.repository import GdkPixbuf

from slugathon.util import fileutils

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Just a place to load the icon image."""

pixbuf = GdkPixbuf.Pixbuf.new_from_file(
    fileutils.basedir(os.path.join("images", "creature", "Serpent.png"))
)
