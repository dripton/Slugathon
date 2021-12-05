#!/usr/bin/env python3


import gi

gi.require_version("Gtk", "3.0")
from twisted.internet import gtk3reactor

try:
    gtk3reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
from gi.repository import Gtk, GObject
from zope.interface import implementer

from slugathon.game import Action, Legion
from slugathon.util.Observer import IObserver


__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class EventLog(Gtk.EventBox):

    """Graphical log of game events."""

    def __init__(self, game, playername):
        GObject.GObject.__init__(self)
        self.game = game
        self.playername = playername
        self.last_st = ""

        self.vbox2 = Gtk.VBox()

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.vadjustment = self.scrolledwindow.get_vadjustment()
        self.add(self.scrolledwindow)
        self.scrolledwindow.add_with_viewport(self.vbox2)
        self.show_all()

    def update(self, observed, action, names):
        st = None
        if isinstance(action, Action.AssignTower):
            st = f"{action.playername} gets tower {action.tower_num}"
        elif isinstance(action, Action.PickedColor):
            st = f"{action.playername} gets color {action.color}"
        elif isinstance(action, Action.StartSplitPhase):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = f"{action.playername} ({playercolor}) turn {action.turn}"
        elif isinstance(action, Action.SplitLegion):
            st = (
                f"{action.parent_markerid} "
                f"({Legion.find_picname(action.parent_markerid)}) "
                f"({len(action.parent_creature_names)}) splits off "
                f"{action.child_markerid} "
                f"({Legion.find_picname(action.child_markerid)}) "
                f"({len(action.child_creature_names)})"
            )
        elif isinstance(action, Action.UndoSplit):
            length = len(action.parent_creature_names) + len(
                action.child_creature_names
            )
            st = (
                f"{action.parent_markerid} "
                f"({Legion.find_picname(action.parent_markerid)}) "
                f"({length}) "
                f"undoes split"
            )
        elif isinstance(action, Action.MergeLegions):
            length = len(action.parent_creature_names) + len(
                action.child_creature_names
            )
            st = (
                f"{action.parent_markerid} "
                f"({Legion.find_picname(action.parent_markerid)}) "
                f"({length}) "
                f"merges with splitoff"
            )
        elif isinstance(action, Action.RollMovement):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = (
                f"{action.playername} ({playercolor}) rolls "
                f"{action.movement_roll} for movement"
            )
        elif isinstance(action, Action.MoveLegion):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"{'teleports' if action.teleport else 'moves'} "
                f"from "
                f"{self.game.board.hexes[action.previous_hexlabel].terrain} "
                f"hex {action.previous_hexlabel} "
                f"to {self.game.board.hexes[action.hexlabel].terrain} "
                f"hex {action.hexlabel}"
            )
        elif isinstance(action, Action.UndoMoveLegion):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"undoes move"
            )
        elif isinstance(action, Action.RevealLegion):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"is revealed as {', '.join(action.creature_names)}"
            )
        elif isinstance(action, Action.Flee):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"in {self.game.board.hexes[action.hexlabel].terrain} "
                f"hex {action.hexlabel} flees"
            )
        elif isinstance(action, Action.Concede):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"in {self.game.board.hexes[action.hexlabel].terrain} "
                f"hex {action.hexlabel} concedes"
            )
        elif isinstance(action, Action.SummonAngel):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"summons "
                f"{action.creature_name} "
                f"from {action.donor_markerid} "
                f"({Legion.find_picname(action.donor_markerid)})"
            )
        elif isinstance(action, Action.RecruitCreature):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"recruits "
                f"{action.creature_name} "
                f"with {', '.join(action.recruiter_names)}"
            )
        elif isinstance(action, Action.UndoRecruit):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"undoes recruit"
            )
        elif isinstance(action, Action.Fight):
            st = (
                f"{action.attacker_markerid} "
                f"({Legion.find_picname(action.attacker_markerid)}) "
                f"fights {action.defender_markerid} "
                f"({Legion.find_picname(action.defender_markerid)}) "
                f"in {self.game.board.hexes[action.hexlabel].terrain} "
                f"hex {action.hexlabel}"
            )
        elif isinstance(action, Action.StartReinforceBattlePhase):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = (
                f"{action.playername} "
                f"({playercolor}) "
                f"starts battle turn {action.battle_turn}"
            )
        elif isinstance(action, Action.MoveCreature):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = (
                f"{action.playername} "
                f"({playercolor}) "
                f"moves {action.creature_name} "
                f"in {self.game.battlemap.hexes[action.old_hexlabel].terrain} "
                f"hex {action.old_hexlabel} "
                f"to {self.game.battlemap.hexes[action.new_hexlabel].terrain} "
                f"hex {action.new_hexlabel}"
            )
        elif isinstance(action, Action.UndoMoveCreature):
            st = (
                f"{action.creature_name} "
                f"in {self.game.battlemap.hexes[action.new_hexlabel].terrain} "
                f"hex {action.new_hexlabel} undoes move"
            )
        elif isinstance(action, Action.Strike):
            if action.carries:
                st = (
                    f"{action.striker_name} "
                    f"in {action.striker_hexlabel} "
                    f"strikes {action.target_name} "
                    f"in {action.target_hexlabel} "
                    f"for {action.hits} "
                    f"{'hit' if action.hits == 1 else 'hits'} "
                    f"and {action.carries} "
                    f"{'carry' if action.carries == 1 else 'carries'}"
                )
            else:
                st = (
                    f"{action.striker_name} "
                    f"in {action.striker_hexlabel} "
                    f"strikes {action.target_name} "
                    f"in {action.target_hexlabel} "
                    f"for {action.hits} "
                    f"{'hit' if action.hits == 1 else 'hits'}"
                )
        elif isinstance(action, Action.Carry):
            st = (
                f"{action.carries} "
                f"{'hit carries' if action.carries == 1 else 'hits carry'} "
                f"to {action.carry_target_name} "
                f"in {action.carry_target_hexlabel} , leaving "
                f"{action.carries_left} "
                f"{'carry' if action.carries == 1 else 'carries'}"
            )
        elif isinstance(action, Action.DriftDamage):
            st = (
                f"{action.target_name} in {action.target_hexlabel} "
                f"suffers drift damage"
            )
        elif isinstance(action, Action.BattleOver):
            if action.winner_survivors:
                st = (
                    f"{action.winner_markerid} "
                    f"({Legion.find_picname(action.winner_markerid)}) "
                    f"defeats {action.loser_markerid} "
                    f"({Legion.find_picname(action.loser_markerid)}) "
                    f"in {action.hexlabel}"
                )
            else:
                st = (
                    f"{action.winner_markerid} "
                    f"({Legion.find_picname(action.winner_markerid)}) "
                    f"and {action.loser_markerid} "
                    f"({Legion.find_picname(action.loser_markerid)}) "
                    f"mutual in {action.hexlabel}"
                )
        elif isinstance(action, Action.AcquireAngels):
            st = (
                f"{action.markerid} "
                f"({Legion.find_picname(action.markerid)}) "
                f"acquires {', '.join(action.angel_names)}"
            )
        elif isinstance(action, Action.GameOver):
            if len(action.winner_names) == 1:
                st = f"{action.winner_names[0]} wins!"
            else:
                st = f"{' and '.join(action.winner_names)} draw"
        if st and st != self.last_st:
            self.last_st = st
            label = Gtk.Label(label=st)
            # left-align the label
            label.set_alignment(0.0, 0.5)
            self.vbox2.pack_start(label, False, False, 0)
            label.show()
            upper = self.vadjustment.get_upper()
            self.vadjustment.set_value(upper)


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils

    parent = Gtk.Window()
    event_log = EventLog(None, None)
    event_log.connect("destroy", guiutils.exit)
    parent.add(event_log)
    parent.show_all()
    action = Action.GameOver("a", ["Bob"], time.time())
    reactor.callWhenRunning(event_log.update, None, action, None)  # type: ignore[attr-defined]
    reactor.run()  # type: ignore[attr-defined]
