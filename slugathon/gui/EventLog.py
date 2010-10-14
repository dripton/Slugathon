#!/usr/bin/env python

__copyright__ = "Copyright (c) 2010 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from zope.interface import implements

from slugathon.game import Action
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
        label = None
        if action == self.last_action:
            pass
        elif isinstance(action, Action.SplitLegion):
            st = "%s splits into %s (%d) and %s (%d)" % (
              action.parent_markername, action.parent_markername,
              len(action.parent_creature_names),
              action.child_markername, len(action.child_creature_names))
            label = gtk.Label(st)
        elif isinstance(action, Action.RollMovement):
            st = "%s rolls %d for movement" % (action.playername,
              action.movement_roll)
            label = gtk.Label(st)
        elif isinstance(action, Action.MoveLegion):
            st = "%s %s to %s" % (action.markername,
              "teleports" if action.teleport else "moves", action.hexlabel)
            label = gtk.Label(st)
        elif isinstance(action, Action.Flee):
            st = "%s in %s flees" % (action.markername, action.hexlabel)
            label = gtk.Label(st)
        elif isinstance(action, Action.Concede):
            st = "%s in %s concedes" % (action.markername, action.hexlabel)
            label = gtk.Label(st)
        elif isinstance(action, Action.SummonAngel):
            st = "%s summons %s from %s" % (action.markername,
              action.creature_name, action.donor_markername)
            label = gtk.Label(st)
        elif isinstance(action, Action.RecruitCreature):
            st = "%s recruits %s with %s" % (action.markername,
              action.creature_name, ", ".join(action.recruiter_names))
            label = gtk.Label(st)
        elif isinstance(action, Action.Strike):
            st = "%s in %s strikes %s in %s for %d hits and %s carries" % (
              action.striker_name, action.striker_hexlabel,
              action.target_name, action.target_hexlabel,
              action.hits, action.carries)
            label = gtk.Label(st)
        elif isinstance(action, Action.Carry):
            st = "%d hits carry to %s in %s, leaving %d carries" % (
              action.carries, action.carry_target_name,
              action.carry_target_hexlabel, action.carries_left)
            label = gtk.Label(st)
        elif isinstance(action, Action.DriftDamage):
            st = "%s in %s suffers drift damage" % (
              action.target_name, action.target_hexlabel)
            label = gtk.Label(st)
        elif isinstance(action, Action.BattleOver):
            if action.winner_survivors:
                st = "%s defeats %s in %s" % (action.winner_markername,
                  action.loser_markername, action.hexlabel)
            else:
                st = "%s and %s mutual in %s" % (action.winner_markername,
                  action.loser_markername, action.hexlabel)
            label = gtk.Label(st)
        elif isinstance(action, Action.Acquire):
            st = "%s acquires %s" % (action.markername,
              ", ".join(action.angel_names))
            label = gtk.Label(st)
        elif isinstance(action, Action.GameOver):
            if len(action.winner_names) == 1:
                st = "%s wins!"
            else:
                st = "%s draw" % " and ".join(action.winner_names)
            label = gtk.Label(st)
        self.last_action = action
        if label:
            self.vbox.pack_start(label, expand=False, fill=False)
            label.show()
            upper = self.vadjustment.get_upper()
            self.vadjustment.set_value(upper)


if __name__ == "__main__":
    parent = gtk.Window()
    event_log = EventLog(None, None, parent)
    gtk.main()
