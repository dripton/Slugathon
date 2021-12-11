from __future__ import annotations
import logging
from typing import Dict, List, Optional, Set

from twisted.internet import reactor

from slugathon.util.Observed import Observed
from slugathon.game import Action, Creature, Game, Legion, Phase
from slugathon.data import playercolordata, creaturedata, markerdata
from slugathon.util.bag import bag
from slugathon.util import Dice


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


class Player(Observed):

    """A person or AI who is (or was) actively playing in a game.

    Note that players are distinct from users.  A user could be just chatting
    or observing, not playing.  A user could be playing in more than one game,
    or could be controlling more than one player in a game.  (Server owners
    might disallow these scenarios to prevent cheating or encourage quick play,
    but that's policy not mechanism, and our mechanisms should be flexible
    enough to handle these cases.)  A user might drop his connection, and
    another user might take over his player can continue the game.
    """

    def __init__(
        self,
        playername: str,
        game: Game.Game,
        join_order: int,
        player_class: str = "Human",
        player_info: str = "",
    ):
        logging.info(
            f"{playername} {game} {join_order} {player_class} {player_info}"
        )
        Observed.__init__(self)
        self.name = playername
        self.player_class = player_class
        self.player_info = player_info or playername
        self.game = game
        self.join_order = join_order
        self.starting_tower = None  # type: Optional[int]
        self.created_starting_legion = False
        self.score = 0
        self.color = None  # type: Optional[str]
        # Currently available markers
        self.markerids_left = set()  # type: Set[str]
        # Private to this instance; not shown to others until a
        # legion is actually split off with this marker.
        self.selected_markerid = None  # type: Optional[str]
        self.markerid_to_legion = {}  # type: Dict[str, Legion.Legion]
        self.mulligans_left = 1
        self.movement_roll = None  # type: Optional[int]
        self.summoned = False
        self.eliminated_colors = set()  # type: Set[str]
        self.last_donor = None  # type: Optional[Legion.Legion]
        self.has_titan = True

    @property
    def legions(self) -> List[Legion.Legion]:
        return list(self.markerid_to_legion.values())

    @property
    def sorted_legions(self) -> List[Legion.Legion]:
        """Return a list of this player's legions in descending order
        of importance."""
        value_legions = [
            (legion.sort_value, legion) for legion in self.legions
        ]
        value_legions.sort()
        value_legions.reverse()
        return [legion for (value, legion) in value_legions]

    @property
    def dead(self) -> bool:
        return self.created_starting_legion and not self.markerid_to_legion

    @property
    def teleported(self) -> bool:
        """Return True iff any of this player's legions have teleported
        this turn."""
        for legion in self.legions:
            if legion.teleported:
                return True
        return False

    @property
    def color_abbrev(self) -> Optional[str]:
        if self.color is None:
            return None
        return playercolordata.name_to_abbrev.get(self.color)

    def __repr__(self) -> str:
        return "Player " + self.name

    def assign_starting_tower(self, tower: int) -> None:
        """Set this player's starting tower to the tower"""
        assert isinstance(tower, int)
        self.starting_tower = tower
        action = Action.AssignTower(self.game.name, self.name, tower)
        self.notify(action)

    def assign_color(self, color: str) -> None:
        """Set this player's color"""
        self.color = color
        abbrev = self.color_abbrev
        num_markers = len(markerdata.data[color])
        for ii in range(num_markers):
            self.markerids_left.add(f"{abbrev}{(ii + 1):02d}")
        logging.info(self.markerids_left)
        action = Action.PickedColor(self.game.name, self.name, color)
        self.notify(action)

    def pick_marker(self, markerid: str) -> None:
        if markerid not in self.markerids_left:
            logging.info("pick_marker with bad marker")
            return
        self.selected_markerid = markerid

    def take_marker(self, markerid: str) -> str:
        if markerid not in self.markerids_left:
            raise AssertionError("take_marker with bad marker")
        self.markerids_left.remove(markerid)
        self.selected_markerid = None
        return markerid

    def create_starting_legion(self) -> None:
        markerid = self.selected_markerid
        if markerid is None:
            raise AssertionError("create_starting_legion without marker")
        if markerid not in self.markerids_left:
            raise AssertionError("create_starting_legion with bad marker")
        if self.markerid_to_legion:
            raise AssertionError("create_starting_legion but have a legion")
        creatures = [
            Creature.Creature(name)
            for name in creaturedata.starting_creature_names
        ]
        assert self.starting_tower is not None
        legion = Legion.Legion(
            self, self.take_marker(markerid), creatures, self.starting_tower
        )
        self.markerid_to_legion[markerid] = legion
        legion.add_observer(self.game)
        action = Action.CreateStartingLegion(
            self.game.name, self.name, markerid
        )
        caretaker = self.game.caretaker
        for creature in creatures:
            caretaker.take_one(creature.name)
        self.created_starting_legion = True
        self.notify(action)

    @property
    def can_split(self) -> bool:
        """Return True if this player can split any legions."""
        if self.markerids_left:
            if self.game.turn == 1:
                return len(self.legions) == 1
            for legion in self.legions:
                if len(legion) >= 4:
                    return True
        return False

    def split_legion(
        self,
        parent_markerid: str,
        child_markerid: str,
        parent_creature_names: List[str],
        child_creature_names: List[str],
    ) -> None:
        logging.info(
            f"{parent_markerid} {child_markerid} {parent_creature_names} "
            f"{child_creature_names}"
        )
        parent = self.markerid_to_legion.get(parent_markerid)
        if parent is None:
            return
        if child_markerid not in self.markerids_left:
            raise AssertionError("illegal marker")
        if bag(parent.creature_names) != bag(parent_creature_names).union(
            bag(child_creature_names)
        ) and bag(parent_creature_names).union(
            bag(child_creature_names)
        ) != bag(
            {"Unknown": len(parent)}
        ):
            raise AssertionError(
                "wrong creatures",
                "parent.creature_names",
                parent.creature_names,
                "parent_creature_names",
                parent_creature_names,
                "child_creature_names",
                child_creature_names,
            )
        new_legion1 = Legion.Legion(
            self,
            parent_markerid,
            Creature.n2c(parent_creature_names),
            parent.hexlabel,
        )
        new_legion2 = Legion.Legion(
            self,
            child_markerid,
            Creature.n2c(child_creature_names),
            parent.hexlabel,
        )
        if not parent.is_legal_split(new_legion1, new_legion2):
            raise AssertionError("illegal split")
        del new_legion1
        parent.creatures = Creature.n2c(parent_creature_names)
        for creature in parent.creatures:
            creature.legion = parent
        self.take_marker(child_markerid)
        new_legion2.add_observer(self.game)
        self.markerid_to_legion[child_markerid] = new_legion2
        del parent
        # One action for our player with creature names
        action = Action.SplitLegion(
            self.game.name,
            self.name,
            parent_markerid,
            child_markerid,
            parent_creature_names,
            child_creature_names,
        )
        logging.info(action)
        self.notify(action, names=[self.name])
        # Another action for everyone (including our player, who will
        # ignore it as a duplicate) without creature names.
        action = Action.SplitLegion(
            self.game.name,
            self.name,
            parent_markerid,
            child_markerid,
            len(parent_creature_names) * ["Unknown"],
            len(child_creature_names) * ["Unknown"],
        )
        logging.info(action)
        self.notify(action)

    def undo_split(self, parent_markerid: str, child_markerid: str) -> None:
        parent = self.markerid_to_legion.get(parent_markerid)
        if parent is None:
            return
        child = self.markerid_to_legion.get(child_markerid)
        if child is None:
            return
        parent_creature_names = parent.creature_names
        child_creature_names = child.creature_names
        parent.creatures += child.creatures
        child.remove_observer(self)
        del self.markerid_to_legion[child_markerid]
        self.markerids_left.add(child.markerid)
        self.selected_markerid = None
        del child
        # One action for our player with creature names, and a
        # different action for other players without.
        action = Action.UndoSplit(
            self.game.name,
            self.name,
            parent_markerid,
            child_markerid,
            parent_creature_names,
            child_creature_names,
        )
        self.notify(action, names=[self.name])
        action = Action.UndoSplit(
            self.game.name,
            self.name,
            parent_markerid,
            child_markerid,
            len(parent_creature_names) * ["Unknown"],
            len(child_creature_names) * ["Unknown"],
        )
        other_playernames = self.game.playernames
        other_playernames.remove(self.name)
        self.notify(action, names=other_playernames)

    @property
    def can_exit_split_phase(self) -> bool:
        """Return True if legal to exit the split phase"""
        if self.game.phase != Phase.SPLIT:
            return False
        if self.dead:
            return True
        return bool(
            self.markerid_to_legion
            and max((len(legion) for legion in self.legions)) < 8
        )

    def _roll_movement(self) -> None:
        self.movement_roll = Dice.roll()[0]
        action = Action.RollMovement(
            self.game.name, self.name, self.movement_roll, self.mulligans_left
        )
        self.notify(action)

    def done_with_splits(self) -> None:
        if self.can_exit_split_phase:
            self._roll_movement()

    @property
    def can_take_mulligan(self) -> bool:
        """Return True iff this player can take a mulligan"""
        return bool(
            self is self.game.active_player
            and self.game.turn == 1
            and self.game.phase == Phase.MOVE
            and self.mulligans_left
        )

    def take_mulligan(self) -> None:
        self.mulligans_left -= 1
        self._roll_movement()

    @property
    def can_titan_teleport(self) -> bool:
        return self.score >= 400

    @property
    def titan_power(self) -> int:
        return 6 + self.score // 100

    @property
    def num_creatures(self) -> int:
        return sum(len(legion) for legion in self.legions)

    @property
    def moved_legions(self) -> Set[Legion.Legion]:
        """Return a set of this players legions that have moved this turn."""
        return {legion for legion in self.legions if legion.moved}

    @property
    def unmoved_legions(self) -> Set[Legion.Legion]:
        """Return a set of this players legions that have not moved."""
        return {legion for legion in self.legions if not legion.moved}

    def friendly_legions(
        self, hexlabel: Optional[int] = None
    ) -> Set[Legion.Legion]:
        """Return a set of this player's legions, in hexlabel if not None."""
        return set(
            [
                legion
                for legion in self.legions
                if hexlabel in (None, legion.hexlabel)
            ]
        )

    def enemy_legions(
        self, hexlabel: Optional[int] = None
    ) -> Set[Legion.Legion]:
        """Return a set of other players' legions, in hexlabel if not None."""
        return set(
            [
                legion
                for legion in self.game.all_legions(hexlabel)
                if legion.player is not self
            ]
        )

    @property
    def can_exit_move_phase(self) -> bool:
        """Return True iff this player can finish the move phase."""
        if self.game.phase != Phase.MOVE:
            return False
        if self.dead:
            return True
        if not self.moved_legions:
            return False
        assert self.movement_roll is not None
        for legion in self.friendly_legions():
            if len(self.friendly_legions(legion.hexlabel)) >= 2:
                if not legion.moved and self.game.find_all_moves(
                    legion,
                    self.game.board.hexes[legion.hexlabel],
                    self.movement_roll,
                ):
                    return False
                # else will need to recombine
        return True

    def recombine(self) -> None:
        """Recombine split legions as necessary."""
        while True:
            for legion in self.friendly_legions():
                legions_in_hex = list(self.friendly_legions(legion.hexlabel))
                if len(legions_in_hex) >= 2:
                    split_action = self.game.history.find_last_split(
                        self.name,
                        legions_in_hex[0].markerid,
                        legions_in_hex[1].markerid,
                    )
                    if split_action is not None:
                        parent_markerid = split_action.parent_markerid
                        child_markerid = split_action.child_markerid
                    else:
                        parent_markerid = legions_in_hex[0].markerid
                        child_markerid = legions_in_hex[1].markerid
                    self.undo_split(parent_markerid, child_markerid)
                    # TODO Add an UndoSplit action to history?
                    break
            else:
                return

    def done_with_moves(self) -> None:
        logging.debug("")
        if self.can_exit_move_phase:
            self.recombine()
            action = Action.StartFightPhase(self.game.name, self.name)
            self.notify(action)
        else:
            logging.warning(f"{self} cannot exit move phase")

    @property
    def can_exit_fight_phase(self) -> bool:
        """Return True iff this player can finish the fight phase."""
        if self.game.phase != Phase.FIGHT:
            return False
        logging.info(
            f"can_exit_fight_phase {self.game.engagement_hexlabels=} "
            f"{self.game.pending_summon=} {self.game.pending_reinforcement=} "
            f"{self.pending_acquire=}"
        )
        return (
            not self.game.engagement_hexlabels
            and not self.game.pending_summon
            and not self.game.pending_reinforcement
            and not self.game.pending_acquire
        )

    @property
    def pending_acquire(self) -> bool:
        for legion in self.legions:
            if legion.angels_pending or legion.archangels_pending:
                return True
        return False

    def reset_angels_pending(self) -> None:
        for legion in self.legions:
            legion.reset_angels_pending()

    def remove_empty_legions(self) -> None:
        """Remove any legions with no creatures, caused by summoning out
        the only creature in the legion."""
        for legion in self.legions:
            if not legion.creatures:
                self.remove_legion(legion.markerid)

    def done_with_engagements(self) -> None:
        logging.info("Player.done_with_engagements")
        if self.can_exit_fight_phase:
            logging.info("can exit fight phase")
            action = Action.StartMusterPhase(self.game.name, self.name)
            self.notify(action)

    @property
    def can_recruit(self) -> bool:
        """Return True if any of this player's legions can recruit."""
        for legion in self.legions:
            if legion.moved and legion.can_recruit:
                return True
        return False

    @property
    def has_forced_strikes(self) -> bool:
        if self.game.battle_active_legion is None:
            return False
        for creature in self.game.battle_active_legion.creatures:
            if creature.engaged and not creature.struck:
                return True
        return False

    def done_with_battle_phase(self) -> None:
        """Finish whatever battle phase it currently is."""
        if self.game.battle_phase == Phase.REINFORCE:
            self.done_with_reinforcements()
        elif self.game.battle_phase == Phase.MANEUVER:
            self.done_with_maneuvers()
        elif self.game.battle_phase == Phase.STRIKE:
            self.done_with_strikes()
        elif self.game.battle_phase == Phase.COUNTERSTRIKE:
            self.done_with_counterstrikes()

    def done_with_recruits(self) -> None:
        if self.game.active_player != self or self.game.phase != Phase.MUSTER:
            logging.info("illegal call to done_with_recruits")
            return
        (player, turn) = self.game.next_player_and_turn
        if player is not None:
            action = Action.StartSplitPhase(self.game.name, player.name, turn)
            self.notify(action)

    def done_with_reinforcements(self) -> None:
        action = Action.StartManeuverBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_maneuvers(self) -> None:
        action = Action.StartStrikeBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_strikes(self) -> None:
        if self.has_forced_strikes:
            logging.info(f"{self} Forced strikes remain")
            return
        player = self
        for legion in self.game.battle_legions:
            if legion.player != self:
                player = legion.player
        assert player is not self
        action = Action.StartCounterstrikeBattlePhase(
            self.game.name, player.name
        )
        self.notify(action)

    def done_with_counterstrikes(self) -> None:
        if self.has_forced_strikes:
            logging.info(f"{self} Forced strikes remain")
            return
        action = Action.StartReinforceBattlePhase(
            self.game.name, self.name, self.game.battle_turn
        )
        self.notify(action)

    @property
    def all_summonables(self) -> List[Creature.Creature]:
        """Return a list of all this Player's Creatures that are summonable."""
        summonables = []
        for legion in self.legions:
            if not legion.engaged:
                for creature in legion.creatures:
                    if creature.summonable:
                        summonables.append(creature)
        return summonables

    def summon_angel(
        self, legion: Legion.Legion, donor: Legion.Legion, creature_name: str
    ) -> None:
        """Summon an angel from donor to legion."""
        logging.info(f"Player.summon_angel {legion} {donor} {creature_name}")
        assert not self.summoned, "player tried to summon twice"
        assert len(legion) < 7, "legion too tall to summon"
        donor.reveal_creatures([creature_name])
        donor.remove_creature_by_name(creature_name)
        legion.add_creature_by_name(creature_name)
        creature = legion.creatures[-1]
        creature.legion = legion
        self.summoned = True
        self.last_donor = donor

    def unsummon_angel(
        self, legion: Legion.Legion, creature_name: str
    ) -> None:
        donor = self.last_donor
        # Avoid doing it twice.
        if not self.summoned or donor is None or len(donor) >= 7:
            return
        # Can be done during battle, so it matters which of this creature.
        if not legion.creatures or legion.creatures[-1].name != creature_name:
            return
        legion.creatures.pop()
        donor.add_creature_by_name(creature_name)
        creature = donor.creatures[-1]
        creature.legion = donor
        self.summoned = False
        self.last_donor = None
        action = Action.UnsummonAngel(
            self.game.name,
            self.name,
            legion.markerid,
            donor.markerid,
            creature.name,
        )
        self.notify(action)

    def do_not_summon_angel(self, legion: Legion.Legion) -> None:
        """Do not summon an angel into legion."""
        logging.info(f"Player.do_not_summon_angel {legion}")
        action = Action.DoNotSummonAngel(
            self.game.name, self.name, legion.markerid
        )
        self.notify(action)

    def do_not_reinforce(self, legion: Legion.Legion) -> None:
        """Do not recruit a reinforcement into legion."""
        logging.info(f"Player.do_not_reinforce {legion}")
        action = Action.DoNotReinforce(
            self.game.name, self.name, legion.markerid
        )
        self.notify(action)

    def new_turn(self) -> None:
        self.selected_markerid = None
        self.movement_roll = None
        self.summoned = False
        self.last_donor = None
        for legion in self.legions:
            legion.moved = False
            legion.teleported = False
            legion.entry_side = None
            legion.previous_hexlabel = None
            legion.recruited = False

    def clear_recruited(self) -> None:
        for legion in self.legions:
            legion.recruited = False

    def remove_legion(self, markerid: str) -> None:
        """Remove the legion with markerid."""
        assert type(markerid) == str
        if markerid in self.markerid_to_legion:
            legion = self.markerid_to_legion[markerid]
            legion.remove_observer(self)
            del self.markerid_to_legion[markerid]
            del legion
            self.markerids_left.add(markerid)

    def remove_all_legions(self) -> None:
        """Remove all legions, after being eliminated from the game."""
        for legion in self.legions:
            self.remove_legion(legion.markerid)

    def die(
        self, scoring_player: Optional[Player], check_for_victory: bool
    ) -> None:
        """Die and give half points to scoring_player, except for legions
        which are engaged with someone else.
        """
        logging.info(f"Player.die {self} {scoring_player} {check_for_victory}")
        # First reveal all this player's legions.
        for legion in self.legions:
            if legion.all_known and legion not in self.game.battle_legions:
                # Only reveal the legion if we're sure about its contents,
                # to avoid spreading disinformation.
                # Do not reveal the legion that's currently in battle, because
                # its contents are in flux.
                action = Action.RevealLegion(
                    self.game.name, legion.markerid, legion.creature_names
                )
                self.notify(action)
        if scoring_player is None:
            scoring_player_name = ""
        else:
            scoring_player_name = scoring_player.name
        self.has_titan = False
        action2 = Action.EliminatePlayer(
            self.game.name, scoring_player_name, self.name, check_for_victory
        )
        reactor.callLater(0.1, self.notify, action2)  # type: ignore

    def add_points(self, points: int) -> None:
        """Add points.  Do not acquire.

        This is only used for half points when eliminating a player.
        """
        logging.info(f"Player.add_points {self} {points}")
        self.score += points

    def forget_enemy_legions(self) -> None:
        """Forget the contents of all enemy legions."""
        logging.info("forget_enemy_legions")
        for legion in self.enemy_legions():
            legion.forget_creatures()

    def withdraw(self) -> None:
        """Withdraw from the game."""
        action = Action.Withdraw(self.game.name, self.name)
        self.notify(action)
