__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"

"""Outward-facing facade for client side."""


import logging

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implementer

from slugathon.net import config
from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed
from slugathon.game import Action, Game
from slugathon.gui import Lobby, PickColor, PickMarker, GUIMasterBoard
from slugathon.gui import MainWindow


@implementer(IObserver)
class Client(pb.Referenceable, Observed):
    def __init__(self, playername, password, host="localhost",
      port=config.DEFAULT_PORT):
        Observed.__init__(self)
        self.playername = playername
        self.playername = playername  # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.factory = pb.PBClientFactory()
        self.factory.unsafeTracebacks = True
        self.user = None
        self.playernames = set()
        self.games = []
        self.guiboards = {}   # Maps game to guiboard
        self.pickcolor = None

    def remote_set_name(self, name):
        self.playername = name
        return name

    def remote_ping(self):
        return True

    def __repr__(self):
        return "Client " + str(self.playername)

    def connect(self):
        user_pass = credentials.UsernamePassword(self.playername,
          self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallback(self.connected)
        # No errback here; let Connect's errback handle failed login.
        return def1

    def connected(self, user):
        if user:
            self.user = user
            def1 = user.callRemote("get_playernames")
            def1.addCallback(self.got_playernames)
            def1.addErrback(self.failure)

    def got_playernames(self, playernames):
        """Only called when the client first connects to the server."""
        self.playernames.clear()
        for playername in playernames:
            self.playernames.add(playername)
        def1 = self.user.callRemote("get_games")
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        logging.info(game_info_tuples)
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        self.main_window = MainWindow.MainWindow(self.playername)
        lobby = Lobby.Lobby(self.user, self.playername,
          self.playernames, self.games, self.main_window)
        self.main_window.add_lobby(lobby)
        self.add_observer(lobby)

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def add_game(self, game_info_tuple):
        (name, create_time, start_time, min_players, max_players,
          playernames, started, finish_time, winner_names,
          loser_names) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players, started=started, finish_time=finish_time)
        self.add_observer(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        if winner_names:
            logging.debug(winner_names)
            # XXX Hack
            game._winner_names = winner_names
            game._loser_names = loser_names
        self.games.append(game)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    def failure(self, error):
        log.err(error)

    def remote_update(self, action, names):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action, names)

    def _maybe_pick_color(self, game):
        if (game.next_playername_to_pick_color == self.playername and
          self.pickcolor is None):
            self.pickcolor, def1 = PickColor.new(self.playername, game,
              game.colors_left, self.main_window)
            def1.addCallback(self._cb_pickcolor)

    def _cb_pickcolor(self, (game, color)):
        """Callback for PickColor"""
        if color is None:
            self._maybe_pick_color(game)
        else:
            def1 = self.user.callRemote("pick_color", game.name, color)
            def1.addErrback(self.failure)

    def _maybe_pick_first_marker(self, game, playername):
        if playername == self.playername:
            player = game.get_player_by_name(playername)
            markerids_left = sorted(player.markerids_left.copy())
            _, def1 = PickMarker.new(self.playername, game.name,
              markerids_left, self.main_window)
            def1.addCallback(self.pick_marker)
            self.pickcolor = None

    def pick_marker(self, (game_name, playername, markerid)):
        """Callback from PickMarker."""
        game = self.name_to_game(game_name)
        player = game.get_player_by_name(playername)
        if markerid is None:
            if not player.markerid_to_legion:
                self._maybe_pick_first_marker(game, playername)
        else:
            player.pick_marker(markerid)
            if not player.markerid_to_legion:
                def1 = self.user.callRemote("pick_first_marker", game_name,
                  markerid)
                def1.addErrback(self.failure)

    def _init_guiboard(self, game):
        logging.info(game)
        guiboard = self.guiboards[game] = GUIMasterBoard.GUIMasterBoard(
          game.board, game, self.user, self.playername,
          parent_window=self.main_window)
        self.main_window.add_guiboard(guiboard)
        game.add_observer(guiboard)

    def update(self, observed, action, names):
        """Updates from User will come via remote_update, with
        observed set to None."""
        logging.info("%s", action)
        if isinstance(action, Action.AddUsername):
            self.playernames.add(action.playername)
        elif isinstance(action, Action.DelUsername):
            self.playernames.remove(action.playername)
        elif isinstance(action, Action.FormGame):
            game_info_tuple = (action.game_name, action.create_time,
              action.start_time, action.min_players, action.max_players,
              [action.playername], False, None, None, None)
            self.add_game(game_info_tuple)
        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)
        elif isinstance(action, Action.AssignedAllTowers):
            game = self.name_to_game(action.game_name)
            if self.playername in game.playernames:
                self._init_guiboard(game)
                self._maybe_pick_color(game)
        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            game.assign_color(action.playername, action.color)
            self._maybe_pick_color(game)
            self._maybe_pick_first_marker(game, action.playername)
        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                logging.info("Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names)))
            else:
                logging.info("Game %s over, draw" % action.game_name)

        self.notify(action, names)
