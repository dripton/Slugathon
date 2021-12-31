import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from twisted.cred import credentials
from twisted.internet import defer, reactor
from twisted.python import log
from twisted.spread.pb import PBClientFactory, Referenceable
from zope.interface import implementer

from slugathon.game import Action, Game
from slugathon.gui import (
    GUIMasterBoard,
    Lobby,
    MainWindow,
    PickColor,
    PickMarker,
)
from slugathon.net import User, config
from slugathon.util.Observed import IObserved, IObserver, Observed

__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Outward-facing facade for client side."""


@implementer(IObserver)
class Client(Referenceable, Observed):
    def __init__(
        self,
        playername: str,
        password: str,
        host: str = "localhost",
        port: int = config.DEFAULT_PORT,
    ):
        Observed.__init__(self)
        self.playername = playername
        self.playername = playername  # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.factory = PBClientFactory()  # type: ignore
        self.factory.unsafeTracebacks = True
        self.user = None  # type: Optional[User.User]
        self.playernames = set()  # type: Set[str]
        self.games = []  # type: List[Game.Game]
        self.guiboards = (
            {}
        )  # type: Dict[Game.Game, GUIMasterBoard.GUIMasterBoard]
        self.pickcolor = None  # type: Optional[PickColor.PickColor]

    def remote_set_playername(self, playername: str) -> None:
        self.playername = playername

    def remote_ping(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "Client " + str(self.playername)

    def connect(self) -> defer.Deferred:
        user_pass = credentials.UsernamePassword(
            bytes(self.playername, "utf-8"), bytes(self.password, "utf-8")
        )  # type: ignore
        reactor.connectTCP(self.host, self.port, self.factory)  # type: ignore
        def1 = self.factory.login(user_pass, self)  # type: ignore
        def1.addCallback(self.connected)
        # No errback here; let Connect's errback handle failed login.
        return def1

    def connected(self, user: Optional[User.User]) -> None:
        if user:
            self.user = user
            def1 = user.callRemote("get_playernames")  # type: ignore
            def1.addCallback(self.got_playernames)
            def1.addErrback(self.failure)

    def got_playernames(self, playernames: Set[str]) -> None:
        """Only called when the client first connects to the server."""
        self.playernames.clear()
        for playername in playernames:
            self.playernames.add(playername)
        def1 = self.user.callRemote("get_games")  # type: ignore
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(
        self,
        game_info_tuples: List[
            Tuple[
                str,
                float,
                float,
                int,
                int,
                List[str],
                bool,
                float,
                List[str],
                List[str],
            ]
        ],
    ) -> None:
        """Only called when the client first connects to the server."""
        logging.info(game_info_tuples)
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        self.main_window = MainWindow.MainWindow(self.playername)
        assert self.user is not None
        lobby = Lobby.Lobby(
            self.user,
            self.playername,
            self.playernames,
            self.games,
            self.main_window,
        )
        self.main_window.add_lobby(lobby)
        self.add_observer(lobby)

    def name_to_game(self, game_name: str) -> Optional[Game.Game]:
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def add_game(
        self,
        game_info_tuple: Tuple[
            str,
            float,
            float,
            int,
            int,
            List[str],
            bool,
            Optional[float],
            List[str],
            List[str],
        ],
    ) -> None:
        (
            name,
            create_time,
            start_time,
            min_players,
            max_players,
            playernames,
            started,
            finish_time,
            winner_names,
            loser_names,
        ) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(
            name,
            owner,
            create_time,
            start_time,
            min_players,
            max_players,
            started=started,
            finish_time=finish_time,
        )
        self.add_observer(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        if winner_names:
            logging.debug(winner_names)
        self.games.append(game)

    def remove_game(self, game_name: str) -> None:
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    def _purge_old_games(self) -> None:
        max_games_wanted = 100
        num_to_purge = len(self.games) - max_games_wanted
        if num_to_purge >= 1:
            for game in self.games:
                if game.started and game.over:
                    self.games.remove(game)
                    num_to_purge -= 1
                    if num_to_purge < 1:
                        return

    def failure(self, error: Any) -> None:
        log.err(error)  # type: ignore

    def remote_update(self, action: Action.Action, names: List[str]) -> None:
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action, names)

    def _maybe_pick_color(self, game: Game.Game) -> None:
        if (
            game.next_playername_to_pick_color == self.playername
            and self.pickcolor is None
        ):
            self.pickcolor, def1 = PickColor.new(
                self.playername, game, game.colors_left, self.main_window
            )
            def1.addCallback(self._cb_pickcolor)

    def _cb_pickcolor(self, tup: Tuple[Game.Game, str]) -> None:
        """Callback for PickColor"""
        (game, color) = tup
        if color is None:
            self._maybe_pick_color(game)
        else:
            def1 = self.user.callRemote("pick_color", game.name, color)  # type: ignore
            def1.addErrback(self.failure)

    def _maybe_pick_first_marker(
        self, game: Game.Game, playername: str
    ) -> None:
        if playername == self.playername:
            player = game.get_player_by_name(playername)
            assert player is not None
            markerids_left = sorted(player.markerids_left.copy())
            _, def1 = PickMarker.new(
                self.playername, game.name, markerids_left, self.main_window
            )
            def1.addCallback(self.pick_marker)
            self.pickcolor = None

    def pick_marker(self, tup1: Tuple[str, str, str]) -> None:
        """Callback from PickMarker."""
        (game_name, playername, markerid) = tup1
        game = self.name_to_game(game_name)
        assert game is not None
        player = game.get_player_by_name(playername)
        assert player is not None
        if markerid is None:
            if not player.markerid_to_legion:
                self._maybe_pick_first_marker(game, playername)
        else:
            player.pick_marker(markerid)
            if not player.markerid_to_legion:
                def1 = self.user.callRemote(  # type: ignore
                    "pick_first_marker", game_name, markerid
                )
                def1.addErrback(self.failure)

    def _init_guiboard(self, game: Game.Game) -> None:
        logging.info(game)
        guiboard = self.guiboards[game] = GUIMasterBoard.GUIMasterBoard(
            game.board,
            game,
            self.user,
            self.playername,
            parent_window=self.main_window,
        )
        self.main_window.add_guiboard(guiboard)
        game.add_observer(guiboard)

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: List[str] = None,
    ) -> None:
        """Updates from User will come via remote_update, with
        observed set to None."""
        logging.info(f"{action}")
        if isinstance(action, Action.AddUsername):
            self.playernames.add(action.playername)
        elif isinstance(action, Action.DelUsername):
            self.playernames.remove(action.playername)
        elif isinstance(action, Action.FormGame):
            game_info_tuple = (
                action.game_name,
                action.create_time,
                action.start_time,
                action.min_players,
                action.max_players,
                [action.playername],
                False,
                None,
                [],
                [],
            )  # type: Tuple[str, float, float, int, int, List[str], bool, Optional[float], List[str], List[str]]
            self.add_game(game_info_tuple)
        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)
        elif isinstance(action, Action.AssignedAllTowers):
            game = self.name_to_game(action.game_name)
            if game and self.playername in game.playernames:
                self._init_guiboard(game)
                self._maybe_pick_color(game)
        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            if game:
                game.assign_color(action.playername, action.color)
                self._maybe_pick_color(game)
                self._maybe_pick_first_marker(game, action.playername)
        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                names_str = " and ".join(action.winner_names)
                logging.info(
                    f"Game {action.game_name} over, won by {names_str}"
                )
            else:
                logging.info(f"Game {action.game_name} over, draw")
            self._purge_old_games()

        self.notify(action, names)
