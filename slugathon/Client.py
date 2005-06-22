"""Outward-facing facade for client side."""

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor, defer
import zope.interface

import Server
import Anteroom
from Observer import IObserver
from Observed import Observed
import Action
import Game
import PickColor
import PickMarker
import BoardRoot
import GUIMasterBoard


class Client(pb.Referenceable, Observed):

    zope.interface.implements(IObserver)

    def __init__(self, username, password, host="localhost", 
          port=Server.DEFAULT_PORT):
        Observed.__init__(self)
        self.username = username
        self.playername = username # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.factory = pb.PBClientFactory()
        self.user = None
        self.anteroom = None
        self.usernames = set()
        self.games = []
        self.guiboards = {}   # Maps game to guiboard
        print "Called Client init:", self

    def remote_set_name(self, name):
        print "remote_set_name(", name, ") called on", self
        self.playername = name
        return name

    def remote_ping(self, arg):
        print "remote_ping(", arg, ") called on", self
        return True

    def __str__(self):
        return "Client " + str(self.username)

    def connect(self):
        print "Client.connect", self
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallbacks(self.connected, self.failure)
        return def1

    def connected(self, user):
        print "Client.connected", self, user
        if user:
            self.user = user
            self.anteroom = Anteroom.Anteroom(user, self.username)
            self.add_observer(self.anteroom)
            def1 = user.callRemote("get_usernames")
            def1.addCallbacks(self.got_usernames, self.failure)
            return defer.succeed(user)
        else:
            return defer.failure(user)

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        self.usernames.clear()
        for username in usernames:
            self.usernames.add(username)
        self.anteroom.set_usernames(self.usernames)
        def1 = self.user.callRemote("get_games")
        def1.addCallbacks(self.got_games, self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        self.anteroom.set_games(self.games)

    def name_to_game(self, game_name):
        for g in self.games:
            if g.name == game_name:
                return g
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
        reactor.stop()

    # TODO Make this an Action, after adding a filter on Observed.notify
    def remote_receive_chat_message(self, text):
        self.anteroom.receive_chat_message(text)

    def remote_update(self, action):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        print "Client.remote_update", self, observed, action
        self.update(observed, action)

    def _maybe_pick_color(self, game):
        if game.next_playername_to_pick_color() == self.username:
            PickColor.PickColor(self.user, self.username, 
              game.name, game.colors_left())

    def _maybe_pick_first_marker(self, game, playername):
        if playername == self.username:
            player = game.get_player_by_name(playername)
            markernames = list(player.markernames.copy())
            markernames.sort()
            PickMarker.PickMarker(self, self.username, game.name, markernames)

    def pick_marker(self, game_name, username, markername):
        """Callback from PickMarker."""
        print "Client.pick_marker", self, game_name, username, markername
        game = self.name_to_game(game_name)
        player = game.get_player_by_name(username)
        player.pick_marker(markername)
        # XXX Need a more explicit way to note that it's the first time?
        if len(player.legions) == 0:
            def1 = self.user.callRemote("pick_first_marker", game_name, 
              markername)
            def1.addErrback(self.failure)

    def _init_guiboard(self, game):
        print "Client._init_guiboard"
        boardroot = BoardRoot.BoardRoot(self.username)
        self.guiboards[game] = GUIMasterBoard.GUIMasterBoard(boardroot,
          game.board, game, self.username)
        self.add_observer(self.guiboards[game])

    def update(self, observed, action):
        """Updates from User will come via remote_update, with
        observed set to None."""
        print "Client.update", self, observed, action

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
            if not self.guiboards.get(game):
                self._init_guiboard(game)

        self.notify(action)

