#!/usr/bin/env python

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import defer
import gtk

from slugathon.gui import Chit, Marker, icon
from slugathon.game import Legion


def new(playername, legion, parent):
    """Create a SplitLegion dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    splitlegion = SplitLegion(playername, legion, def1, parent)
    return splitlegion, def1


class SplitLegion(gtk.Dialog):
    """Dialog to split a legion."""
    def __init__(self, playername, legion, def1, parent):
        gtk.Dialog.__init__(self, "SplitLegion - %s" % playername, parent)
        self.old_legion = legion
        player = legion.player
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = gtk.Label("Splitting legion %s (%s) in hex %s" % (
          legion.markerid, legion.picname, legion.hexlabel))
        self.vbox.pack_start(legion_name)

        old_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(old_hbox)
        old_marker_hbox = gtk.HBox()
        old_hbox.pack_start(old_marker_hbox, expand=False)
        self.old_chits_hbox = gtk.HBox()
        old_hbox.pack_start(self.old_chits_hbox, expand=True)

        new_hbox = gtk.HBox(spacing=15)
        self.vbox.pack_start(new_hbox)
        new_marker_hbox = gtk.HBox()
        new_hbox.pack_start(new_marker_hbox, expand=False)
        self.new_chits_hbox = gtk.HBox()
        new_hbox.pack_start(self.new_chits_hbox, expand=True)

        old_marker = Marker.Marker(legion, False, scale=20)
        old_marker_hbox.pack_start(old_marker.event_box, expand=False)

        self.new_legion1 = Legion.Legion(player, legion.markerid,
          legion.sorted_creatures, legion.hexlabel)
        self.new_legion2 = Legion.Legion(player, player.selected_markerid,
          [], legion.hexlabel)
        self.new_marker = Marker.Marker(self.new_legion2, False, scale=20)
        new_marker_hbox.pack_start(self.new_marker.event_box, expand=False)

        for creature in legion.sorted_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            self.old_chits_hbox.pack_start(chit.event_box, expand=False,
              fill=False)
            chit.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", gtk.RESPONSE_CANCEL)
        self.ok_button = self.add_button("gtk-ok", gtk.RESPONSE_OK)
        self.ok_button.set_sensitive(False)
        self.connect("response", self.cb_response)

        self.show_all()

    def cb_click(self, widget, event):
        """Move the clicked-on Chit's EventBox to the other hbox."""
        eventbox = widget
        if eventbox in self.old_chits_hbox.get_children():
            prev = self.old_chits_hbox
            next = self.new_chits_hbox
            previous_legion = self.new_legion1
            next_legion = self.new_legion2
        else:
            prev = self.new_chits_hbox
            next = self.old_chits_hbox
            previous_legion = self.new_legion2
            next_legion = self.new_legion1
        prev.remove(eventbox)
        next.pack_start(eventbox, expand=False, fill=False)
        chit = eventbox.chit
        previous_legion.creatures.remove(chit.creature)
        next_legion.creatures.append(chit.creature)
        legal = self.old_legion.is_legal_split(self.new_legion1,
          self.new_legion2)
        self.ok_button.set_sensitive(legal)

    def cb_response(self, widget, response_id):
        self.destroy()
        if response_id == gtk.RESPONSE_OK:
            self.deferred.callback((self.old_legion, self.new_legion1,
              self.new_legion2))
        else:
            self.deferred.callback((None, None, None))


if __name__ == "__main__":
    import time
    from slugathon.data import creaturedata
    from slugathon.game import Creature, Player, Game
    from slugathon.util import guiutils

    now = time.time()
    creatures = [Creature.Creature(name) for name in
      creaturedata.starting_creature_names]
    playername = "test"
    game = Game.Game("g1", playername, now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    player.selected_markerid = "Rd02"
    splitlegion, def1 = new(playername, legion, None)
    def1.addCallback(guiutils.exit)
    splitlegion.connect("destroy", guiutils.exit)

    gtk.main()
