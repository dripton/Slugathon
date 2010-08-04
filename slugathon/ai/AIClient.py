#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"

"""Outward-facing facade for AI."""


import random
from optparse import OptionParser

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor
from zope.interface import implements

from slugathon.net import config
from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed
from slugathon.game import Action, Game


class Client(pb.Referenceable, Observed):

    implements(IObserver)

    def __init__(self, username, password, host="localhost",
      port=config.DEFAULT_PORT):
        Observed.__init__(self)
        self.username = username
        self.playername = username # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.factory = pb.PBClientFactory()
        self.factory.unsafeTracebacks = True
        self.user = None
        self.anteroom = None
        self.usernames = set()
        self.games = []
        self.guiboards = {}   # Maps game to guiboard
        self.status_screens = {}   # Maps game to status_screen

    def remote_set_name(self, name):
        self.playername = name
        return name

    def remote_ping(self, arg):
        return True

    def __repr__(self):
        return "Client " + str(self.username)

    def connect(self):
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def connected(self, user):
        print "connected"
        if user:
            self.user = user
            def1 = user.callRemote("get_usernames")
            def1.addCallback(self.got_usernames)
            def1.addErrback(self.failure)

    def connection_failed(self, arg):
        print "connection failed"

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        print "got usernames", usernames
        self.usernames.clear()
        for username in usernames:
            self.usernames.add(username)
        def1 = self.user.callRemote("get_games")
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        print "got games", game_info_tuples
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def add_game(self, game_info_tuple):
        (name, create_time, start_time, min_players, max_players,
          playernames) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players)
        self.add_observer(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        self.games.append(game)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    def failure(self, error):
        print "Client.failure", self, error

    def remote_receive_chat_message(self, text):
        pass

    def remote_update(self, action):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action)

    def _maybe_pick_color(self, game):
        if game.next_playername_to_pick_color() == self.username:
            color = random.choice(game.colors_left())
            self._cb_pickcolor(game, color)

    def _cb_pickcolor(self, (game, color)):
        """Callback for PickColor"""
        if color is None:
            self._maybe_pick_color(game)
        else:
            def1 = self.user.callRemote("pick_color", game.name, color)
            def1.addErrback(self.failure)

    def _maybe_pick_first_marker(self, game, playername):
        if playername == self.username:
            player = game.get_player_by_name(playername)
            markername = random.choice(player.markernames)
            self.pick_marker((game.name, self.username, markername))

    def pick_marker(self, (game_name, username, markername)):
        """Callback from PickMarker."""
        game = self.name_to_game(game_name)
        player = game.get_player_by_name(username)
        if markername is None:
            if not player.legions:
                self._maybe_pick_first_marker(game, username)
        else:
            player.pick_marker(markername)
            if not player.legions:
                def1 = self.user.callRemote("pick_first_marker", game_name,
                  markername)
                def1.addErrback(self.failure)

    def update(self, observed, action):
        """Updates from User will come via remote_update, with
        observed set to None."""
        if isinstance(action, Action.AddUsername):
            self.usernames.add(action.username)
        elif isinstance(action, Action.DelUsername):
            self.usernames.remove(action.username)
        elif isinstance(action, Action.FormGame):
            game_info_tuple = (action.game_name, action.create_time,
              action.start_time, action.min_players, action.max_players,
              [action.username])
            self.add_game(game_info_tuple)
        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)
        elif isinstance(action, Action.AssignedAllTowers):
            game = self.name_to_game(action.game_name)
            self._maybe_pick_color(game)
        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            game.assign_color(action.playername, action.color)
            self._maybe_pick_color(game)
            self._maybe_pick_first_marker(game, action.playername)
        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                print "Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names))
            else:
                print "Game %s over, draw" % action.game_name

        self.notify(action)


def main():
    op = OptionParser()
    op.add_option("-n", "--playername", action="store", type="str")
    op.add_option("-a", "--password", action="store", type="str")
    op.add_option("-s", "--server", action="store", type="str",
      default="localhost")
    op.add_option("-p", "--port", action="store", type="int",
      default=config.DEFAULT_PORT)
    opts, args = op.parse_args()
    if args:
        op.error("got illegal argument")
    client = Client(opts.playername, opts.password, opts.server, opts.port)
    client.connect()
    reactor.run()

if __name__ == "__main__":
    main()
