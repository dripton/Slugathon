#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"

import gtk

from slugathon.util import guiutils

class InfoDialog(object):
    def __init__(self, title, message, parent):
        self.dialog = gtk.Dialog(title, parent,
          buttons=((gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)))
        label = gtk.Label(message)
        self.dialog.vbox.pack_start(label)
        self.dialog.connect("response", self.cb_response)
        self.dialog.show_all()

    def cb_response(self, widget, response_id):
        self.dialog.destroy()


if __name__ == "__main__":
    info_dialog = InfoDialog("Info", "Look out behind you!", None)
    info_dialog.dialog.connect("destroy", guiutils.exit)
    gtk.main()
