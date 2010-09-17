__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"

"""Outward-facing facade for client side."""


from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor
from zope.interface import implements

from slugathon.net import config
from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed
from slugathon.game import Action, Game
from slugathon.gui import Anteroom, PickColor, PickMarker, GUIMasterBoard
from slugathon.util.log import log


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
        self.pickcolor = None

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
        # No errback here; let Connect's errback handle failed login.
        return def1

    def connected(self, user):
        if user:
            self.user = user
            def1 = user.callRemote("get_usernames")
            def1.addCallback(self.got_usernames)
            def1.addErrback(self.failure)

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        self.usernames.clear()
        for username in usernames:
            self.usernames.add(username)
        def1 = self.user.callRemote("get_games")
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        self.anteroom = Anteroom.Anteroom(self.user, self.username,
          self.usernames, self.games)
        self.add_observer(self.anteroom)

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
        log("failure", self, error)

    # TODO Make this an Action, after adding a filter on Observed.notify
    def remote_receive_chat_message(self, text):
        self.anteroom.receive_chat_message(text)

    def remote_update(self, action):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action)

    def _maybe_pick_color(self, game):
        if (game.next_playername_to_pick_color == self.username and
          self.pickcolor is None):
            self.pickcolor, def1 = PickColor.new(self.username, game,
              game.colors_left, self.guiboards[game])
            def1.addCallback(self._cb_pickcolor)

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
            markernames = sorted(player.markernames.copy())
            _, def1 = PickMarker.new(self.username, game.name, markernames,
              self.guiboards[game])
            def1.addCallback(self.pick_marker)
            self.pickcolor = None

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

    def _init_guiboard(self, game):
        self.guiboards[game] = GUIMasterBoard.GUIMasterBoard(game.board, game,
          self.user, self.username)
        game.add_observer(self.guiboards[game])

    def update(self, observed, action):
        """Updates from User will come via remote_update, with
        observed set to None."""
        log("update", action)
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
            self._init_guiboard(game)
            self._maybe_pick_color(game)
        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            game.assign_color(action.playername, action.color)
            self._maybe_pick_color(game)
            self._maybe_pick_first_marker(game, action.playername)
        elif isinstance(action, Action.GameOver):
            # TODO Destroy windows and dialogs?
            if action.winner_names:
                log("Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names)))
            else:
                log("Game %s over, draw" % action.game_name)

        self.notify(action)
