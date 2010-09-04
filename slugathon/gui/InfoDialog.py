#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009-2010 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.gui import icon


class InfoDialog(gtk.MessageDialog):
    def __init__(self, parent, title, message_format):
        gtk.MessageDialog.__init__(self, parent=parent,
          flags=gtk.DIALOG_DESTROY_WITH_PARENT,
          buttons=gtk.BUTTONS_OK, message_format=message_format)
        self.set_title(title)
        self.set_icon(icon.pixbuf)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.connect("response", self.cb_response)
        self.show_all()

    def cb_response(self, widget, response_id):
        self.destroy()


if __name__ == "__main__":
    from slugathon.util import guiutils

    info_dialog = InfoDialog(parent=None, title="Info",
      message_format="Look out behind you!")
    info_dialog.connect("destroy", guiutils.exit)
    gtk.main()
