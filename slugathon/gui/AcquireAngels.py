#!/usr/bin/env python3

__copyright__ = "Copyright (c) 2007-2021 David Ripton"
__license__ = "GNU GPL v2"


import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject
from twisted.internet import defer

from slugathon.gui import Chit, Marker, icon
from slugathon.game import Creature


def new(playername, legion, num_archangels, num_angels, caretaker, parent):
    """Create an AcquireAngels dialog and return it and a Deferred."""
    def1 = defer.Deferred()
    acquire_angel = AcquireAngels(
        playername, legion, num_archangels, num_angels, caretaker, def1, parent
    )
    return acquire_angel, def1


def find_angel_combos(
    num_archangels, num_angels, archangels_left, angels_left
):
    """Return a list of tuples of Creatures, corresponding to each
    possible group of angels and archangels."""
    set1 = set()
    for archangels in range(min(num_archangels, archangels_left) + 1):
        for angels in range(
            min((num_angels + num_archangels), angels_left) + 1
        ):
            if 0 < archangels + angels <= num_archangels + num_angels:
                lst = []
                for unused in range(archangels):
                    lst.append(Creature.Creature("Archangel"))
                for unused in range(angels):
                    lst.append(Creature.Creature("Angel"))
                combo = tuple(lst)
                set1.add(combo)
    sorter = []
    for combo in set1:
        score = sum((creature.score for creature in combo))
        sorter.append((score, combo))
    sorter.sort(reverse=True)
    combos = [combo for (unused, combo) in sorter]
    return combos


class AcquireAngels(Gtk.Dialog):

    """Dialog to acquire an angel."""

    def __init__(
        self,
        playername,
        legion,
        num_archangels,
        num_angels,
        caretaker,
        def1,
        parent,
    ):
        GObject.GObject.__init__(
            self, title=f"AcquireAngels - {playername}", parent=parent
        )
        self.deferred = def1
        self.legion = legion
        player = legion.player

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        legion_name = Gtk.Label(
            label=f"Acquire angel for legion {legion.markerid} "
            f"({legion.picname}) in hex {legion.hexlabel}"
        )
        self.vbox.pack_start(legion_name, True, True, 0)

        legion_hbox = Gtk.HBox(spacing=3)
        self.vbox.pack_start(legion_hbox, True, True, 0)

        marker_hbox = Gtk.HBox()
        legion_hbox.pack_start(marker_hbox, False, True, 0)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, False, True, 0)

        chits_hbox = Gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox, True, True, 0)

        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, False, True, 0)

        angel_combos = find_angel_combos(
            num_archangels,
            num_angels,
            caretaker.num_left("Archangel"),
            caretaker.num_left("Angel"),
        )
        max_len = max(len(combo) for combo in angel_combos)
        leading_spaces = (len(legion) + 2 - max_len) // 2
        for combo in angel_combos:
            hbox = Gtk.HBox(spacing=3, homogeneous=False)
            self.vbox.pack_start(hbox, True, True, 0)
            for unused in range(leading_spaces):
                chit = Chit.Chit(None, player.color, scale=20, name="Nothing")
                chit.combo = combo
                hbox.pack_start(chit.event_box, False, True, 0)
                chit.connect("button-press-event", self.cb_click)
            for angel in combo:
                chit = Chit.Chit(angel, player.color, scale=20)
                chit.combo = combo
                hbox.pack_start(chit.event_box, False, True, 0)
                chit.connect("button-press-event", self.cb_click)

        self.add_button("gtk-cancel", Gtk.ResponseType.CANCEL)
        self.connect("response", self.cb_cancel)

        self.show_all()

    def cb_click(self, widget, event):
        """Acquire an angel."""
        eventbox = widget
        chit = eventbox.chit
        self.deferred.callback((self.legion, chit.combo))
        self.destroy()

    def cb_cancel(self, widget, response_id):
        self.deferred.callback((self.legion, None))
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Legion, Player, Game
    from slugathon.util import guiutils

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def my_callback(tup):
        (legion, creature) = tup
        logging.info(f"{legion} acquired {creature}")
        guiutils.exit()

    now = time.time()
    playername = "p0"
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player(playername, game, 0)
    player.color = "Red"
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    legion.hexlabel = 1000
    window = Gtk.Window()
    acquire_angel, def1 = new(playername, legion, 1, 1, game.caretaker, window)
    acquire_angel.connect("destroy", guiutils.exit)
    def1.addCallback(my_callback)

    Gtk.main()
