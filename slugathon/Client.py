"""Outward-facing facade for client side."""

try:
    set
except NameError:
    from sets import Set as set
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


class Client(pb.Referenceable, Observed):

    zope.interface.implements(IObserver)

    def __init__(self, username, password, host='localhost', 
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
            self.attach(self.anteroom)
            def1 = user.callRemote("get_usernames")
            def1.addCallbacks(self.got_usernames, self.failure)
            return defer.succeed(user)
        else:
            return defer.failure(user)

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        self.usernames.clear()
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
        raise KeyError("No game named %s found" % game_name)

    def add_game(self, game_info_tuple):
        (name, create_time, start_time, min_players, max_players,
          playernames) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players)
        self.attach(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        self.games.append(game)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
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

    # TODO Game should observe Client directly.
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
        
        self.notify(action)

