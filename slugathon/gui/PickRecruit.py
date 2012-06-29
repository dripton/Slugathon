#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


import logging

import gtk
from twisted.internet import defer

from slugathon.gui import Chit, Marker, icon
from slugathon.game import Creature


def new(playername, legion, mterrain, caretaker, parent):
    """Create a PickRecruit dialog and return it and a Deferred."""
    logging.info("new %s %s %s", playername, legion, mterrain)
    def1 = defer.Deferred()
    pickrecruit = PickRecruit(playername, legion, mterrain, caretaker, def1,
      parent)
    return pickrecruit, def1


class PickRecruit(gtk.Dialog):
    """Dialog to pick a recruit."""
    def __init__(self, playername, legion, mterrain, caretaker, def1, parent):
        gtk.Dialog.__init__(self, "PickRecruit - %s" % playername, parent)
        self.legion = legion
        player = legion.player
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label("Pick recruit for legion %s (%s) in hex %s" % (
          legion.markerid, legion.picname, legion.hexlabel))
        self.vbox.pack_start(legion_name)

        legion_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox)

        marker_hbox = gtk.HBox()
        legion_hbox.pack_start(marker_hbox, expand=False)

        chits_hbox = gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox, expand=False)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, expand=False,
          fill=False)

        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, expand=False)

        recruit_tups = legion.available_recruits_and_recruiters(mterrain,
          caretaker)
        max_len = max(len(tup) for tup in recruit_tups)
        for tup in recruit_tups:
            hbox = gtk.HBox()
            self.vbox.pack_start(hbox)
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
                    hbox.pack_start(chit.event_box, expand=False)
                elif ii == len(li) - 2:
                    hbox.pack_start(chit.event_box, expand=True)
                else:
                    hbox.pack_end(chit.event_box, expand=False)
                chit.connect("button-press-event", self.cb_click)
            label = gtk.Label(caretaker.num_left(creature.name))
            hbox.pack_end(label, expand=False)

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.connect("response", self.cb_cancel)
        self.show_all()

    def cb_click(self, widget, event):
        """Chose a recruit."""
        eventbox = widget
        chit = eventbox.chit
        self.deferred.callback((self.legion, chit.recruit,
          chit.recruiter_names))
        self.destroy()

    def cb_cancel(self, widget, response_id):
        """The cancel button was pressed, so exit"""
        self.deferred.callback((self.legion, None, None))
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Legion, Player, Game
    from slugathon.util import guiutils

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def my_callback((legion, creature, recruiter_names)):
        logging.info("%s recruited %s %s", legion, creature, recruiter_names)
        guiutils.exit()

    now = time.time()
    playername = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    masterhex = game.board.hexes[legion.hexlabel]
    mterrain = masterhex.terrain
    pickrecruit, def1 = new(playername, legion, mterrain, game.caretaker, None)
    def1.addCallback(my_callback)
    pickrecruit.connect("destroy", guiutils.exit)

    gtk.main()
