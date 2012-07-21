#!/usr/bin/env python

__copyright__ = "Copyright (c) 2004-2012 David Ripton"
__license__ = "GNU GPL v2"


import time

from twisted.internet import gtk2reactor
try:
    gtk2reactor.install()
except AssertionError:
    pass
from twisted.internet import reactor
from twisted.python import log
import gtk
from zope.interface import implementer

from slugathon.util.Observer import IObserver
from slugathon.game import Action
from slugathon.gui import icon
from slugathon.util.NullUser import NullUser


def format_time(secs):
    tup = time.localtime(secs)
    return time.strftime("%H:%M:%S", tup)


@implementer(IObserver)
class WaitingForPlayers(gtk.Dialog):
    """Waiting for players to start game dialog."""
    def __init__(self, user, playername, game, parent):
        gtk.Dialog.__init__(self, "Waiting for Players - %s" % playername,
          parent)
        self.user = user
        self.playername = playername
        self.game = game
        self.game.add_observer(self)
        self.started = False

        self.set_icon(icon.pixbuf)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Waiting for Players - %s" % self.playername)
        self.set_default_size(-1, 300)

        label1 = gtk.Label(game.name)
        self.vbox.pack_start(label1, expand=False)

        scrolled_window1 = gtk.ScrolledWindow()
        scrolled_window1.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.vbox.pack_start(scrolled_window1)

        self.player_list = gtk.TreeView()
        scrolled_window1.add(self.player_list)

        hbox1 = gtk.HBox()
        self.vbox.pack_start(hbox1, expand=False)

        vbox2 = gtk.VBox()
        hbox1.pack_start(vbox2)
        label2 = gtk.Label("Created at")
        vbox2.pack_start(label2, expand=False)
        scrolled_window2 = gtk.ScrolledWindow()
        scrolled_window2.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        vbox2.pack_start(scrolled_window2)
        viewport1 = gtk.Viewport()
        scrolled_window2.add(viewport1)
        created_entry = gtk.Entry(max=8)
        created_entry.set_editable(False)
        created_entry.set_text(format_time(game.create_time))
        viewport1.add(created_entry)

        vbox3 = gtk.VBox()
        hbox1.pack_start(vbox3)
        label3 = gtk.Label("Starts by")
        vbox3.pack_start(label3, expand=False)
        scrolled_window3 = gtk.ScrolledWindow()
        scrolled_window3.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        vbox3.pack_start(scrolled_window3)
        viewport2 = gtk.Viewport()
        scrolled_window3.add(viewport2)
        starts_by_entry = gtk.Entry(max=8)
        starts_by_entry.set_editable(False)
        starts_by_entry.set_text(format_time(game.start_time))
        viewport2.add(starts_by_entry)

        vbox4 = gtk.VBox()
        hbox1.pack_start(vbox4)
        label4 = gtk.Label("Time Left")
        vbox4.pack_start(label4, expand=False)
        scrolled_window4 = gtk.ScrolledWindow()
        scrolled_window4.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        vbox4.pack_start(scrolled_window4)
        viewport3 = gtk.Viewport()
        scrolled_window4.add(viewport3)
        self.countdown_entry = gtk.Entry(max=8)
        self.countdown_entry.set_editable(False)
        viewport3.add(self.countdown_entry)

        join_button = gtk.Button("Join Game")
        self.vbox.pack_start(join_button, expand=False)
        join_button.connect("button-press-event", self.cb_click_join)

        drop_button = gtk.Button("Drop out of Game")
        self.vbox.pack_start(drop_button, expand=False)
        drop_button.connect("button-press-event", self.cb_click_drop)

        self.start_button = gtk.Button("Start Game Now")
        self.vbox.pack_start(self.start_button, expand=False)
        self.start_button.connect("button-press-event", self.cb_click_start)
        self.start_button.set_sensitive(self.playername ==
          self.game.owner.name)

        self.connect("destroy", self.cb_destroy)

        self.player_store = gtk.ListStore(str, int)
        self.update_player_store()

        self.update_countdown()
        self.player_list.set_model(self.player_store)
        selection = self.player_list.get_selection()
        selection.set_select_function(self.cb_player_list_select, None)
        headers = ["Player Name", "Skill"]
        for (ii, title) in enumerate(headers):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(),
              text=ii)
            self.player_list.append_column(column)

        self.show_all()

    def cb_click_join(self, widget, event):
        def1 = self.user.callRemote("join_game", self.game.name, "Human", "")
        def1.addErrback(self.failure)

    def cb_destroy(self, unused):
        if self.game and not self.game.started:
            def1 = self.user.callRemote("withdraw", self.game.name)
            def1.addErrback(self.failure)

    def cb_click_drop(self, widget, event):
        def1 = self.user.callRemote("withdraw", self.game.name)
        def1.addErrback(self.failure)
        self.destroy()

    def cb_click_start(self, widget, event):
        self.start_game()

    def start_game(self):
        if not self.started:
            self.started = True
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
            if self.game.num_players >= self.game.max_players:
                self.start_game()
            else:
                reactor.callLater(1, self.update_countdown)
        else:
            if self.game.num_players >= self.game.min_players:
                self.start_game()

    def update_player_store(self):
        def1 = self.user.callRemote("get_player_data")
        def1.addCallback(self._got_player_data)
        def1.addErrback(self.failure)

    def _got_player_data(self, player_data):
        playername_to_data = {}
        if player_data:
            for dct in player_data:
                playername_to_data[dct["name"]] = dct
        length = len(self.player_store)
        for ii, playername in enumerate(self.game.playernames):
            dct = playername_to_data.get(playername)
            if dct:
                skill = dct["skill"]
            else:
                # TODO unhardcode
                skill = 1
            if ii < length:
                self.player_store[(ii, 0)] = (playername, skill)
            else:
                self.player_store.append((playername, skill))
        length = len(self.game.playernames)
        while len(self.player_store) > length:
            del self.player_store[length]
        self.start_button.set_sensitive(self.playername ==
          self.game.owner.name)

    def failure(self, arg):
        log.err(arg)

    def shutdown(self):
        self.game.remove_observer(self)
        self.destroy()

    def update(self, observed, action, names):
        if isinstance(action, Action.RemoveGame):
            if action.game_name == self.game.name:
                self.shutdown()
        elif isinstance(action, Action.JoinGame):
            self.update_player_store()
        elif isinstance(action, Action.Withdraw):
            self.update_player_store()
        elif isinstance(action, Action.AssignTower):
            if action.game_name == self.game.name:
                self.shutdown()

if __name__ == "__main__":
    from slugathon.game import Game

    now = time.time()
    user = NullUser()
    playername = "Player 1"
    game = Game.Game("g1", "Player 1", now, now, 2, 6)
    wfp = WaitingForPlayers(user, playername, game, None)
    wfp.connect("destroy", lambda x: reactor.stop())
    reactor.run()
