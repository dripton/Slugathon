#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

from slugathon.util import guiutils


class InfoDialog(gtk.Dialog):
    def __init__(self, title, message, parent):
        gtk.Dialog.__init__(self, title, parent,
          buttons=((gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)))
        label = gtk.Label(message)
        self.vbox.pack_start(label)
        self.connect("response", self.cb_response)
        self.show_all()

    def cb_response(self, widget, response_id):
        self.destroy()


if __name__ == "__main__":
    info_dialog = InfoDialog("Info", "Look out behind you!", None)
    info_dialog.connect("destroy", guiutils.exit)
    gtk.main()
