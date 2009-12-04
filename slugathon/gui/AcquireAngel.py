#!/usr/bin/env python

__copyright__ = "Copyright (c) 2007-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from twisted.internet import defer

from slugathon.gui import Chit, Marker, icon
from slugathon.game import Creature
from slugathon.util import guiutils


def new(username, legion, available_angels, parent):
    """Create an AcquireAngel dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    acquire_angel = AcquireAngel(username, legion, available_angels, def1,
      parent)
    return acquire_angel, def1


class AcquireAngel(gtk.Dialog):
    """Dialog to acquire an angel."""
    def __init__(self, username, legion, available_angels, def1, parent):
        gtk.Dialog.__init__(self, "AcquireAngel - %s" % username, parent)
        self.deferred = def1
        self.legion = legion
        player = legion.player

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label("Acquire angel for legion %s in hex %s" % (
          legion.markername, legion.hexlabel))
        self.vbox.pack_start(legion_name)

        legion_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox)

        marker_hbox = gtk.HBox()
        legion_hbox.pack_start(marker_hbox, expand=False)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, expand=False)

        chits_hbox = gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox, expand=True)

        for creature in legion.sorted_creatures:
            # XXX This is the wrong place to do this.
            if not creature.dead:
                creature.heal()
                chit = Chit.Chit(creature, player.color, scale=20)
                chits_hbox.pack_start(chit.event_box, expand=False)

        angels_hbox = gtk.HBox(spacing=15, homogeneous=True)
        self.vbox.pack_start(angels_hbox)

        angels = Creature.n2c(available_angels)
        for angel in angels:
            chit = Chit.Chit(angel, player.color, scale=20)
            angels_hbox.pack_start(chit.event_box, expand=False)
            chit.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()


    def cb_click(self, widget, event):
        """Acquire an angel."""
        eventbox = widget
        chit = eventbox.chit
        self.deferred.callback((self.legion, chit.creature))
        self.destroy()

    def cb_cancel(self, widget, response_id):
        self.destroy()

if __name__ == "__main__":
    import time
    from slugathon.game import Legion, Player, Game

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def my_callback((legion, creature)):
        print legion, "acquired", creature
        guiutils.exit()

    now = time.time()
    username = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(username, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    available_angels = ["Archangel", "Angel"]
    acquire_angel, def1 = new(username, legion, available_angels, None)
    acquire_angel.connect("destroy", guiutils.exit)
    def1.addCallback(my_callback)

    gtk.main()
