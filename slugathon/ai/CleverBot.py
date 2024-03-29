import collections
import copy
import itertools
import logging
import random
import time
from sys import maxsize
from typing import (
    Any,
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
)

from twisted.python import log
from zope.interface import implementer

from slugathon.ai import BotParams
from slugathon.ai.Bot import Bot
from slugathon.game import Creature, Game, Legion, Phase, Player
from slugathon.net import User

__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


"""An attempt at a smarter AI."""


def best7(score_moves: List[Tuple[float, str]]) -> Set[str]:
    """Return a set of the the best (highest score) (up to) 7 moves from
    score_moves, which is a sorted list of (score, move) tuples.

    If there's a tie, pick at random.
    """
    score_moves = score_moves[:]
    best_moves = set()  # type: Set[str]
    while score_moves and len(best_moves) < 7:
        choices = []
        best_score = score_moves[-1][0]
        for (score, move) in reversed(score_moves):
            if score == best_score:
                choices.append((score, move))
            else:
                break
        (score, move) = random.choice(choices)
        score_moves.remove((score, move))
        best_moves.add(move)
    return best_moves


@implementer(Bot)
class CleverBot(object):
    def __init__(
        self,
        playername: str,
        ai_time_limit: float,
        bot_params: Optional[BotParams.BotParams] = None,
    ):
        logging.info(f"CleverBot {playername=} {ai_time_limit=}")
        self.playername = playername
        self.user = None  # type: Optional[User.User]
        self.ai_time_limit = ai_time_limit
        self.best_creature_moves = (
            None
        )  # type: Optional[List[Tuple[str, str, str]]]
        if bot_params is None:
            self.bp = BotParams.default_bot_params
        else:
            self.bp = bot_params

    @property
    def player_info(self) -> str:
        """Return a string with information for result-tracking purposes."""
        return str(self.bp)

    def maybe_pick_color(self, game: Game.Game) -> None:
        logging.info("")
        if game.next_playername_to_pick_color == self.playername:
            color = random.choice(game.colors_left)
            def1 = self.user.callRemote("pick_color", game.name, color)  # type: ignore
            def1.addErrback(self.failure)

    def maybe_pick_first_marker(
        self, game: Game.Game, playername: str
    ) -> None:
        logging.info("")
        if playername == self.playername:
            player = game.get_player_by_name(playername)
            assert player is not None
            markerid = self.choose_marker(player)
            self._pick_marker(game, self.playername, markerid)

    def _pick_marker(
        self, game: Game.Game, playername: str, markerid: str
    ) -> None:
        logging.info("")
        player = game.get_player_by_name(playername)
        assert player is not None
        if markerid is None:
            if not player.markerid_to_legion:
                self.maybe_pick_first_marker(game, playername)
        else:
            player.pick_marker(markerid)
            if not player.markerid_to_legion:
                def1 = self.user.callRemote(  # type: ignore
                    "pick_first_marker", game.name, markerid
                )
                def1.addErrback(self.failure)

    def choose_marker(self, player: Player.Player) -> str:
        """Pick a legion marker randomly, except prefer my own markers
        to captured ones to be less annoying."""
        own_markerids_left = [
            name
            for name in player.markerids_left
            if name[:2] == player.color_abbrev
        ]
        if own_markerids_left:
            return random.choice(own_markerids_left)
        else:
            return random.choice(list(player.markerids_left))

    # TODO Avoid hitting 100-point multiples with 7-high legions.
    def choose_engagement(self, game: Game.Game) -> None:
        """Resolve engagements.

        Fight with legions that have angels first (so we can summon them),
        then with the most important legion.
        """
        logging.info("")
        if (
            game.pending_summon
            or game.pending_reinforcement
            or game.pending_acquire
        ):
            logging.info(
                f"choose_engagement bailing early {game.pending_summon=}"
                f"{game.pending_reinforcement=} {game.pending_acquire=}"
            )
            return
        hexlabels = list(game.engagement_hexlabels)
        if hexlabels:
            if len(hexlabels) >= 2:
                player = game.get_player_by_name(self.playername)
                assert player is not None
                value_to_hexlabel = []
                for hexlabel in hexlabels:
                    legion = player.friendly_legions(hexlabel=hexlabel).pop()
                    value = legion.sort_value
                    if not player.summoned and legion.any_summonable:
                        value += 1000
                    value_to_hexlabel.append((value, hexlabel))
                value_to_hexlabel.sort()
                (value, hexlabel) = value_to_hexlabel[-1]
            else:
                hexlabel = hexlabels[0]
            logging.info("calling resolve_engagement")
            def1 = self.user.callRemote(  # type: ignore
                "resolve_engagement", game.name, hexlabel
            )
            def1.addErrback(self.failure)
        else:
            logging.info("calling done_with_engagements")
            def1 = self.user.callRemote("done_with_engagements", game.name)  # type: ignore
            def1.addErrback(self.failure)

    # TODO concede, negotiate
    def resolve_engagement(self, game: Game.Game, hexlabel: int) -> None:
        """Resolve the engagement in hexlabel."""
        logging.info(f"{game=} {hexlabel=}")
        attacker = None
        defender = None
        for legion in game.all_legions(hexlabel):
            if legion.player == game.active_player:
                attacker = legion
            else:
                defender = legion
        if attacker:
            logging.info(f"{attacker=} {attacker.player.name=}")
        if defender:
            logging.info(f"{defender=} {defender.player.name=}")
        if not attacker or not defender:
            logging.info("no attacker or defender; bailing")
            return
        if defender.player.name == self.playername:
            if game.defender_chose_not_to_flee:
                logging.info("defender already chose not to flee")
            else:
                logging.info("defender hasn't chosen whether to flee yet")
                if defender.can_flee:
                    logging.info("can flee")
                    if (
                        defender.terrain_combat_value * self.bp.FLEE_RATIO  # type: ignore
                        < attacker.terrain_combat_value
                    ):
                        logging.info("fleeing")
                        def1 = self.user.callRemote(  # type: ignore
                            "flee", game.name, defender.markerid
                        )
                        def1.addErrback(self.failure)
                    else:
                        logging.info("not fleeing")
                        def1 = self.user.callRemote(  # type: ignore
                            "do_not_flee", game.name, defender.markerid
                        )
                        def1.addErrback(self.failure)
                else:
                    logging.info("can't flee")
                    def1 = self.user.callRemote(  # type: ignore
                        "do_not_flee", game.name, defender.markerid
                    )
                    def1.addErrback(self.failure)
        elif attacker.player.name == self.playername:
            if not game.defender_chose_not_to_flee:
                # Wait for the defender to choose whether to flee.
                logging.info("waiting for defender")
            else:
                logging.info("attacker fighting")
                def1 = self.user.callRemote(  # type: ignore
                    "fight", game.name, attacker.markerid, defender.markerid
                )
                def1.addErrback(self.failure)
        else:
            logging.info("not my engagement")

    def _scary_enemy_legions_behind(self, legion: Legion.Legion) -> bool:
        """Return True if there are any scary enemy legions that can
        catch this legion next turn."""
        player = legion.player
        game = player.game
        legion_combat_value = legion.combat_value
        hexlabel = legion.hexlabel
        for enemy in player.enemy_legions():
            # TODO take terrain into account
            if enemy.combat_value >= self.bp.BE_SQUASHED * legion_combat_value:  # type: ignore
                for roll in range(1, 6 + 1):
                    hex1 = game.board.hexes[enemy.hexlabel]
                    moves = game.find_normal_moves(enemy, hex1, roll).union(
                        game.find_titan_teleport_moves(enemy)
                    )
                    hexlabels = {move[0] for move in moves}
                    if hexlabel in hexlabels:
                        return True
        return False

    def _scary_enemy_legions_ahead(self, legion: Legion.Legion) -> bool:
        """Return True if there are any scary enemy legions that this
        legion can catch next turn."""
        player = legion.player
        game = player.game
        legion_combat_value = legion.combat_value
        hexlabel = legion.hexlabel
        all_hexlabels = set()
        for roll in range(1, 6 + 1):
            hex1 = game.board.hexes[hexlabel]
            moves = game.find_normal_moves(legion, hex1, roll).union(
                game.find_titan_teleport_moves(legion)
            )
            hexlabels = {move[0] for move in moves}
            all_hexlabels.update(hexlabels)
        for enemy in player.enemy_legions():
            # TODO take terrain into account
            if enemy.combat_value >= self.bp.BE_SQUASHED * legion_combat_value:  # type: ignore
                if enemy.hexlabel in all_hexlabels:
                    return True
        return False

    def _pick_recruit_and_recruiters(
        self, legion: Legion.Legion
    ) -> Tuple[Optional[str], Optional[Tuple[str, ...]]]:
        """Return a tuple of (recruit name, recruiter names), or (None, None)."""
        player = legion.player
        game = player.game
        caretaker = game.caretaker
        masterhex = game.board.hexes[legion.hexlabel]
        mterrain = masterhex.terrain
        lst = legion.available_recruits_and_recruiters(mterrain, caretaker)
        # Put the biggest creature first
        lst.reverse()

        if not lst:
            return (None, None)

        # TODO We need to be able to split smarter before recruiting
        # a third lesser creature is useful for 6-high legions.
        if (
            len(lst) == 1
            or len(legion) == 6
            or self._scary_enemy_legions_behind(legion)
            or self._scary_enemy_legions_ahead(legion)
            or random.random() > self.bp.THIRD_CREATURE_RATIO  # type: ignore
        ):
            best_recruit_index = 0

        else:
            # Look at what we can recruit on each movement roll, to see if we
            # should take a third creature of a kind.
            all_hexlabels = set()
            for roll in range(1, 6 + 1):
                moves = game.find_all_moves(
                    legion, game.board.hexes[legion.hexlabel], roll
                )
                hexlabels = {move[0] for move in moves}
                all_hexlabels.update(hexlabels)
            mterrains = set()
            for hexlabel in all_hexlabels:
                mterrains.add(game.board.hexes[hexlabel].terrain)

            all_recruits = {tup[0] for tup in lst}
            recruit_to_later_recruits = {}
            for recruit in all_recruits:
                # Make a copy of the legion so we can safely modify it.
                legion2 = Legion.Legion(
                    player,
                    legion.markerid,
                    legion.creatures[:],
                    legion.hexlabel,
                )
                legion2.add_creature_by_name(recruit)
                for mterrain2 in mterrains:
                    lst2 = legion2.available_recruits_and_recruiters(
                        mterrain2, caretaker
                    )
                    later_recruits = {tup[0] for tup in lst2}
                    recruit_to_later_recruits[recruit] = later_recruits
            best_creature = None
            best_recruit = None
            for recruit2, recruits in recruit_to_later_recruits.items():
                for creature_name in [recruit2] + list(recruits):
                    creature = Creature.Creature(creature_name)
                    if (
                        best_creature is None
                        or creature.sort_value > best_creature.sort_value
                    ):
                        best_creature = creature
                        best_recruit = recruit2
            best_recruit_index = 0
            for ii, tup in enumerate(lst):
                if tup[0] == best_recruit:
                    best_recruit_index = ii
                    break

        tup = lst[best_recruit_index]
        recruit3 = tup[0]

        # And pick randomly among its recruiters.
        possible_recruiters = set()
        for tup in lst:
            if tup[0] == recruit3:
                recruiters = tup[1:]
                possible_recruiters.add(recruiters)
        recruiters = random.choice(list(possible_recruiters))
        return (recruit3, recruiters)

    def recruit(self, game: Game.Game) -> None:
        logging.info("")
        player = game.active_player
        assert player is not None
        if player.name != self.playername:
            logging.info("not my turn")
            return
        for legion in player.legions:
            if legion.moved and legion.can_recruit:
                recruit, recruiters = self._pick_recruit_and_recruiters(legion)
                if recruit is not None:
                    logging.info(
                        f"calling recruit_creature {legion.markerid=}"
                        f"{recruit=} {recruiters=}"
                    )
                    def1 = self.user.callRemote(  # type: ignore
                        "recruit_creature",
                        game.name,
                        legion.markerid,
                        recruit,
                        recruiters,
                    )
                    def1.addErrback(self.failure)
                    return
        logging.info("calling done_with_recruits")
        def1 = self.user.callRemote("done_with_recruits", game.name)  # type: ignore
        def1.addErrback(self.failure)

    def reinforce(self, game: Game.Game) -> None:
        """Reinforce, during the REINFORCE battle phase or after the battle"""
        logging.info("")
        battle_over = game.is_battle_over
        if not battle_over:
            assert game.battle_active_player is not None
            assert game.battle_active_player.name == self.playername
            assert game.battle_phase == Phase.REINFORCE
        legion = game.defender_legion
        assert legion is not None
        if legion.can_recruit and (battle_over or game.battle_turn == 4):
            recruit, recruiters = self._pick_recruit_and_recruiters(legion)
            if recruit is not None:
                logging.info(f"calling recruit_creature {recruit=}")
                def1 = self.user.callRemote(  # type: ignore
                    "recruit_creature",
                    game.name,
                    legion.markerid,
                    recruit,
                    recruiters,
                )
                def1.addErrback(self.failure)
                return
        if battle_over:
            logging.info("calling do_not_reinforce")
            def1 = self.user.callRemote(  # type: ignore
                "do_not_reinforce", game.name, legion.markerid
            )
            def1.addErrback(self.failure)
        else:
            logging.info("calling done_with_reinforcements")
            def1 = self.user.callRemote("done_with_reinforcements", game.name)  # type: ignore
            def1.addErrback(self.failure)

    # TODO Consider value of this legion and donor legion before deciding
    # whether to summon.  But we may want to summon from a greater legion
    # if it's 7 high and doing this lets it recruit.
    def summon_angel(self, game: Game.Game) -> None:
        """Summon, during the REINFORCE battle phase or after the battle."""
        logging.info("")
        during_battle = not game.is_battle_over
        assert game.active_player is not None
        assert game.active_player.name == self.playername
        if during_battle and game.battle_phase != Phase.REINFORCE:
            return
        legion = game.attacker_legion
        assert legion is not None
        assert legion.player.name == self.playername
        if legion.can_summon and (
            not during_battle
            or game.battle_turn is not None
            and game.first_attacker_kill
            in {game.battle_turn - 1, game.battle_turn}
        ):
            summonables = legion.player.all_summonables
            if summonables:
                tuples = sorted(
                    (
                        (creature.sort_value, creature)
                        for creature in summonables
                    ),
                    reverse=True,
                )
                summonable = tuples[0][1]

                # After battle, do not summon if 6 high and we could recruit
                # something at least as good as the summonable.
                recruit = None
                if not during_battle:
                    if (
                        len(legion) >= 6
                        and legion.can_recruit
                        and legion.moved
                    ):
                        recruit_name, _ = self._pick_recruit_and_recruiters(
                            legion
                        )
                        if recruit_name:
                            recruit = Creature.Creature(recruit_name)

                if not recruit or summonable.sort_value > recruit.sort_value:
                    donor = summonable.legion
                    assert donor is not None
                    logging.info(
                        f"calling _summon_angel {legion.markerid} "
                        f"{donor.markerid} {summonable.name}"
                    )
                    def1 = self.user.callRemote(  # type: ignore
                        "summon_angel",
                        game.name,
                        legion.markerid,
                        donor.markerid,
                        summonable.name,
                    )
                    def1.addErrback(self.failure)
                    return

        logging.info(f"calling do_not_summon_angel {legion.markerid}")
        def1 = self.user.callRemote(  # type: ignore
            "do_not_summon_angel", game.name, legion.markerid
        )
        def1.addErrback(self.failure)

        if during_battle:
            logging.info("calling done_with_reinforcements")
            def1 = self.user.callRemote("done_with_reinforcements", game.name)  # type: ignore
            def1.addErrback(self.failure)

    def acquire_angels(
        self,
        game: Game.Game,
        markerid: str,
        num_angels: int,
        num_archangels: int,
    ) -> None:
        logging.info(f"{markerid=} {num_angels=} {num_archangels=}")
        player = game.get_player_by_name(self.playername)
        assert player is not None
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        starting_height = len(legion)
        acquires = 0
        angel_names = []
        while starting_height + acquires < 7 and num_archangels:
            angel_names.append("Archangel")
            num_archangels -= 1
            acquires += 1
        while starting_height + acquires < 7 and num_angels:
            angel_names.append("Angel")
            num_angels -= 1
            acquires += 1
        if angel_names:
            # If we can recruit something better than the worst angel, don't
            # take it.
            if (
                len(legion) + acquires >= 7
                and legion.can_recruit
                and legion.moved
            ):
                recruit_name, _ = self._pick_recruit_and_recruiters(legion)
                if recruit_name:
                    recruit = Creature.Creature(recruit_name)
                    angel = Creature.Creature(angel_names[-1])
                    if recruit.sort_value > angel.sort_value:
                        angel_names = angel_names[:-1]
                if angel_names:
                    logging.info(
                        f"calling acquire_angels {markerid=} {angel_names=}"
                    )
                    def1 = self.user.callRemote(  # type: ignore
                        "acquire_angels", game.name, markerid, angel_names
                    )
                    def1.addErrback(self.failure)
                    return
        logging.info(f"calling do_not_acquire_angels {markerid=}")
        def1 = self.user.callRemote(  # type: ignore
            "do_not_acquire_angels", game.name, markerid
        )
        def1.addErrback(self.failure)

    # TODO Sometimes split off a better creature to enable better recruiting.
    # TODO Fear being caught from behind by a bigger legion.
    def split(self, game: Game.Game) -> None:
        """Split a legion, or end split phase."""
        logging.info("split")
        assert game.active_player is not None
        logging.info(
            f"playername {self.playername} active_playername "
            f"{game.active_player.name}"
        )
        if game.active_player.name != self.playername:
            logging.warning("called split out of turn; exiting")
            return
        player = game.active_player
        assert player is not None
        caretaker = game.caretaker
        # Let more important legions get the first crack at markers.
        for legion in player.sorted_legions:
            if len(legion) == 8:
                if game.turn != 1:
                    raise AssertionError("8-high legion", legion)
                # initial split 4-4, one lord per legion
                # TODO Parameterize and train initial split preferences
                # split_gargs, split_ogres, split_centaurs,
                # gargs_with_titan, ogres_with_titan, centaurs_with_titan
                logging.info("initial split")
                new_markerid = self.choose_marker(player)
                lord = random.choice(["Titan", "Angel"])
                creatures = ["Centaur", "Gargoyle", "Ogre"]
                creature1 = random.choice(creatures)
                creature2 = creature1
                creature3 = creature1
                while creature3 == creature1:
                    creature3 = random.choice(creatures)
                new_creatures = [lord, creature1, creature2, creature3]
                old_creatures = legion.creature_names
                for creature in new_creatures:
                    old_creatures.remove(creature)
                logging.info(f"{new_creatures=} {old_creatures=}")
                def1 = self.user.callRemote(  # type: ignore
                    "split_legion",
                    game.name,
                    legion.markerid,
                    new_markerid,
                    old_creatures,
                    new_creatures,
                )
                def1.addErrback(self.failure)
                return
            elif len(legion) == 7 and player.markerids_left:
                logging.info("7-high")
                good_recruit_rolls = set()
                safe_split_rolls = set()
                new_markerid = self.choose_marker(player)
                lst = legion.sorted_creatures
                split = lst[-2:]
                split_names = [creature.name for creature in split]
                keep = lst[:-2]
                keep_names = [creature.name for creature in keep]
                logging.info(f"{lst=} {split_names=} {keep_names=}")
                # Pretend to split so that we can compute the bigger
                # child legion's combat value.
                new_legion1 = Legion.Legion(
                    legion.player,
                    legion.markerid,
                    Creature.n2c(keep_names),
                    legion.hexlabel,
                )
                for roll in range(1, 6 + 1):
                    moves = game.find_all_moves(
                        legion, game.board.hexes[legion.hexlabel], roll
                    )
                    for hexlabel, entry_side in moves:
                        masterhex2 = game.board.hexes[hexlabel]
                        terrain = masterhex2.terrain
                        recruits = legion.available_recruits(
                            terrain, caretaker
                        )
                        if recruits:
                            recruit = Creature.Creature(recruits[-1])
                            if recruit.sort_value > lst[-1].sort_value:
                                good_recruit_rolls.add(roll)
                        enemies = player.enemy_legions(hexlabel)
                        if enemies:
                            enemy = enemies.pop()
                            new_legion1.hexlabel = hexlabel
                            if (
                                enemy.terrain_combat_value
                                < self.bp.SQUASH  # type: ignore
                                * new_legion1.terrain_combat_value
                            ):
                                safe_split_rolls.add(roll)
                        else:
                            safe_split_rolls.add(roll)
                if good_recruit_rolls and len(safe_split_rolls) == 6:
                    def1 = self.user.callRemote(  # type: ignore
                        "split_legion",
                        game.name,
                        legion.markerid,
                        new_markerid,
                        keep_names,
                        split_names,
                    )
                    def1.addErrback(self.failure)
                    return

        # No splits, so move on to the next phase.
        def1 = self.user.callRemote("done_with_splits", game.name)  # type: ignore
        def1.addErrback(self.failure)

    def move_legions(self, game: Game.Game) -> None:
        """Move one or more legions, and then end the Move phase."""
        logging.debug("")
        player = game.active_player
        assert player is not None
        if player.name != self.playername:
            logging.info("not active player; aborting")
            return
        assert player.movement_roll is not None
        non_moves = {}  # markerid: score
        while True:
            # Score moves
            # (score, legion, hexlabel, entry_side)
            best_moves = []
            for legion in player.unmoved_legions:
                moves = game.find_all_moves(
                    legion,
                    game.board.hexes[legion.hexlabel],
                    player.movement_roll,
                )
                logging.debug(f"legion {legion} moves {moves}")
                for hexlabel, entry_side in moves:
                    score = self._score_move(legion, hexlabel, True)
                    best_moves.append((score, legion, hexlabel, entry_side))
            # Entry sides are a mix of str and int, so stringify them
            best_moves.sort(
                key=lambda move: (move[0], move[1], move[2], str(move[3]))
            )
            logging.debug(f"{best_moves=}")
            if not best_moves:
                logging.debug("dumping all legions")
                for legion in game.all_legions():
                    logging.debug(legion)

            if player.can_take_mulligan:
                legions_with_good_moves = set()
                for (score, legion, _, _) in best_moves:
                    if score > 0:
                        legions_with_good_moves.add(legion)
                if len(legions_with_good_moves) < 2:
                    logging.info("taking a mulligan")
                    def1 = self.user.callRemote("take_mulligan", game.name)  # type: ignore
                    def1.addErrback(self.failure)
                    return

            # Score non-moves
            # (score, legion, hexlabel, None)
            # Entry side None means not a move.
            for legion in player.unmoved_legions:
                score = self._score_move(legion, legion.hexlabel, False)
                non_moves[legion.markerid] = score
            logging.debug(f"non_moves {non_moves}")

            while best_moves:
                score, legion, hexlabel, entry_side = best_moves.pop()
                non_move_score = non_moves[legion.markerid]
                if (
                    score > non_move_score
                    or not player.moved_legions
                    or len(player.friendly_legions(legion.hexlabel)) >= 2
                ):
                    teleporting_lord = None  # type: Optional[str]
                    if entry_side == Game.TELEPORT:
                        teleport = True
                        masterhex = game.board.hexes[hexlabel]
                        terrain = masterhex.terrain
                        if terrain == "Tower":
                            entry_side = 5
                        else:
                            entry_side = random.choice([1, 3, 5])
                        teleporting_lord = sorted(legion.lord_types)[-1]
                    else:
                        teleport = False
                    def1 = self.user.callRemote(  # type: ignore
                        "move_legion",
                        game.name,
                        legion.markerid,
                        hexlabel,
                        entry_side,
                        teleport,
                        teleporting_lord,
                    )
                    def1.addErrback(self.failure)
                    return

            # No more legions will move.
            logging.debug("done_with_moves")
            def1 = self.user.callRemote("done_with_moves", game.name)  # type: ignore
            def1.addErrback(self.failure)
            return

    def _score_move(
        self, legion: Legion.Legion, hexlabel: int, moved: bool
    ) -> float:
        """Return a score for legion moving to (or staying in) hexlabel."""
        score = 0.0
        player = legion.player
        game = player.game
        caretaker = game.caretaker
        board = game.board
        enemies = player.enemy_legions(hexlabel)
        legion_combat_value = legion.combat_value
        legion_sort_value = legion.sort_value

        if enemies:
            assert len(enemies) == 1
            enemy = enemies.pop()
            enemy_combat_value = enemy.terrain_combat_value
            logging.debug(f"legion {legion} hexlabel {hexlabel}")
            logging.debug(f"legion_combat_value {legion_combat_value}")
            logging.debug(f"enemy_combat_value {enemy_combat_value}")
            if enemy_combat_value < self.bp.SQUASH * legion_combat_value:  # type: ignore
                score += enemy.score
            elif (
                enemy_combat_value >= self.bp.BE_SQUASHED * legion_combat_value  # type: ignore
            ):
                score -= legion_sort_value
        if moved and (len(legion) < 7 or enemies):
            masterhex = board.hexes[hexlabel]
            terrain = masterhex.terrain
            recruits = legion.available_recruits(terrain, caretaker)
            if recruits:
                recruit_name = recruits[-1]
                recruit = Creature.Creature(recruit_name)
                # Only give credit for recruiting if we're likely to live.
                if not enemies or enemy_combat_value < legion_combat_value:
                    recruit_value = recruit.sort_value
                elif (
                    enemy_combat_value
                    < self.bp.BE_SQUASHED * legion_combat_value  # type: ignore
                ):
                    recruit_value = 0.5 * recruit.sort_value
                logging.debug(
                    f"recruit value {legion.markerid} {hexlabel} "
                    f"{recruit_value}"
                )
                score += recruit_value
        if game.turn > 1:
            # Do not fear enemy legions on turn 1.  8-high legions will be
            # forced to split, and hanging around in the tower to avoid getting
            # attacked 5-on-4 is too passive.
            try:
                previous_hexlabel = legion.hexlabel
                legion.hexlabel = hexlabel
                for enemy in player.enemy_legions():
                    if (
                        enemy.terrain_combat_value
                        >= self.bp.BE_SQUASHED * legion_combat_value  # type: ignore
                    ):
                        for roll in range(1, 6 + 1):
                            moves = game.find_normal_moves(
                                enemy, game.board.hexes[enemy.hexlabel], roll
                            ).union(game.find_titan_teleport_moves(enemy))
                            hexlabels = {move[0] for move in moves}
                            if hexlabel in hexlabels:
                                score -= legion_sort_value / 6.0
            finally:
                legion.hexlabel = previous_hexlabel
        return score

    def _gen_legion_moves_inner(
        self, movesets: List[Set[str]]
    ) -> Generator[Tuple, None, None]:
        """Yield tuples of distinct hexlabels, one from each moveset, in order,
        with no duplicates.

        movesets is a list of sets of hexlabels, corresponding to the order of
        remaining creatures in the legion.
        """
        if not movesets:
            yield ()
        elif len(movesets) == 1:
            for move in movesets[0]:
                yield (move,)
        else:
            for move in movesets[0]:
                movesets1 = copy.deepcopy(movesets[1:])
                for moveset in movesets1:
                    moveset.discard(move)
                for moves in self._gen_legion_moves_inner(movesets1):
                    yield (move,) + moves

    def _gen_legion_moves(
        self, movesets: List[Set[str]]
    ) -> Generator[List[str], None, None]:
        """Yield all possible legion_moves for movesets.

        movesets is a list of sets of hexlabels to which each Creature can move
        (or stay), in the same order as Legion.sorted_creatures.  Like:
        creatures [titan1, ogre1, troll1]
        movesets [{"A1", "A2", "B1"}, {"B1", "B2"}, {"B1", "B3"}]

        A legion_move is a list of hexlabels, in the same order as creatures,
        where each Creature's hexlabel is one from its original list, and no
        two Creatures have the same hexlabel.  Like:
        ["A1", "B1", "B3"]
        """
        logging.info(f"_gen_legion_moves {movesets}")
        for moves in self._gen_legion_moves_inner(movesets):
            if len(moves) == len(movesets):
                yield list(moves)

    def _gen_fallback_legion_moves(
        self, movesets: List[Set[str]]
    ) -> Generator[List[str], None, None]:
        """Yield all possible legion_moves for movesets, possibly including
        some missing moves in the case where not all creatures can get onboard.

        movesets is a list of sets of hexlabels to which each Creature can move
        (or stay), in the same order as Legion.sorted_creatures.  Like:
        creatures [titan1, ogre1, troll1]
        movesets [{"A1", "A2", "B1"}, {"B1", "B2"}, {"B1", "B3"}]

        A legion_move is a list of hexlabels, in the same order as creatures,
        where each Creature's hexlabel is one from its original list, and no
        two Creatures have the same hexlabel.  Like:
        ["A1", "B1", "B3"]
        """
        logging.info(movesets)
        for moves in self._gen_legion_moves_inner(movesets):
            yield list(moves)

    def _score_perm(
        self,
        game: Game.Game,
        sort_values: Dict[str, float],
        perm: Iterable[Tuple[str, str, str]],
    ) -> float:
        """Score one move order permutation."""
        score = 0.0
        moved_creatures = set()
        try:
            for (creature_name, start, move) in perm:
                creature = game.creatures_in_battle_hex(
                    start, creature_name
                ).pop()
                if move == start or move in game.find_battle_moves(creature):
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = move
                    moved_creatures.add(creature)
                    score += sort_values[creature_name]
            return score
        finally:
            for creature in moved_creatures:
                creature.hexlabel = creature.previous_hexlabel
                creature.previous_hexlabel = None

    def _find_move_order(
        self, game: Game.Game, creature_moves: List[Tuple[str, str, str]]
    ) -> List[Tuple[str, str, str]]:
        """Return a new list with creature_moves rearranged so that as
        many of the moves as possible can be legally made.

        creature_moves is a list of (creature_name, start_hexlabel,
        finish_hexlabel) tuples.
        """
        max_score = 0.0
        sort_values = {}
        for creature_name, start, move in creature_moves:
            creature = game.creatures_in_battle_hex(start, creature_name).pop()
            sort_values[creature_name] = creature.sort_value
            max_score += creature.sort_value
        perms = list(
            itertools.permutations(creature_moves)
        )  # type: List[Iterable[Tuple[str, str, str]]]
        logging.info(f"{len(perms)} perms")
        # Scramble the list so we don't get a bunch of similar bad
        # orders jumbled together at the beginning.
        random.shuffle(perms)
        best_score = float(-maxsize)
        best_perm = perms[0]
        finish_time = time.time() + self.ai_time_limit
        for perm in perms:
            score = self._score_perm(game, sort_values, perm)
            if score == max_score:
                best_perm = perm
                logging.info("found perfect order")
                break
            elif score > best_score:
                best_perm = perm
                best_score = score
            if time.time() > finish_time:
                logging.info("time limit")
                break
        logging.info(f"returning {list(best_perm)}")
        return list(best_perm)

    def _find_best_creature_moves(
        self, game: Game.Game
    ) -> Optional[List[Tuple[str, str, str]]]:
        """Return a list of up to one (creature_name, start_hexlabel,
        finish_hexlabel) tuple for each Creature in the battle active legion.

        Idea: Find all possible moves for each creature in the legion,
        ignoring mobile allies, and score them in isolation without knowing
        where its allies will end up.  Find the best 7 moves for each creature
        (because with up to 7 creatures in a legion, a creature may have to
        take its 7th-favorite move, and because 7! = 5040, not too big).
        Combine these into legion moves, and score those again, then take
        the best legion move.  Finally, find the order of creature moves
        that lets all the creatures reach their assigned hexes without
        blocking their allies' moves.
        """
        if (
            game.battle_active_player is None
            or game.battle_active_player.name != self.playername
        ):
            return None
        legion = game.battle_active_legion
        assert legion is not None
        logging.info(f"{legion=}")
        creatures = legion.sorted_living_creatures
        if not creatures:
            return None
        movesets = []  # list of a set of hexlabels for each creature
        previous_creature = None
        moveset = None
        for creature in creatures:
            assert creature.hexlabel is not None
            if (
                previous_creature
                and creature.name == previous_creature.name
                and creature.hexlabel == previous_creature.hexlabel
            ):
                # Reuse previous moveset
                moveset = copy.deepcopy(moveset)
            else:
                moves = game.find_battle_moves(
                    creature, ignore_mobile_allies=True
                )
                if moves:
                    score_moves = []
                    # Not moving is also an option, unless offboard.
                    if creature.hexlabel not in {"ATTACKER", "DEFENDER"}:
                        moves.add(creature.hexlabel)
                    for move in moves:
                        try:
                            creature.previous_hexlabel = creature.hexlabel
                            creature.hexlabel = move
                            score = self._score_legion_move(game, [creature])
                            score_moves.append((score, move))
                        finally:
                            creature.hexlabel = creature.previous_hexlabel
                    score_moves.sort()
                    logging.info(f"{creature=} {score_moves=}")
                    moveset = best7(score_moves)
                else:
                    moveset = {creature.hexlabel}
            movesets.append(moveset)
            previous_creature = creature
        now = time.time()
        legion_moves = list(self._gen_legion_moves(movesets))
        logging.info(
            f"found {len(legion_moves)} legion_moves in {time.time() - now}"
        )
        if not legion_moves:
            legion_moves = list(self._gen_fallback_legion_moves(movesets))
            if not legion_moves:
                return None
        start_time = time.time()
        finish_time = start_time + self.ai_time_limit
        # Scramble the moves, in case we don't have time to look at them all.
        random.shuffle(legion_moves)
        best_legion_move = legion_moves[0]
        best_score = float(-maxsize)
        lc = len(creatures)
        llm0 = len(legion_moves[0])
        logging.info(f"len(creatures) = {lc} len(legion_moves[0]) = {llm0}")
        for legion_move in legion_moves:
            try:
                for ii, creature in enumerate(creatures):
                    move = legion_move[ii]
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = move
                score = self._score_legion_move(game, creatures)
                if score > best_score:
                    best_legion_move = legion_move
                    best_score = score
                now = time.time()
                if now > finish_time:
                    logging.info("time limit")
                    break
            finally:
                for creature in creatures:
                    creature.hexlabel = creature.previous_hexlabel
        logging.info(
            f"found best_legion_move {best_legion_move} in {now - start_time}"
        )
        for creature in creatures:
            assert creature.hexlabel is not None
        start_hexlabels = [creature.hexlabel for creature in creatures]
        creature_names = [creature.name for creature in creatures]
        assert (
            len(creature_names)
            == len(start_hexlabels)
            == len(best_legion_move)
        )
        creature_moves = list(
            zip(creature_names, start_hexlabels, best_legion_move)
        )
        logging.info(f"creature_moves {creature_moves}")
        now = time.time()
        ordered_creature_moves = self._find_move_order(game, creature_moves)  # type: ignore
        logging.info(
            f"found ordered_creature_moves {ordered_creature_moves} in "
            f"{time.time() - now}"
        )
        return ordered_creature_moves

    def move_creatures(self, game: Game.Game) -> None:
        """Move all creatures in the legion.

        Idea: Find all possible moves for each creature in the legion,
        ignoring mobile allies, and score them in isolation without knowing
        where its allies will end up.  Find the best 7 moves for each creature
        (because with up to 7 creatures in a legion, a creature may have to
        take its 7th-favorite move, and because 7 ** 7 = 823543, not too big).
        Combine these into legion moves, and score those again, then take
        the best legion move.  Finally, find the order of creature moves
        that lets all the creatures reach their assigned hexes without
        blocking their allies' moves.
        """
        logging.info("")
        if self.best_creature_moves is None:
            self.best_creature_moves = self._find_best_creature_moves(game)
        # Loop in case a non-move is best.
        while self.best_creature_moves:
            (creature_name, start, finish) = self.best_creature_moves.pop(0)
            logging.info(f"checking move {creature_name} {start} {finish}")
            creatures = game.creatures_in_battle_hex(start, creature_name)
            if creatures:
                creature = creatures.pop()
            else:
                logging.info("best_creature_moves was broken")
                self.best_creature_moves = self._find_best_creature_moves(game)
                continue
            if finish != start and finish in game.find_battle_moves(creature):
                logging.info(
                    f"calling move_creature {creature.name} {start} {finish}"
                )
                def1 = self.user.callRemote(  # type: ignore
                    "move_creature", game.name, creature.name, start, finish
                )
                def1.addErrback(self.failure)
                return

        # No moves, so end the maneuver phase.
        logging.info("calling done_with_maneuvers")
        self.best_creature_moves = None
        def1 = self.user.callRemote("done_with_maneuvers", game.name)  # type: ignore
        def1.addErrback(self.failure)

    def _score_legion_move(
        self, game: Game.Game, creatures: List[Creature.Creature]
    ) -> float:
        """Return a score for creatures in their current hexlabels."""
        assert game.battle_turn is not None
        score = 0
        battlemap = game.battlemap
        assert battlemap is not None
        legion = creatures[0].legion
        assert legion is not None
        legion2 = game.other_battle_legion(legion)
        assert legion2 is not None

        # For each enemy, figure out the average damage we could do to it if
        # everyone concentrated on hitting it, and if that's enough to kill it,
        # give every creature a kill bonus.
        # (This is not quite right because each creature can only hit one enemy
        # (ignoring carries), but it's a start.)
        kill_bonus = 0.0
        for enemy in legion2.creatures:
            total_mean_hits = 0.0
            for creature in creatures:
                if enemy in creature.engaged_enemies or (
                    not creature.engaged
                    and enemy in creature.rangestrike_targets
                ):
                    dice = creature.number_of_dice(enemy)
                    strike_number = creature.strike_number(enemy)
                    mean_hits = dice * (7.0 - strike_number) / 6
                    total_mean_hits += mean_hits
            if total_mean_hits >= enemy.hits_left:
                kill_bonus += enemy.sort_value

        for creature in creatures:
            assert creature.hexlabel is not None
            can_rangestrike = False
            engaged = creature.engaged_enemies
            max_mean_hits = 0.0
            total_mean_damage_taken = 0.0
            engaged_with_rangestriker = False
            # melee
            for enemy in engaged:
                # Damage we can do.
                dice = creature.number_of_dice(enemy)
                strike_number = creature.strike_number(enemy)
                mean_hits = dice * (7.0 - strike_number) / 6
                max_mean_hits = max(mean_hits, max_mean_hits)
                # Damage we can take.
                dice = enemy.number_of_dice(creature)
                strike_number = enemy.strike_number(creature)
                mean_hits = dice * (7.0 - strike_number) / 6
                total_mean_damage_taken += mean_hits
                if enemy.rangestrikes:
                    engaged_with_rangestriker = True
            # inbound rangestriking
            for enemy in legion2.creatures:
                if enemy not in engaged:
                    if creature in enemy.potential_rangestrike_targets:
                        dice = enemy.number_of_dice(creature)
                        strike_number = enemy.strike_number(creature)
                        mean_hits = dice * (7.0 - strike_number) / 6
                        total_mean_damage_taken += mean_hits
            probable_death = total_mean_damage_taken >= creature.hits_left

            if engaged_with_rangestriker and not creature.rangestrikes:
                score += self.bp.ENGAGE_RANGESTRIKER_BONUS  # type: ignore

            # rangestriking
            if not engaged:
                targets = creature.rangestrike_targets
                for enemy in targets:
                    # Damage we can do
                    dice = creature.number_of_dice(enemy)
                    strike_number = creature.strike_number(enemy)
                    mean_hits = dice * (7.0 - strike_number) / 6
                    max_mean_hits = max(mean_hits, max_mean_hits)
                    can_rangestrike = True
            if can_rangestrike:
                score += self.bp.RANGESTRIKE_BONUS  # type: ignore

            # Don't encourage titans to charge early.
            if (
                creature.name != "Titan"
                or game.battle_turn >= 4
                or len(legion) == 1
            ):
                if max_mean_hits:
                    bonus = self.bp.HIT_BONUS * max_mean_hits  # type: ignore
                    score += bonus
                if kill_bonus:
                    bonus = self.bp.KILL_MULTIPLIER * kill_bonus  # type: ignore
                    score += bonus
            if total_mean_damage_taken:
                penalty = self.bp.DAMAGE_PENALTY * total_mean_damage_taken  # type: ignore
                score += penalty
            if probable_death:
                penalty = (
                    self.bp.DEATH_MULTIPLIER  # type: ignore
                    * probable_death
                    * creature.sort_value
                )
                score += penalty

            # Attacker must attack to avoid time loss
            # Don't encourage titans to charge early.
            if legion == game.attacker_legion and (
                creature.name != "Titan"
                or game.battle_turn >= 4
                or len(legion) == 1
            ):
                if engaged or targets:
                    score += self.bp.ATTACKER_AGGRESSION_BONUS  # type: ignore
                else:
                    enemy_hexlabels = [
                        enemy.hexlabel
                        for enemy in legion2.living_creatures
                        if enemy.hexlabel is not None
                    ]
                    if enemy_hexlabels:
                        min_range = min(
                            (
                                battlemap.range(
                                    creature.hexlabel, enemy_hexlabel
                                )
                                for enemy_hexlabel in enemy_hexlabels
                            )
                        )
                        penalty = min_range * self.bp.ATTACKER_DISTANCE_PENALTY  # type: ignore
                        score += penalty

            battlehex = battlemap.hexes[creature.hexlabel]
            terrain = battlehex.terrain

            # Make titans hang back early.
            if (
                creature.is_titan
                and game.battle_turn < 4
                and terrain != "Tower"
            ):
                if legion == game.attacker_legion:
                    entrance = "ATTACKER"
                else:
                    entrance = "DEFENDER"
                distance = (
                    battlemap.range(
                        creature.hexlabel, entrance, allow_entrance=True
                    )
                    - 2
                )
                penalty = distance * self.bp.TITAN_FORWARD_PENALTY  # type: ignore
                if penalty:
                    score += penalty

            # Make defenders hang back early.
            if (
                legion == game.defender_legion
                and game.battle_turn < 4
                and terrain != "Tower"
            ):
                entrance = "DEFENDER"
                distance = (
                    battlemap.range(
                        creature.hexlabel, entrance, allow_entrance=True
                    )
                    - 2
                )
                penalty = distance * self.bp.DEFENDER_FORWARD_PENALTY  # type: ignore
                if penalty:
                    score += penalty

            # terrain
            if battlehex.elevation:
                bonus = battlehex.elevation * self.bp.ELEVATION_BONUS  # type: ignore
                score += bonus
            if terrain == "Bramble":
                if creature.is_native(terrain):
                    score += self.bp.NATIVE_BRAMBLE_BONUS  # type: ignore
                else:
                    score += self.bp.NON_NATIVE_BRAMBLE_PENALTY  # type: ignore
            elif terrain == "Tower":
                # XXX Hardcoded to default Tower map
                score += self.bp.TOWER_BONUS  # type: ignore
                if battlehex.elevation == 2:
                    if creature.is_titan:
                        score += self.bp.TITAN_IN_CENTER_OF_TOWER_BONUS  # type: ignore
                    else:
                        score += self.bp.CENTER_OF_TOWER_BONUS  # type: ignore
                elif (
                    legion == game.defender_legion
                    and creature.name != "Titan"
                    and battlehex.label in ["C3", "D3"]
                ):
                    score += self.bp.FRONT_OF_TOWER_BONUS  # type: ignore
                elif (
                    legion == game.defender_legion
                    and creature.name != "Titan"
                    and battlehex.label in ["C4", "E3"]
                ):
                    score += self.bp.MIDDLE_OF_TOWER_BONUS  # type: ignore
            elif terrain == "Drift":
                if not creature.is_native(terrain):
                    score += self.bp.NON_NATIVE_DRIFT_PENALTY  # type: ignore
            elif terrain == "Volcano":
                score += self.bp.NATIVE_VOLCANO_BONUS  # type: ignore

            if "Slope" in battlehex.borders:
                if creature.is_native("Slope"):
                    score += self.bp.NATIVE_SLOPE_BONUS  # type: ignore
                else:
                    score += self.bp.NON_NATIVE_SLOPE_PENALTY  # type: ignore
            if "Dune" in battlehex.borders:
                if creature.is_native("Dune"):
                    score += self.bp.NATIVE_DUNE_BONUS  # type: ignore
                else:
                    score += self.bp.NON_NATIVE_DUNE_PENALTY  # type: ignore

            # allies
            num_adjacent_allies = 0
            for neighbor in battlehex.neighbors.values():
                for ally in legion.living_creatures:
                    if ally.hexlabel == neighbor.label:
                        num_adjacent_allies += 1
            adjacent_allies_bonus = (
                num_adjacent_allies * self.bp.ADJACENT_ALLY_BONUS  # type: ignore
            )
            if adjacent_allies_bonus:
                score += adjacent_allies_bonus

        return score

    def strike(self, game: Game.Game) -> None:
        logging.info("")
        if not game.battle_active_player:
            logging.info("called strike with no battle")
            return
        if game.battle_active_player.name != self.playername:
            logging.info("called strike for wrong player")
            return
        legion = game.battle_active_legion
        assert legion is not None
        # First do the strikers with only one target.
        for striker in legion.sorted_creatures:
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                if len(hexlabels) == 1:
                    hexlabel = hexlabels.pop()
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    num_dice = striker.number_of_dice(target)
                    strike_number = striker.strike_number(target)
                    def1 = self.user.callRemote(  # type: ignore
                        "strike",
                        game.name,
                        striker.name,
                        striker.hexlabel,
                        target.name,
                        target.hexlabel,
                        num_dice,
                        strike_number,
                    )
                    def1.addErrback(self.failure)
                    return

        # Then do the ones that have to choose a target.
        target_to_total_mean_hits = collections.defaultdict(
            float
        )  # type: DefaultDict[Creature.Creature, float]
        best_target = None
        for striker in legion.sorted_creatures:
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                for hexlabel in hexlabels:
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    num_dice = striker.number_of_dice(target)
                    strike_number = striker.strike_number(target)
                    mean_hits = num_dice * (7.0 - strike_number) / 6
                    target_to_total_mean_hits[target] += mean_hits
        # First find the best target we can kill.
        for target, total_mean_hits in target_to_total_mean_hits.items():
            if total_mean_hits >= target.hits_left:
                if (
                    best_target is None
                    or target.sort_value > best_target.sort_value
                ):
                    best_target = target
        # If we can't kill anything, go after the target we can hurt most.
        if best_target is None:
            max_total_mean_hits = 0.0
            for target, total_mean_hits in target_to_total_mean_hits.items():
                if total_mean_hits >= max_total_mean_hits:
                    best_target = target
                    max_total_mean_hits = total_mean_hits
        # Find the least valuable striker who can hit best_target.
        for striker in reversed(legion.sorted_creatures):
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                for hexlabel in hexlabels:
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    if target is best_target:
                        num_dice = striker.number_of_dice(target)
                        strike_number = striker.strike_number(target)
                        def1 = self.user.callRemote(  # type: ignore
                            "strike",
                            game.name,
                            striker.name,
                            striker.hexlabel,
                            target.name,
                            target.hexlabel,
                            num_dice,
                            strike_number,
                        )
                        def1.addErrback(self.failure)
                        return
        # No strikes, so end the strike phase.
        if game.battle_phase == Phase.STRIKE:
            def1 = self.user.callRemote("done_with_strikes", game.name)  # type: ignore
            def1.addErrback(self.failure)
        else:
            if game.battle_phase != Phase.COUNTERSTRIKE:
                logging.info("wrong phase")
            def1 = self.user.callRemote("done_with_counterstrikes", game.name)  # type: ignore
            def1.addErrback(self.failure)

    def carry(
        self,
        game: Game.Game,
        striker_name: str,
        striker_hexlabel: str,
        target_name: str,
        target_hexlabel: str,
        num_dice: int,
        strike_number: int,
        carries: int,
    ) -> None:
        striker = game.creatures_in_battle_hex(striker_hexlabel).pop()
        target = game.creatures_in_battle_hex(target_hexlabel).pop()
        carry_targets = []
        for creature in striker.engaged_enemies:
            if striker.can_carry_to(creature, target, num_dice, strike_number):
                carry_targets.append(creature)
        best_target = None
        # If there's only one carry target, it's easy.
        if len(carry_targets) == 1:
            best_target = carry_targets[0]
        # First find the best target we can kill.
        if best_target is None:
            for carry_target in carry_targets:
                if carries >= target.hits_left:
                    if (
                        best_target is None
                        or carry_target.sort_value > best_target.sort_value
                    ):
                        best_target = carry_target
        # If we can't kill anything then go after the hardest target to hit.
        if best_target is None:
            best_num_dice = maxsize
            best_strike_number = 0
            for carry_target in carry_targets:
                num_dice2 = striker.number_of_dice(carry_target)
                strike_number2 = striker.strike_number(carry_target)
                if (
                    best_target is None
                    or num_dice2 < best_num_dice
                    or strike_number2 > best_strike_number
                ):
                    best_target = carry_target
                    best_num_dice = num_dice2
                    best_strike_number = strike_number2
        assert best_target is not None
        def1 = self.user.callRemote(  # type: ignore
            "carry", game.name, best_target.name, best_target.hexlabel, carries
        )
        def1.addErrback(self.failure)

    def failure(self, error: Any) -> None:
        log.err(error)  # type: ignore
