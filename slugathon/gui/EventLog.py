#!/usr/bin/env python

__copyright__ = "Copyright (c) 2010-2011 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from zope.interface import implements

from slugathon.game import Action, Legion
from slugathon.gui import icon
from slugathon.util import prefs
from slugathon.util.Observer import IObserver


class EventLog(gtk.Window):
    """Graphical log of game events."""

    implements(IObserver)

    def __init__(self, game, username, parent):
        gtk.Window.__init__(self)
        self.game = game
        self.username = username
        self.last_action = None
        self.reveal_actions = set()

        self.scrolledwindow = gtk.ScrolledWindow()
        self.vadjustment = self.scrolledwindow.get_vadjustment()
        self.add(self.scrolledwindow)
        self.vbox = gtk.VBox()
        self.scrolledwindow.add_with_viewport(self.vbox)

        self.connect("configure-event", self.cb_configure_event)

        if self.username:
            tup = prefs.load_window_position(self.username,
              self.__class__.__name__)
            if tup:
                x, y = tup
                self.move(x, y)
            tup = prefs.load_window_size(self.username,
              self.__class__.__name__)
            if tup:
                width, height = tup
                self.resize(width, height)

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Event Log - %s" % self.username)
        self.show_all()

    def cb_configure_event(self, event, unused):
        if self.username:
            x, y = self.get_position()
            prefs.save_window_position(self.username, self.__class__.__name__,
              x, y)
            width, height = self.get_size()
            prefs.save_window_size(self.username, self.__class__.__name__,
              width, height)
        return False

    def update(self, observed, action):
        st = None
        if action == self.last_action or action in self.reveal_actions:
            pass
        elif isinstance(action, Action.AssignTower):
            st = "%s gets tower %d" % (action.playername,
              action.tower_num)
        elif isinstance(action, Action.PickedColor):
            st = "%s gets color %s" % (action.playername,
              action.color)
        elif isinstance(action, Action.StartSplitPhase):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = "%s (%s) turn %d" % (action.playername,
              playercolor, action.turn)
        elif isinstance(action, Action.SplitLegion):
            st = "%s (%s) (%d) splits off %s (%s) (%d)" % (
              action.parent_markerid,
              Legion.find_picname(action.parent_markerid),
              len(action.parent_creature_names),
              action.child_markerid,
              Legion.find_picname(action.child_markerid),
              len(action.child_creature_names))
        elif isinstance(action, Action.UndoSplit):
            st = "%s (%s) (%d) undoes split" % (
              action.parent_markerid,
              Legion.find_picname(action.parent_markerid),
              len(action.parent_creature_names) +
              len(action.child_creature_names))
        elif isinstance(action, Action.MergeLegions):
            st = "%s (%s) (%d) merges with splitoff" % (
              action.parent_markerid,
              Legion.find_picname(action.parent_markerid),
              len(action.parent_creature_names) +
              len(action.child_creature_names))
        elif isinstance(action, Action.RollMovement):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = "%s (%s) rolls %d for movement" % (action.playername,
              playercolor, action.movement_roll)
        elif isinstance(action, Action.MoveLegion):
            st = "%s (%s) %s to %s hex %s" % (action.markerid,
              Legion.find_picname(action.markerid),
              "teleports" if action.teleport else "moves",
              self.game.board.hexes[action.hexlabel].terrain,
              action.hexlabel)
        elif isinstance(action, Action.UndoMoveLegion):
            st = "%s (%s) undoes move" % (action.markerid,
              Legion.find_picname(action.markerid))
        elif isinstance(action, Action.RevealLegion):
            self.reveal_actions.add(action)
            st = "%s (%s) is revealed as %s" % (action.markerid,
              Legion.find_picname(action.markerid),
              ", ".join(action.creature_names))
        elif isinstance(action, Action.Flee):
            st = "%s (%s) in %s hex %s flees" % (action.markerid,
              Legion.find_picname(action.markerid),
              self.game.board.hexes[action.hexlabel].terrain,
              action.hexlabel)
        elif isinstance(action, Action.Concede):
            st = "%s (%s) in %s hex %s concedes" % (action.markerid,
              Legion.find_picname(action.markerid),
              self.game.board.hexes[action.hexlabel].terrain,
              action.hexlabel)
        elif isinstance(action, Action.SummonAngel):
            st = "%s (%s) summons %s from %s" % (action.markerid,
              Legion.find_picname(action.markerid),
              action.creature_name, action.donor_markerid)
        elif isinstance(action, Action.RecruitCreature):
            st = "%s (%s) recruits %s with %s" % (action.markerid,
              Legion.find_picname(action.markerid),
              action.creature_name, ", ".join(action.recruiter_names))
        elif isinstance(action, Action.UndoRecruit):
            st = "%s (%s) undoes recruit" % (action.markerid,
              Legion.find_picname(action.markerid))
        elif isinstance(action, Action.Fight):
            st = "%s (%s) fights %s (%s) in %s hex %s" % (
              action.attacker_markerid,
              Legion.find_picname(action.attacker_markerid),
              action.defender_markerid,
              Legion.find_picname(action.defender_markerid),
              self.game.board.hexes[action.hexlabel].terrain,
              action.hexlabel)
        elif isinstance(action, Action.StartReinforceBattlePhase):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = "%s (%s) starts battle turn %d" % (action.playername,
              playercolor, action.battle_turn)
        elif isinstance(action, Action.MoveCreature):
            playercolor = self.game.get_player_by_name(action.playername).color
            st = "%s (%s) moves %s in %s hex %s to %s hex %s" % (
              action.playername, playercolor, action.creature_name,
              self.game.battlemap.hexes[action.old_hexlabel].terrain,
              action.old_hexlabel,
              self.game.battlemap.hexes[action.new_hexlabel].terrain,
              action.new_hexlabel)
        elif isinstance(action, Action.UndoMoveCreature):
            st = "%s in %s hex %s undoes move" % (action.creature_name,
              self.game.battlemap.hexes[action.new_hexlabel].terrain,
              action.new_hexlabel)
        elif isinstance(action, Action.Strike):
            if action.carries:
                st = "%s in %s strikes %s in %s for %d %s and %s %s" % (
                  action.striker_name, action.striker_hexlabel,
                  action.target_name, action.target_hexlabel,
                  action.hits,
                  "hit" if action.hits == 1 else "hits",
                  action.carries,
                  "carry" if action.carries == 1 else "carries")
            else:
                st = "%s in %s strikes %s in %s for %d %s" % (
                  action.striker_name, action.striker_hexlabel,
                  action.target_name, action.target_hexlabel, action.hits,
                  "hit" if action.hits == 1 else "hits")
        elif isinstance(action, Action.Carry):
            st = "%d %s to %s in %s, leaving %d %s" % (
              action.carries,
              "hit carries" if action.carries == 1 else "hits carry",
              action.carry_target_name,
              action.carry_target_hexlabel, action.carries_left,
              "carry" if action.carries == 1 else "carries")
        elif isinstance(action, Action.DriftDamage):
            st = "%s in %s suffers drift damage" % (
              action.target_name, action.target_hexlabel)
        elif isinstance(action, Action.BattleOver):
            if action.winner_survivors:
                st = "%s (%s) defeats %s (%s) in %s" % (
                  action.winner_markerid,
                  Legion.find_picname(action.winner_markerid),
                  action.loser_markerid,
                  Legion.find_picname(action.loser_markerid),
                  action.hexlabel)
            else:
                st = "%s (%s) and %s (%s) mutual in %s" % (
                  action.winner_markerid,
                  Legion.find_picname(action.winner_markerid),
                  action.loser_markerid,
                  Legion.find_picname(action.loser_markerid),
                  action.hexlabel)
        elif isinstance(action, Action.Acquire):
            st = "%s (%s) acquires %s" % (action.markerid,
              Legion.find_picname(action.markerid),
              ", ".join(action.angel_names))
        elif isinstance(action, Action.GameOver):
            if len(action.winner_names) == 1:
                st = "%s wins!" % action.winner_names[0]
            else:
                st = "%s draw" % " and ".join(action.winner_names)
        self.last_action = action
        if st:
            label = gtk.Label(st)
            # left-align the label
            label.set_alignment(0.0, 0.5)
            self.vbox.pack_start(label, expand=False, fill=False)
            label.show()
            upper = self.vadjustment.get_upper()
            self.vadjustment.set_value(upper)


if __name__ == "__main__":
    parent = gtk.Window()
    event_log = EventLog(None, None, parent)
    gtk.main()
