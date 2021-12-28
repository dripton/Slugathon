from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from twisted.internet.error import ConnectionLost
from twisted.internet.task import LoopingCall
from twisted.python import log
from twisted.python.failure import Failure
from twisted.spread.pb import Avatar, PBConnectionLost, RemoteReference
from zope.interface import implementer

from slugathon.game import Action
from slugathon.net import Server
from slugathon.util.bag import bag
from slugathon.util.Observed import IObserved, IObserver

__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class User(Avatar):

    """Perspective for a player or spectator."""

    def __init__(
        self, name: str, server: Server.Server, client: RemoteReference
    ):
        self.name = name
        self.server = server
        self.client = client
        self.server.add_observer(self)
        self.logging_out = False

    def attached(self, mind: Any) -> None:
        pass

    def detached(self, mind: Any) -> None:
        pass

    def perspective_ping(self) -> bool:
        return True

    def perspective_get_name(self, arg: Any) -> str:
        return self.name

    def perspective_get_playernames(self) -> Set[str]:
        return self.server.playernames

    def perspective_get_games(
        self,
    ) -> List[
        Tuple[
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
        ]
    ]:
        """Return a list of Game.info_tuple for each current or recent game."""
        return self.server.get_game_info_tuples()

    def perspective_send_chat_message(
        self, dest: Optional[Set[str]], text: str
    ) -> None:
        """Send chat text to dest, a set of playernames.

        If dest is None, send to everyone.
        """
        self.server.send_chat_message(self.name, dest, text)

    def perspective_form_game(
        self,
        game_name: str,
        min_players: int,
        max_players: int,
        ai_time_limit: float,
        player_time_limit: float,
        player_class: str,
        player_info: str,
    ) -> Optional[str]:
        return self.server.form_game(
            self.name,
            game_name,
            min_players,
            max_players,
            ai_time_limit,
            player_time_limit,
            player_class,
            player_info,
        )

    def perspective_join_game(
        self, game_name: str, player_class: str, player_info: str
    ) -> bool:
        return self.server.join_game(
            self.name, game_name, player_class, player_info
        )

    def perspective_start_game(self, game_name: str) -> None:
        self.server.start_game(self.name, game_name)

    def perspective_pick_color(self, game_name: str, color: str) -> None:
        self.server.pick_color(self.name, game_name, color)

    def perspective_pick_first_marker(
        self, game_name: str, markerid: str
    ) -> None:
        self.server.pick_first_marker(self.name, game_name, markerid)

    def perspective_split_legion(
        self,
        game_name: str,
        parent_markerid: str,
        child_markerid: str,
        parent_creature_names: List[str],
        child_creature_names: List[str],
    ) -> None:
        self.server.split_legion(
            self.name,
            game_name,
            parent_markerid,
            child_markerid,
            parent_creature_names,
            child_creature_names,
        )

    def perspective_done_with_splits(self, game_name: str) -> None:
        self.server.done_with_splits(self.name, game_name)

    def perspective_take_mulligan(self, game_name: str) -> None:
        self.server.take_mulligan(self.name, game_name)

    def perspective_move_legion(
        self,
        game_name: str,
        markerid: str,
        hexlabel: int,
        entry_side: int,
        teleport: bool,
        teleporting_lord: Optional[str],
    ) -> None:
        self.server.move_legion(
            self.name,
            game_name,
            markerid,
            hexlabel,
            entry_side,
            teleport,
            teleporting_lord,
        )

    def perspective_done_with_moves(self, game_name: str) -> None:
        self.server.done_with_moves(self.name, game_name)

    def perspective_resolve_engagement(
        self, game_name: str, hexlabel: int
    ) -> None:
        self.server.resolve_engagement(self.name, game_name, hexlabel)

    def perspective_flee(self, game_name: str, markerid: str) -> None:
        self.server.flee(self.name, game_name, markerid)

    def perspective_do_not_flee(self, game_name: str, markerid: str) -> None:
        self.server.do_not_flee(self.name, game_name, markerid)

    def perspective_concede(
        self, game_name: str, markerid: str, enemy_markerid: str, hexlabel: int
    ) -> None:
        self.server.concede(
            self.name, game_name, markerid, enemy_markerid, hexlabel
        )

    def perspective_make_proposal(
        self,
        game_name: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
    ) -> None:
        self.server.make_proposal(
            self.name,
            game_name,
            attacker_markerid,
            attacker_creature_names,
            defender_markerid,
            defender_creature_names,
        )

    def perspective_accept_proposal(
        self,
        game_name: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
    ) -> None:
        self.server.accept_proposal(
            self.name,
            game_name,
            attacker_markerid,
            attacker_creature_names,
            defender_markerid,
            defender_creature_names,
        )

    def perspective_reject_proposal(
        self,
        game_name: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
    ) -> None:
        self.server.reject_proposal(
            self.name,
            game_name,
            attacker_markerid,
            attacker_creature_names,
            defender_markerid,
            defender_creature_names,
        )

    def perspective_no_more_proposals(
        self, game_name: str, attacker_markerid: str, defender_markerid: str
    ) -> None:
        self.server.no_more_proposals(
            self.name, game_name, attacker_markerid, defender_markerid
        )

    def perspective_fight(
        self, game_name: str, attacker_markerid: str, defender_markerid: str
    ) -> None:
        self.server.fight(
            self.name, game_name, attacker_markerid, defender_markerid
        )

    def perspective_move_creature(
        self,
        game_name: str,
        creature_name: str,
        old_hexlabel: str,
        new_hexlabel: str,
    ) -> None:
        self.server.move_creature(
            self.name, game_name, creature_name, old_hexlabel, new_hexlabel
        )

    def perspective_done_with_reinforcements(self, game_name: str) -> None:
        self.server.done_with_reinforcements(self.name, game_name)

    def perspective_done_with_maneuvers(self, game_name: str) -> None:
        self.server.done_with_maneuvers(self.name, game_name)

    def perspective_done_with_strikes(self, game_name: str) -> None:
        self.server.done_with_strikes(self.name, game_name)

    def perspective_done_with_counterstrikes(self, game_name: str) -> None:
        self.server.done_with_counterstrikes(self.name, game_name)

    def perspective_strike(
        self,
        game_name: str,
        creature_name: str,
        hexlabel: str,
        target_creature_name: str,
        target_hexlabel: str,
        num_dice: int,
        strike_number: int,
    ) -> None:
        self.server.strike(
            self.name,
            game_name,
            creature_name,
            hexlabel,
            target_creature_name,
            target_hexlabel,
            num_dice,
            strike_number,
        )

    def perspective_acquire_angels(
        self, game_name: str, markerid: str, angel_names: List[str]
    ) -> None:
        self.server.acquire_angels(self.name, game_name, markerid, angel_names)

    def perspective_do_not_acquire_angels(
        self, game_name: str, markerid: str
    ) -> None:
        logging.info(f"do_not_acquire_angels {self} {game_name} {markerid}")
        self.server.do_not_acquire_angels(self.name, game_name, markerid)

    def perspective_done_with_engagements(self, game_name: str) -> None:
        self.server.done_with_engagements(self.name, game_name)

    def perspective_recruit_creature(
        self,
        game_name: str,
        markerid: str,
        creature_name: str,
        recruiter_names: List[str],
    ) -> None:
        self.server.recruit_creature(
            self.name, game_name, markerid, creature_name, recruiter_names
        )

    def perspective_done_with_recruits(self, game_name: str) -> None:
        self.server.done_with_recruits(self.name, game_name)

    def perspective_summon_angel(
        self,
        game_name: str,
        markerid: str,
        donor_markerid: str,
        creature_name: str,
    ) -> None:
        self.server.summon_angel(
            self.name, game_name, markerid, donor_markerid, creature_name
        )

    def perspective_do_not_summon_angel(
        self, game_name: str, markerid: str
    ) -> None:
        self.server.do_not_summon_angel(self.name, game_name, markerid)

    def perspective_do_not_reinforce(
        self, game_name: str, markerid: str
    ) -> None:
        self.server.do_not_reinforce(self.name, game_name, markerid)

    def perspective_carry(
        self,
        game_name: str,
        carry_target_name: str,
        carry_target_hexlabel: str,
        carries: int,
    ) -> None:
        logging.info(
            f"perspective_carry {carry_target_name} {carry_target_hexlabel} "
            f"{carries}"
        )
        self.server.carry(
            self.name,
            game_name,
            carry_target_name,
            carry_target_hexlabel,
            carries,
        )

    def perspective_apply_action(self, action: Action.Action) -> None:
        """Pull the exact method and args out of the Action."""
        if isinstance(action, Action.UndoSplit):
            self.server.undo_split(
                self.name,
                action.game_name,
                action.parent_markerid,
                action.child_markerid,
            )
        elif isinstance(action, Action.UndoMoveLegion):
            self.server.undo_move_legion(
                self.name, action.game_name, action.markerid
            )
        elif isinstance(action, Action.UndoRecruit):
            self.server.undo_recruit(
                self.name, action.game_name, action.markerid
            )
        elif isinstance(action, Action.UndoMoveCreature):
            self.server.undo_move_creature(
                self.name,
                action.game_name,
                action.creature_name,
                action.new_hexlabel,
            )
        elif isinstance(action, Action.SplitLegion):
            self.server.split_legion(
                self.name,
                action.game_name,
                action.parent_markerid,
                action.child_markerid,
                list(action.parent_creature_names),
                list(action.child_creature_names),
            )
        elif isinstance(action, Action.MoveLegion):
            self.server.move_legion(
                self.name,
                action.game_name,
                action.markerid,
                action.hexlabel,
                action.entry_side,
                action.teleport,
                action.teleporting_lord,
            )
        elif isinstance(action, Action.MoveCreature):
            self.server.move_creature(
                self.name,
                action.game_name,
                action.creature_name,
                action.old_hexlabel,
                action.new_hexlabel,
            )
        elif isinstance(action, Action.RecruitCreature):
            self.server.recruit_creature(
                self.name,
                action.game_name,
                action.markerid,
                action.creature_name,
                list(action.recruiter_names),
            )

    def perspective_save(self, game_name: str) -> None:
        self.server.save(self.name, game_name)

    def perspective_withdraw(self, game_name: str) -> None:
        self.server.withdraw(self.name, game_name)

    def perspective_pause_ai(self, game_name: str) -> None:
        self.server.pause_ai(self.name, game_name)

    def perspective_resume_ai(self, game_name: str) -> None:
        self.server.resume_ai(self.name, game_name)

    def perspective_get_player_data(
        self,
    ) -> List[Dict[str, Union[str, float]]]:
        return self.server.get_player_data()

    def __repr__(self) -> str:
        return "User " + self.name

    def add_observer(self, mind: Any) -> None:
        logging.info(f"User.add_observer {self} {mind}")
        def1 = self.client.callRemote("set_name", self.name)  # type: ignore
        def1.addErrback(self.trap_connection_lost)
        def1.addErrback(self.log_failure)
        lc = LoopingCall(self.client.callRemote, "ping")
        def2 = lc.start(30)
        def2.addErrback(self.trap_connection_lost)
        def2.addErrback(self.log_failure)

    def trap_connection_lost(self, failure: Failure) -> None:
        failure.trap(ConnectionLost, PBConnectionLost)  # type: ignore
        if not self.logging_out:
            self.logging_out = True
            logging.info(f"Connection lost for {self.name}; logging out")
            self.logout()

    def log_failure(self, failure: Any) -> None:
        log.err(failure)  # type: ignore

    def logout(self) -> None:
        logging.info(f"logout {self.name}")
        self.server.logout(self)

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        """Defer updates to its client, dropping the observed reference."""
        # Filter DriftDamage; we redo it on the client.
        if isinstance(action, Action.DriftDamage):
            return
        # Filter SplitLegion to our own player with censored creature names;
        # it'll get the other one with creature names.
        if (
            isinstance(action, Action.SplitLegion)
            and action.playername == self.name
            and "Unknown" in action.parent_creature_names
        ):
            return
        def1 = self.client.callRemote("update", action, names)  # type: ignore
        def1.addErrback(self.trap_connection_lost)
        def1.addErrback(self.log_failure)
