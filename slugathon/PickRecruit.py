#!/usr/bin/env python 

import time

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import Chit
import Marker
import Creature
import Legion
import Player
import icon
import guiutils
import Game


class PickRecruit(object):
    """Dialog to pick a recruit."""
    def __init__(self, username, player, legion, masterhex, caretaker, 
      callback):
        print "PickRecruit.__init__", username, player, legion
        self.callback = callback
        self.glade = gtk.glade.XML("../glade/pickrecruit.glade")
        self.widgets = ["pick_recruit_dialog", "marker_hbox", 
          "chits_hbox", "recruits_hbox", "legion_name"]
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self.pick_recruit_dialog.set_icon(icon.pixbuf)
        self.pick_recruit_dialog.set_title("PickRecruit - %s" % (username))

        self.legion_name.set_text("Pick recruit for legion %s in hex %s" % (
          legion.markername, legion.hexlabel))

        self.player = player
        self.legion = legion
        self.masterhex = masterhex
        self.recruit = None

        self.marker = Marker.Marker(legion, scale=20)
        self.marker_hbox.pack_start(self.marker.image, expand=False,
          fill=False)
        self.marker.show()

        for creature in legion.creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chit.show()
            self.chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)

        recruit_names = legion.available_recruits(masterhex, caretaker)
        recruits = Creature.n2c(recruit_names)
        for recruit in recruits:
            chit = Chit.Chit(recruit, player.color, scale=20)
            chit.show()
            self.recruits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button_press_event", self.cb_click)

        self.okbutton = self.pick_recruit_dialog.action_area.get_children()[0]
        self.okbutton.set_sensitive(False)

        self.pick_recruit_dialog.connect("response", self.cb_response)
        self.pick_recruit_dialog.show()


    def cb_click(self, widget, event):
        """Chose a recruit."""
        eventbox = widget
        if eventbox in self.recruits_hbox.get_children():
            chit = eventbox.chit
            self.recruit = chit.creature
            self.okbutton.set_sensitive(True)
        else:
            self.recruit = None
            self.okbutton.set_sensitive(False)

    def cb_response(self, widget, response_id):
        """Send the recruit to the callback function."""
        print "PickRecruit.cb_response", widget, response_id, self.recruit
        self.pick_recruit_dialog.destroy()
        self.callback(self.legion, self.recruit)


if __name__ == "__main__":
    creaturenames = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creaturenames)
   
    now = time.time()
    username = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, "g1", 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    masterhex = game.board.hexes[legion.hexlabel]
    pickrecruit = PickRecruit(username, player, legion, masterhex, 
      game.caretaker, guiutils.die)
    pickrecruit.pick_recruit_dialog.connect("destroy", guiutils.die)

    gtk.main()
