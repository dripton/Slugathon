#!/usr/bin/env python2.3

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, AttributeError:
    pass
import gtk
from gtk import glade
import sys


class NewGame:
    """Form new game dialog."""
    def __init__(self, user):
        self.user = user
        self.glade = glade.XML('../glade/newgame.glade')
        self.widgets = ['newgameDialog', 'nameEntry', 'minplayersSpin', 
          'maxplayersSpin']
        for widgetName in self.widgets:
            setattr(self, widgetName, self.glade.get_widget(widgetName))
        
    def cb_ok(self): 
        print "ok"
        self.user.callRemote("formgame", name min_players, max_players)
        dismiss()

    def cb_cancel(self): 
        print "cancel"
        dismiss()
