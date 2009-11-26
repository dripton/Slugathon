#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk

import Chit
import Marker
import icon
import Creature


class PickRecruit(object):
    """Dialog to pick a recruit."""
    def __init__(self, username, player, legion, mterrain, caretaker,
      callback, parent):
        self.callback = callback
        self.builder = gtk.Builder()
        self.builder.add_from_file("../ui/pickrecruit.ui")
        self.widget_names = ["pick_recruit_dialog", "marker_hbox",
          "chits_hbox", "vbox1", "legion_name"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))

        self.pick_recruit_dialog.set_icon(icon.pixbuf)
        self.pick_recruit_dialog.set_title("PickRecruit - %s" % (username))
        self.pick_recruit_dialog.set_transient_for(parent)

        self.legion_name.set_text("Pick recruit for legion %s in hex %s" % (
          legion.markername, legion.hexlabel))

        self.player = player
        self.legion = legion

        self.marker = Marker.Marker(legion, True, scale=20)
        self.marker_hbox.pack_start(self.marker.event_box, expand=False,
          fill=False)
        self.marker.show()

        for creature in legion.sorted_creatures:
            if not creature.dead:
                chit = Chit.Chit(creature, player.color, scale=20)
                chit.show()
                self.chits_hbox.pack_start(chit.event_box, expand=False,
                  fill=False)

        recruit_tups = legion.available_recruits_and_recruiters(mterrain,
          caretaker)
        max_len = max(len(tup) for tup in recruit_tups)
        for tup in recruit_tups:
            hbox = gtk.HBox()
            self.vbox1.pack_start(hbox)
            recruit_name = tup[0]
            recruit = Creature.Creature(recruit_name)
            recruiter_names = tup[1:]
            li = list(tup)
            li.reverse()
            while len(li) < max_len:
                li.insert(-1, "Nothing")
            li.insert(-1, "RightArrow")
            for ii, name in enumerate(li):
                if name in ["RightArrow", "Nothing"]:
                    chit = Chit.Chit(None, player.color, scale=20, name=name)
                else:
                    creature = Creature.Creature(name)
                    chit = Chit.Chit(creature, player.color, scale=20)
                chit.recruit = recruit
                chit.recruiter_names = recruiter_names
                if ii < len(li) - 2:
                    hbox.pack_start(chit.event_box, expand=False, fill=False)
                elif ii == len(li) - 2:
                    hbox.pack_start(chit.event_box, expand=True, fill=False)
                else:
                    hbox.pack_end(chit.event_box, expand=False, fill=False)
                chit.show()
                chit.connect("button-press-event", self.cb_click)
            hbox.show()

        self.pick_recruit_dialog.connect("response", self.cb_response)
        self.pick_recruit_dialog.show()


    def cb_click(self, widget, event):
        """Chose a recruit."""
        eventbox = widget
        chit = eventbox.chit
        self.callback(self.legion, chit.recruit, chit.recruiter_names)
        self.pick_recruit_dialog.destroy()

    def cb_response(self, dialog, response_id):
        """The cancel button was pressed, so exit"""
        self.pick_recruit_dialog.destroy()


if __name__ == "__main__":
    import time
    import Legion
    import Player
    import guiutils
    import Game

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def callback(legion, creature, recruiter_names):
        print legion, "recruited", creature, recruiter_names
        guiutils.exit()

    now = time.time()
    username = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    masterhex = game.board.hexes[legion.hexlabel]
    mterrain = masterhex.terrain
    pickrecruit = PickRecruit(username, player, legion, mterrain,
      game.caretaker, callback, None)
    pickrecruit.pick_recruit_dialog.connect("destroy", guiutils.exit)

    gtk.main()
