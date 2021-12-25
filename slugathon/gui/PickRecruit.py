#!/usr/bin/env python3

from __future__ import annotations

import logging
from typing import Any, List, Optional, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk
from twisted.internet import defer

from slugathon.game import Caretaker, Creature, Legion
from slugathon.gui import Chit, Marker, icon


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


def new(
    playername: str,
    legion: Legion.Legion,
    mterrain: str,
    caretaker: Caretaker.Caretaker,
    parent: Optional[Gtk.Window],
) -> Tuple[PickRecruit, defer.Deferred]:
    """Create a PickRecruit dialog and return it and a Deferred."""
    logging.info(f"new {playername} {legion} {mterrain}")
    def1 = defer.Deferred()  # type: defer.Deferred
    pickrecruit = PickRecruit(
        playername, legion, mterrain, caretaker, def1, parent
    )
    return pickrecruit, def1


class PickRecruit(Gtk.Dialog):

    """Dialog to pick a recruit."""

    def __init__(
        self,
        playername: str,
        legion: Legion.Legion,
        mterrain: str,
        caretaker: Caretaker.Caretaker,
        def1: defer.Deferred,
        parent: Optional[Gtk.Window],
    ):
        GObject.GObject.__init__(
            self, title=f"PickRecruit - {playername}", parent=parent
        )
        self.legion = legion
        player = legion.player
        assert player is not None
        self.deferred = def1

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.vbox.set_spacing(9)

        self.chit_to_recruit = {}
        self.chit_to_recruiter_names = {}

        legion_name = Gtk.Label(
            label=f"Pick recruit for legion {legion.markerid} "
            f"({legion.picname}) "
            f"in hex {legion.hexlabel}"
        )
        self.vbox.pack_start(legion_name, True, True, 0)

        legion_hbox = Gtk.HBox(spacing=15)
        self.vbox.pack_start(legion_hbox, True, True, 0)

        marker_hbox = Gtk.HBox()
        legion_hbox.pack_start(marker_hbox, False, True, 0)

        chits_hbox = Gtk.HBox(spacing=3)
        legion_hbox.pack_start(chits_hbox, False, True, 0)

        marker = Marker.Marker(legion, True, scale=20)
        marker_hbox.pack_start(marker.event_box, False, False, 0)

        assert player.color is not None
        for creature in legion.sorted_living_creatures:
            chit = Chit.Chit(creature, player.color, scale=20)
            chits_hbox.pack_start(chit.event_box, False, True, 0)

        recruit_tups = legion.available_recruits_and_recruiters(
            mterrain, caretaker
        )
        max_len = max(len(tup) for tup in recruit_tups)
        for tup in recruit_tups:
            hbox = Gtk.HBox()
            self.vbox.pack_start(hbox, True, True, 0)
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
                self.chit_to_recruit[chit] = recruit
                self.chit_to_recruiter_names[chit] = recruiter_names
                if ii < len(li) - 2:
                    hbox.pack_start(chit.event_box, False, True, 0)
                elif ii == len(li) - 2:
                    hbox.pack_start(chit.event_box, True, True, 0)
                else:
                    hbox.pack_end(chit.event_box, False, True, 0)
                chit.connect("button-press-event", self.cb_click)
            label = Gtk.Label(label=caretaker.num_left(creature.name))
            hbox.pack_end(label, False, True, 0)

        self.add_button("gtk-cancel", Gtk.ResponseType.CANCEL)
        self.connect("response", self.cb_cancel)
        self.show_all()

    def cb_click(self, widget: Gtk.Widget, event: Any) -> None:
        """Chose a recruit."""
        eventbox = widget
        chit = eventbox.chit
        self.deferred.callback(
            (
                self.legion,
                self.chit_to_recruit[chit],
                self.chit_to_recruiter_names[chit],
            )
        )
        self.destroy()

    def cb_cancel(self, widget: Gtk.Widget, response_id: int) -> None:
        """The cancel button was pressed, so exit"""
        self.deferred.callback((self.legion, None, None))
        self.destroy()


if __name__ == "__main__":
    import time
    from slugathon.game import Player, Game
    from slugathon.util import guiutils

    creature_names = ["Titan", "Dragon", "Dragon", "Minotaur", "Minotaur"]
    creatures = Creature.n2c(creature_names)

    def my_callback(
        tup: Tuple[Legion.Legion, Creature.Creature, List[str]]
    ) -> None:
        (legion, creature, recruiter_names) = tup
        logging.info(f"{legion} recruited {creature} {recruiter_names}")
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

    Gtk.main()
