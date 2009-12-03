#!/usr/bin/env python

__copyright__ = "Copyright (c) 2004-2009 David Ripton"
__license__ = "GNU GPL v2"


import time

import gtk
from twisted.internet import reactor
from zope.interface import implements

from slugathon.util.Observer import IObserver
from slugathon.game import Action
from slugathon.gui import icon
from slugathon.util import guiutils


def format_time(secs):
    tup = time.localtime(secs)
    return time.strftime("%H:%M:%S", tup)


class WaitingForPlayers(object):
    """Waiting for players to start game dialog."""

    implements(IObserver)

    def __init__(self, user, username, game):
        self.user = user
        self.username = username
        self.game = game
        self.game.add_observer(self)
        self.builder = gtk.Builder()
        self.builder.add_from_file(guiutils.basedir("ui/waitingforplayers.ui"))
        self.widget_names = ["waiting_for_players_window", "game_name_label",
          "player_list", "created_entry", "starts_by_entry", "countdown_entry",
          "join_button", "drop_button", "start_button"]
        for widget_name in self.widget_names:
            setattr(self, widget_name, self.builder.get_object(widget_name))
        self.player_store = gtk.ListStore(str)
        self.update_player_store()

        self.waiting_for_players_window.set_icon(icon.pixbuf)
        self.waiting_for_players_window.set_title("%s - %s" % (
          self.waiting_for_players_window.get_title(), self.username))

        self.waiting_for_players_window.connect("destroy", self.cb_destroy)
        self.join_button.connect("button-press-event", self.cb_click_join)
        self.drop_button.connect("button-press-event", self.cb_click_drop)
        self.start_button.connect("button-press-event", self.cb_click_start)
        self.start_button.set_sensitive(self.username ==
          self.game.get_owner().name)
        # TODO Start button should automatically be triggered when max
        # players have joined, or min players have joined and time is up.
        self.game_name_label.set_text(game.name)
        self.created_entry.set_text(format_time(game.create_time))
        self.starts_by_entry.set_text(format_time(game.start_time))
        self.update_countdown()
        self.player_list.set_model(self.player_store)
        selection = self.player_list.get_selection()
        selection.set_select_function(self.cb_player_list_select, None)
        column = gtk.TreeViewColumn("Player Name", gtk.CellRendererText(),
          text=0)
        self.player_list.append_column(column)

    def cb_click_join(self, widget, event):
        def1 = self.user.callRemote("join_game", self.game.name)
        def1.addErrback(self.failure)

    def cb_destroy(self, unused):
        if self.game:
            def1 = self.user.callRemote("drop_from_game", self.game.name)
            def1.addErrback(self.failure)

    def cb_click_drop(self, widget, event):
        def1 = self.user.callRemote("drop_from_game", self.game.name)
        def1.addErrback(self.failure)
        self.destroy()

    def cb_click_start(self, widget, event):
        def1 = self.user.callRemote("start_game", self.game.name)
        def1.addErrback(self.failure)

    # TODO Save the selection and do something useful with it.
    def cb_player_list_select(self, path, unused):
        index = path[0]
        self.player_store[index, 0]
        return False

    def update_countdown(self):
        diff = int(self.game.start_time - time.time())
        label = str(max(diff, 0))
        self.countdown_entry.set_text(label)
        if diff > 0:
            reactor.callLater(1, self.update_countdown)

    # XXX cleanup
    def update_player_store(self):
        playernames = self.game.get_playernames()
        leng = len(self.player_store)
        for ii, playername in enumerate(playernames):
            if ii < leng:
                self.player_store[ii, 0] = (playername,)
            else:
                self.player_store.append((playername,))
        leng = len(self.game.get_playernames())
        while len(self.player_store) > leng:
            del self.player_store[leng]
        self.start_button.set_sensitive(self.username ==
          self.game.get_owner().name)

    def destroy(self):
        self.waiting_for_players_window.destroy()

    def failure(self, arg):
        print "WaitingForPlayers.failure", arg

    def shutdown(self):
        self.game.remove_observer(self)
        self.destroy()

    def update(self, observed, action):
        if isinstance(action, Action.RemoveGame):
            if action.game_name == self.game.name:
                self.shutdown()
        elif isinstance(action, Action.JoinGame):
            self.update_player_store()
        elif isinstance(action, Action.DropFromGame):
            self.update_player_store()
        elif isinstance(action, Action.AssignTower):
            if action.game_name == self.game.name:
                self.shutdown()

if __name__ == "__main__":
    from twisted.internet import defer
    from slugathon.game import Game

    class NullUser(object):
        def callRemote(*args):
            return defer.Deferred()

    now = time.time()
    user = NullUser()
    username = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    wfp = WaitingForPlayers(user, username, game)

    gtk.main()
