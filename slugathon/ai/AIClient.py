#!/usr/bin/env python3


from __future__ import annotations

import argparse
import logging
import os
import random
import re
import sys
import tempfile
from typing import Any, List, NoReturn, Optional, Tuple

from twisted.cred import credentials
from twisted.internet import defer, reactor
from twisted.internet.error import ReactorNotRunning
from twisted.internet.task import LoopingCall
from twisted.python import log
from twisted.spread.pb import (
    DeadReferenceError,
    PBClientFactory,
    PBConnectionLost,
    Referenceable,
)
from zope.interface import implementer

from slugathon.ai import BotParams, CleverBot, predictsplits
from slugathon.data.creaturedata import starting_creature_names
from slugathon.game import Action, Creature, Game, Phase
from slugathon.net import Results, User, config
from slugathon.util.Observed import IObserved, IObserver, Observed

__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Outward-facing facade for AI."""


TEMPDIR = tempfile.gettempdir()


defer.setDebugging(True)


@implementer(IObserver)
class AIClient(Referenceable, Observed):
    def __init__(
        self,
        playername: str,
        password: str,
        host: str,
        port: int,
        delay: int,
        game_name: str,
        log_path: str,
        ai_time_limit: int,
        player_time_limit: int,
        form_game: bool,
        min_players: int,
        max_players: int,
    ):
        Observed.__init__(self)
        self.playername = playername
        self.password = password
        self.host = host
        self.port = port
        self.delay = delay
        self.aiclass = "CleverBot"
        self.factory = PBClientFactory()  # type: ignore
        self.factory.unsafeTracebacks = True
        self.user = None  # type: Optional[User.User]
        self.games = []  # type: List[Game.Game]
        self.log_path = log_path
        self._setup_logging()

        bp = None
        # Using Results means we need to be on the server.
        results = Results.Results()
        if not re.match(r"^ai\d+$", playername):
            raise AssertionError("invalid playername for AI")
        player_id = int(playername[2:])
        player_info = results.get_player_info(player_id)
        if player_info is None:
            player_id = results.get_weighted_random_player_id()
            playername = f"ai{player_id}"
            player_info = results.get_player_info(player_id)
        assert player_info is not None
        bp = BotParams.BotParams.fromstring(player_info)
        self.ai = CleverBot.CleverBot(
            self.playername, ai_time_limit, bot_params=bp
        )
        self.game_name = game_name
        self.ai_time_limit = ai_time_limit
        self.player_time_limit = player_time_limit
        self.form_game = form_game
        self.min_players = min_players
        self.max_players = max_players
        self.paused = False
        self.last_actions = []  # type: List[Action.Action]
        self.aps = predictsplits.AllPredictSplits()

    def _setup_logging(self) -> None:
        if self.log_path:
            log_observer = log.PythonLoggingObserver()  # type: ignore
            log_observer.start()
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(filename)s %(funcName)s "
                "%(lineno)d %(message)s"
            )
            file_handler = logging.FileHandler(filename=self.log_path)
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
            logging.getLogger().setLevel(logging.DEBUG)

    def _setup_logging_form_game(self) -> None:
        log_observer = log.PythonLoggingObserver()  # type: ignore
        log_observer.start()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d "
            "%(message)s"
        )
        logdir = os.path.join(TEMPDIR, "slugathon")
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        self.log_path = os.path.join(
            logdir, f"slugathon-{self.game_name}-{self.playername}.log"
        )
        file_handler = logging.FileHandler(filename=self.log_path)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def remote_set_name(self, name: str) -> None:
        self.playername = name

    def remote_ping(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "AIClient " + str(self.playername)

    def connect(self) -> None:
        user_pass = credentials.UsernamePassword(  # type: ignore
            bytes(self.playername, "utf-8"), bytes(self.password, "utf-8")
        )
        reactor.connectTCP(self.host, self.port, self.factory)  # type: ignore
        def1 = self.factory.login(user_pass, self)  # type: ignore
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def connected(self, user: User.User) -> None:
        logging.info("connected")
        if user:
            self.user = user
            self.ai.user = user
            def1 = user.callRemote("get_games")  # type: ignore
            def1.addCallback(self.got_games)
            def1.addErrback(self.failure)
            lc = LoopingCall(user.callRemote, "ping")  # type: ignore
            def2 = lc.start(10)
            def2.addErrback(self.failure)
        else:
            logging.info("failed to get user; exiting")
            self.exit_unconditionally(1)

    def connection_failed(self, arg: Any) -> None:
        log.err(arg)  # type: ignore
        self.exit_unconditionally(1)

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
        logging.info(f"got games {game_info_tuples}")
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        if self.form_game:
            if not self.game_name:
                self.game_name = f"Game_{random.randrange(1000000)}"
            if not self.log_path:
                self._setup_logging_form_game()
            def1 = self.user.callRemote(  # type: ignore
                "form_game",
                self.game_name,
                self.min_players,
                self.max_players,
                self.ai_time_limit,
                self.player_time_limit,
                self.aiclass,
                self.ai.player_info,
            )
            def1.addErrback(self.failure)
        else:
            # If game_name is set, AI only tries to join game with that name.
            # If game_name is null, AI tries to join all games.
            for game in self.games:
                if not self.game_name or game.name == self.game_name:
                    logging.info(f"joining game {game.name}")
                    def1 = self.user.callRemote(  # type: ignore
                        "join_game",
                        game.name,
                        self.aiclass,
                        self.ai.player_info,
                    )
                    def1.addCallback(self.joined_game)
                    def1.addErrback(self.failure)

    def joined_game(self, success: bool) -> None:
        if not success:
            logging.info("failed to join game; aborting")
            self.exit_unconditionally(1)

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
        logging.info(f"add_game {game_info_tuple}")
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
        self.games.append(game)
        if not game.finish_time and (
            not self.game_name or game.name == self.game_name
        ):
            def1 = self.user.callRemote(  # type: ignore
                "join_game", game.name, self.aiclass, self.ai.player_info
            )
            def1.addErrback(self.failure)

    def remove_game(self, game_name: str) -> None:
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    def update_creatures(self, game: Game.Game) -> None:
        """Update creatures in game from self.aps."""
        for legion in game.all_legions():
            markerid = legion.markerid
            node = self.aps.get_leaf(markerid)
            if node and node.creature_names != legion.creature_names:
                legion.creatures = Creature.n2c(node.creature_names)
                for creature in legion.creatures:
                    creature.legion = legion

    def failure(self, error: Any) -> None:
        log.err(error)  # type: ignore
        if error.check(PBConnectionLost, DeadReferenceError):
            self.exit_unconditionally(1)

    def remote_update(self, action: Action.Action, names: List[str]) -> None:
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action, names)

    def exit_unconditionally(self, returncode: int) -> NoReturn:
        """Just exit the process, with no tracebacks or other drama."""
        logging.info(f"{returncode}")
        if reactor.running:  # type: ignore
            try:
                reactor.stop()  # type: ignore
            except ReactorNotRunning:
                pass
        sys.exit(returncode)

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        """Updates from User will come via remote_update, with observed set to
        None."""
        if (
            self.game_name is not None
            and hasattr(action, "game_name")
            and action.game_name != self.game_name  # type: ignore
        ):
            return
        if isinstance(action, Action.AddUsername) or isinstance(
            action, Action.DelUsername
        ):
            return

        logging.info(f"{action}")

        if isinstance(action, Action.ResumeAI):
            self.paused = False
            while self.last_actions:
                action = self.last_actions.pop(0)
                self.update(None, action, None)
            return

        # Make sure that Game knows that the angel is in the donor
        # legion before we send the Action to Game.
        if isinstance(action, Action.SummonAngel):
            game = self.name_to_game(action.game_name)
            assert game is not None
            node = self.aps.get_leaf(action.donor_markerid)
            if node:
                node.reveal_creatures([action.creature_name])
            self.update_creatures(game)

        # Update the Game first, then act.
        self.notify(action, names)

        if self.paused:
            self.last_actions.append(action)
            return

        if isinstance(action, Action.FormGame):
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
            if action.playername == self.playername:
                assert self.user is not None
                def1 = self.user.callRemote("start_game", self.game_name)  # type: ignore
                def1.addErrback(self.failure)

        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)

        elif isinstance(action, Action.AssignedAllTowers):
            logging.info(
                f"AssignedAllTowers player_info {self.ai.player_info}"
            )
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.maybe_pick_color, game)  # type: ignore

        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            assert game is not None
            self.ai.maybe_pick_color(game)
            reactor.callLater(  # type: ignore
                self.delay,
                self.ai.maybe_pick_first_marker,
                game,
                action.playername,
            )

        elif isinstance(action, Action.AssignedAllColors):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)  # type: ignore

        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                names_str = " and ".join(action.winner_names)
                logging.info(
                    f"Game {action.game_name} over, won by {names_str}"
                )
            else:
                logging.info(f"Game {action.game_name} over, draw")
            logging.info("AI exiting")
            self.exit_unconditionally(0)

        elif isinstance(action, Action.StartSplitPhase):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)  # type: ignore

        elif isinstance(action, Action.CreateStartingLegion):
            game = self.name_to_game(action.game_name)
            logging.info(
                f"ps = PredictSplits('{action.playername}', "
                + f"'{action.markerid}', {starting_creature_names})"
            )
            ps = predictsplits.PredictSplits(
                action.playername, action.markerid, starting_creature_names
            )
            self.aps.append(ps)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)  # type: ignore

        elif isinstance(action, Action.SplitLegion):
            game = self.name_to_game(action.game_name)
            assert game is not None
            parent = self.aps.get_leaf(action.parent_markerid)
            assert parent is not None
            parent.split(
                len(action.child_creature_names),
                action.child_markerid,
                game.turn,
            )
            if action.parent_creature_names[0] != "Unknown":
                parent = self.aps.get_leaf(action.parent_markerid)
                assert parent is not None
                parent.reveal_creatures(list(action.parent_creature_names))
                child = self.aps.get_leaf(action.child_markerid)
                assert child is not None
                child.reveal_creatures(list(action.child_creature_names))
            self.update_creatures(game)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)  # type: ignore

        elif isinstance(action, Action.UndoSplit):
            game = self.name_to_game(action.game_name)
            assert game is not None
            logging.info(
                f"self.aps.get_leaf('{action.parent_markerid}')"
                + f".merge(self.aps.get_leaf('{action.child_markerid}'), "
                + f"{game.turn})"
            )
            parent = self.aps.get_leaf(action.parent_markerid)
            assert parent is not None
            child = self.aps.get_leaf(action.child_markerid)
            assert child is not None
            parent.merge(child, game.turn)
            self.update_creatures(game)

        elif isinstance(action, Action.RollMovement):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.move_legions, game)  # type: ignore

        elif isinstance(action, Action.MoveLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.move_legions, game)  # type: ignore

        elif isinstance(action, Action.StartFightPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.StartMusterPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.ai.recruit, game)  # type: ignore

        elif isinstance(action, Action.ResolvingEngagement):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.resolve_engagement, game, action.hexlabel)  # type: ignore

        elif isinstance(action, Action.Flee) or isinstance(
            action, Action.Concede
        ):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.DoNotFlee):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.resolve_engagement, game, action.hexlabel)  # type: ignore

        elif isinstance(action, Action.Fight):
            game = self.name_to_game(action.game_name)
            assert game is not None
            player = game.get_player_by_name(self.playername)
            assert player is not None
            if (
                game.defender_legion
                and game.defender_legion.player.name == self.playername
                and action.defender_markerid in player.markerid_to_legion
            ):
                reactor.callLater(self.delay, self.ai.move_creatures, game)  # type: ignore

        elif isinstance(action, Action.MoveCreature):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.move_creatures, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.StartStrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.strike, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.Strike):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if action.carries:
                        reactor.callLater(  # type: ignore
                            self.delay,
                            self.ai.carry,
                            game,
                            action.striker_name,
                            action.striker_hexlabel,
                            action.target_name,
                            action.target_hexlabel,
                            action.num_dice,
                            action.strike_number,
                            action.carries,
                        )
                    else:
                        reactor.callLater(self.delay, self.ai.strike, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.Carry):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if action.carries_left:
                        reactor.callLater(  # type: ignore
                            self.delay,
                            self.ai.carry,
                            game,
                            action.striker_name,
                            action.striker_hexlabel,
                            action.target_name,
                            action.target_hexlabel,
                            action.num_dice,
                            action.strike_number,
                            action.carries_left,
                        )
                    else:
                        reactor.callLater(self.delay, self.ai.strike, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.strike, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.StartReinforceBattlePhase):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if legion == game.defender_legion:
                        reactor.callLater(self.delay, self.ai.reinforce, game)  # type: ignore
                    else:
                        reactor.callLater(self.delay, self.ai.summon_angel, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.StartManeuverBattlePhase):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.move_creatures, game)  # type: ignore
            else:
                logging.info("game.battle_active_legion not found")

        elif isinstance(action, Action.RecruitCreature):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            leaf = self.aps.get_leaf(action.markerid)
            assert leaf is not None
            leaf.reveal_creatures(list(action.recruiter_names))
            leaf.add_creature(action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.phase == Phase.MUSTER:
                    if (
                        game.active_player
                        and game.active_player.name == self.playername
                    ):
                        reactor.callLater(self.delay, self.ai.recruit, game)  # type: ignore
                elif game.phase == Phase.FIGHT:
                    if game.battle_phase == Phase.REINFORCE:
                        reactor.callLater(self.delay, self.ai.reinforce, game)  # type: ignore
                    else:
                        reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore
            else:
                if (
                    game.phase == Phase.FIGHT
                    and game.battle_phase != Phase.REINFORCE
                    and game.active_player.name == self.playername
                ):
                    reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.UndoRecruit):
            game = self.name_to_game(action.game_name)
            assert game is not None
            leaf = self.aps.get_leaf(action.markerid)
            assert leaf is not None
            leaf.remove_creature(action.creature_name)
            self.update_creatures(game)

        elif isinstance(action, Action.UnReinforce):
            game = self.name_to_game(action.game_name)
            assert game is not None
            leaf = self.aps.get_leaf(action.markerid)
            assert leaf is not None
            leaf.remove_creature(action.creature_name)
            self.update_creatures(game)

        elif isinstance(action, Action.DoNotReinforce):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if action.playername == self.playername:
                assert game.phase == Phase.FIGHT
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore
            else:
                if (
                    game.phase == Phase.FIGHT
                    and game.active_player.name == self.playername
                ):
                    reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.SummonAngel):
            game = self.name_to_game(action.game_name)
            assert game is not None
            donor = self.aps.get_leaf(action.donor_markerid)
            if donor:
                donor.reveal_creatures([action.creature_name])
                donor.remove_creature(action.creature_name)
            recipient = self.aps.get_leaf(action.markerid)
            if recipient:
                recipient.add_creature(action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon_angel, game)  # type: ignore
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.UnsummonAngel):
            game = self.name_to_game(action.game_name)
            assert game is not None
            leaf = self.aps.get_leaf(action.markerid)
            assert leaf is not None
            leaf.reveal_creatures([action.creature_name])
            leaf.remove_creature(action.creature_name)
            donor = self.aps.get_leaf(action.donor_markerid)
            assert donor is not None
            donor.add_creature(action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon_angel, game)  # type: ignore
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.DoNotSummonAngel):
            game = self.name_to_game(action.game_name)
            assert game is not None
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon_angel, game)  # type: ignore
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.BattleOver):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if action.winner_losses:
                node = self.aps.get_leaf(action.winner_markerid)
                if node:
                    node.remove_creatures(list(action.winner_losses))
            if action.loser_losses:
                node = self.aps.get_leaf(action.loser_markerid)
                if node:
                    node.remove_creatures(list(action.loser_losses))
            self.update_creatures(game)
            if game.active_player.name == self.playername:
                if game.attacker_legion:
                    legion = game.attacker_legion
                    if (
                        legion.markerid == action.winner_markerid
                        and legion.can_summon
                    ):
                        reactor.callLater(self.delay, self.ai.summon_angel, game)  # type: ignore
                        return
            else:
                if game.defender_legion:
                    legion = game.defender_legion
                    if legion.player.name == self.playername:
                        if (
                            legion.markerid == action.winner_markerid
                            and legion.can_recruit
                        ):
                            reactor.callLater(self.delay, self.ai.reinforce, game)  # type: ignore
                            return
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.CanAcquireAngels):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(  # type: ignore
                    self.delay,
                    self.ai.acquire_angels,
                    game,
                    action.markerid,
                    action.angels,
                    action.archangels,
                )

        elif isinstance(action, Action.AcquireAngels):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            for angel_name in action.angel_names:
                leaf = self.aps.get_leaf(action.markerid)
                assert leaf is not None
                leaf.add_creature(angel_name)
            self.update_creatures(game)
            logging.info(f"active player {game.active_player}")
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.DoNotAcquireAngels):
            game = self.name_to_game(action.game_name)
            assert game is not None
            assert game.active_player is not None
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)  # type: ignore

        elif isinstance(action, Action.EliminatePlayer) or isinstance(
            action, Action.Withdraw
        ):
            game = self.name_to_game(action.game_name)
            assert game is not None
            if hasattr(action, "loser_playername"):  # type: ignore
                playername = action.loser_playername  # type: ignore
            else:
                playername = action.playername  # type: ignore
            if playername == self.playername:
                if game.owner.name != self.playername:
                    logging.info("Eliminated; AI exiting")
                    self.exit_unconditionally(0)
            # Remove the dead player's PredictSplits from self.aps
            # to avoid problems later if his markers get reused.
            player = game.get_player_by_name(playername)
            assert player is not None
            color_abbrev = player.color_abbrev
            assert color_abbrev is not None
            for ps in self.aps:
                for node in ps.get_nodes():
                    if node.markerid.startswith(color_abbrev):
                        self.aps.remove(ps)
                        break

        elif isinstance(action, Action.RevealLegion):
            game = self.name_to_game(action.game_name)
            assert game is not None
            legion = game.find_legion(action.markerid)
            if legion:
                legion.reveal_creatures(list(action.creature_names))
                node = self.aps.get_leaf(action.markerid)
                if node is not None:
                    node.reveal_creatures(list(action.creature_names))
                self.update_creatures(game)

        elif isinstance(action, Action.PauseAI):
            self.paused = True

        else:
            logging.info(f"got unhandled action {action}")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    # Twisted throws a TypeError if playername or password is None.
    parser.add_argument(
        "-n", "--playername", action="store", type=str, default=""
    )
    parser.add_argument(
        "-a", "--password", action="store", type=str, default=""
    )
    parser.add_argument(
        "-s", "--server", action="store", type=str, default="localhost"
    )
    parser.add_argument(
        "-p", "--port", action="store", type=int, default=config.DEFAULT_PORT
    )
    parser.add_argument(
        "-d",
        "--delay",
        action="store",
        type=float,
        default=config.DEFAULT_AI_DELAY,
    )
    parser.add_argument("-g", "--game-name", action="store", type=str)
    parser.add_argument("-l", "--log-path", action="store", type=str)
    parser.add_argument(
        "--ai-time-limit",
        action="store",
        type=int,
        default=config.DEFAULT_AI_TIME_LIMIT,
    )
    parser.add_argument(
        "--player-time-limit",
        action="store",
        type=int,
        default=config.DEFAULT_PLAYER_TIME_LIMIT,
    )
    parser.add_argument("--form-game", action="store_true", default=False)
    parser.add_argument("--min-players", type=int, default=2)
    parser.add_argument("--max-players", type=int, default=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args, extras = parser.parse_known_args()
    aiclient = AIClient(
        args.playername,
        args.password,
        args.server,
        args.port,
        args.delay,
        args.game_name,
        args.log_path,
        args.ai_time_limit,
        args.player_time_limit,
        args.form_game,
        args.min_players,
        args.max_players,
    )
    reactor.callWhenRunning(aiclient.connect)  # type: ignore
    reactor.run()  # type: ignore


if __name__ == "__main__":
    main()
