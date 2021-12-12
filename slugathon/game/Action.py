import ast
from typing import Any, List, Optional, Tuple

from twisted.spread import pb

from slugathon.util.bag import bag


__copyright__ = "Copyright (c) 2004-2021 David Ripton"
__license__ = "GNU GPL v2"


def fromstring(st: str) -> Any:
    """Construct and return the appropriate Action subclass from the given
    repr string."""
    classname, dictstr = st.split(" ", 1)
    classobj = globals()[classname]
    dct = ast.literal_eval(dictstr)
    obj = classobj(**dct)
    return obj


class Action(pb.Copyable, pb.RemoteCopy):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__dict__}"

    def __hash__(self) -> int:
        """Based on all the attributes of the Action, but not its class,
        so that an Action and its matching UndoAction have the same hash.
        """
        return hash(tuple(sorted(list(self.__dict__.items()))))

    def __eq__(self, other: Any) -> bool:
        """Based on all the attributes of the Action, and its class."""
        return self.__class__ == other.__class__ and hash(self) == hash(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def undo_action(self) -> Any:
        """If this action is undoable, construct the appropriate UndoAction."""
        return None

    def undoable(self) -> bool:
        return self.undo_action() is not None


pb.setUnjellyableForClass(Action, Action)  # type: ignore


class UndoAction(Action):

    """Abstract base class for Undo actions"""

    pass


class EphemeralAction(Action):

    """Abstract base class for actions that we don't want to save."""

    pass


class AddUsername(Action):
    def __init__(self, playername: str):
        self.playername = playername


pb.setUnjellyableForClass(AddUsername, AddUsername)  # type: ignore


class DelUsername(Action):
    def __init__(self, playername: str):
        self.playername = playername


pb.setUnjellyableForClass(DelUsername, DelUsername)  # type: ignore


class FormGame(Action):
    def __init__(
        self,
        playername: str,
        game_name: str,
        create_time: float,
        start_time: float,
        min_players: int,
        max_players: int,
        ai_time_limit: int,
        player_time_limit: int,
        player_class: str,
        player_info: str,
    ):
        self.playername = playername
        self.game_name = game_name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
        self.ai_time_limit = ai_time_limit
        self.player_time_limit = player_time_limit
        self.player_class = player_class
        self.player_info = player_info


pb.setUnjellyableForClass(FormGame, FormGame)  # type: ignore


class RemoveGame(Action):
    def __init__(self, game_name: str):
        self.game_name = game_name


pb.setUnjellyableForClass(RemoveGame, RemoveGame)  # type: ignore


class JoinGame(Action):
    def __init__(
        self,
        playername: str,
        game_name: str,
        player_class: str,
        player_info: str,
    ):
        self.playername = playername
        self.game_name = game_name
        self.player_class = player_class
        self.player_info = player_info


pb.setUnjellyableForClass(JoinGame, JoinGame)  # type: ignore


class AssignTower(Action):
    def __init__(self, game_name: str, playername: str, tower_num: int):
        self.game_name = game_name
        self.playername = playername
        self.tower_num = tower_num


pb.setUnjellyableForClass(AssignTower, AssignTower)  # type: ignore


class AssignedAllTowers(Action):
    def __init__(self, game_name: str):
        self.game_name = game_name


pb.setUnjellyableForClass(AssignedAllTowers, AssignedAllTowers)  # type: ignore


class PickedColor(Action):
    def __init__(self, game_name: str, playername: str, color: str):
        self.game_name = game_name
        self.playername = playername
        self.color = color


pb.setUnjellyableForClass(PickedColor, PickedColor)  # type: ignore


class AssignedAllColors(Action):
    def __init__(self, game_name: str):
        self.game_name = game_name


pb.setUnjellyableForClass(AssignedAllColors, AssignedAllColors)  # type: ignore


class CreateStartingLegion(Action):
    def __init__(self, game_name: str, playername: str, markerid: str):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid


pb.setUnjellyableForClass(CreateStartingLegion, CreateStartingLegion)  # type: ignore


class SplitLegion(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        parent_markerid: str,
        child_markerid: str,
        parent_creature_names: List[str],
        child_creature_names: List[str],
    ):
        """parent_creature_names and child_creature_names are lists of the
        actual creature names or "Unknown".
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markerid = parent_markerid
        self.child_markerid = child_markerid
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)

    def undo_action(self):
        return UndoSplit(
            self.game_name,
            self.playername,
            self.parent_markerid,
            self.child_markerid,
            self.parent_creature_names,
            self.child_creature_names,
        )


pb.setUnjellyableForClass(SplitLegion, SplitLegion)  # type: ignore


class UndoSplit(UndoAction):
    def __init__(
        self,
        game_name: str,
        playername: str,
        parent_markerid: str,
        child_markerid: str,
        parent_creature_names: List[str],
        child_creature_names: List[str],
    ):
        """Used for voluntarily undoing a split during the split phase.

        parent_creature_names and child_creature_names are lists of the
        actual creature names if known, or lists of height * "Unknown" if not.
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markerid = parent_markerid
        self.child_markerid = child_markerid
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)


pb.setUnjellyableForClass(UndoSplit, UndoSplit)  # type: ignore


class MergeLegions(Action):
    def __init__(
        self,
        game_name,
        playername,
        parent_markerid,
        child_markerid,
        parent_creature_names,
        child_creature_names,
    ):
        """Used for involuntarily undoing a split during the movement phase,
        because of a lack of legal non-teleport moves.

        parent_creature_names and child_creature_names are lists of the
        actual creature names if known, or lists of height * "Unknown" if not.
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markerid = parent_markerid
        self.child_markerid = child_markerid
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)


pb.setUnjellyableForClass(MergeLegions, MergeLegions)  # type: ignore


class RollMovement(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        movement_roll: int,
        mulligans_left: int,
    ):
        self.game_name = game_name
        self.playername = playername
        self.movement_roll = movement_roll
        self.mulligans_left = mulligans_left


pb.setUnjellyableForClass(RollMovement, RollMovement)  # type: ignore


class MoveLegion(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        hexlabel: int,
        entry_side: int,
        teleport: bool,
        teleporting_lord: str,
        previous_hexlabel: int,
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.hexlabel = hexlabel
        self.entry_side = entry_side
        self.teleport = teleport
        self.teleporting_lord = teleporting_lord
        self.previous_hexlabel = previous_hexlabel

    def undo_action(self):
        return UndoMoveLegion(
            self.game_name,
            self.playername,
            self.markerid,
            self.hexlabel,
            self.entry_side,
            self.teleport,
            self.teleporting_lord,
            self.previous_hexlabel,
        )


pb.setUnjellyableForClass(MoveLegion, MoveLegion)  # type: ignore


class UndoMoveLegion(UndoAction):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        hexlabel: int,
        entry_side: int,
        teleport: bool,
        teleporting_lord: Optional[str],
        previous_hexlabel: int,
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.hexlabel = hexlabel
        self.entry_side = entry_side
        self.teleport = teleport
        self.teleporting_lord = teleporting_lord
        self.previous_hexlabel = previous_hexlabel


pb.setUnjellyableForClass(UndoMoveLegion, UndoMoveLegion)  # type: ignore


class StartSplitPhase(Action):
    def __init__(self, game_name: str, playername: str, turn: int):
        self.game_name = game_name
        self.playername = playername
        self.turn = turn


pb.setUnjellyableForClass(StartSplitPhase, StartSplitPhase)  # type: ignore


class StartFightPhase(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(StartFightPhase, StartFightPhase)  # type: ignore


class StartMusterPhase(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(StartMusterPhase, StartMusterPhase)  # type: ignore


class RecruitCreature(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        creature_name: str,
        recruiter_names: Tuple[str, ...],
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.creature_name = creature_name
        self.recruiter_names = tuple(recruiter_names)

    def undo_action(self):
        return UndoRecruit(
            self.game_name,
            self.playername,
            self.markerid,
            self.creature_name,
            self.recruiter_names,
        )


pb.setUnjellyableForClass(RecruitCreature, RecruitCreature)  # type: ignore


class DoNotReinforce(Action):
    def __init__(self, game_name: str, playername: str, markerid: str):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid


pb.setUnjellyableForClass(DoNotReinforce, DoNotReinforce)  # type: ignore


class UnReinforce(UndoAction):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        creature_name: str,
        recruiter_names: Tuple[str, ...],
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.creature_name = creature_name
        self.recruiter_names = recruiter_names


pb.setUnjellyableForClass(UnReinforce, UnReinforce)  # type: ignore


class UndoRecruit(UndoAction):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        creature_name: str,
        recruiter_names: Tuple[str, ...],
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.creature_name = creature_name
        self.recruiter_names = recruiter_names


pb.setUnjellyableForClass(UndoRecruit, UndoRecruit)  # type: ignore


class RevealLegion(Action):
    def __init__(
        self, game_name: str, markerid: str, creature_names: List[str]
    ):
        self.game_name = game_name
        self.markerid = markerid
        self.creature_names = tuple(creature_names)  # type: Tuple[str, ...]


pb.setUnjellyableForClass(RevealLegion, RevealLegion)  # type: ignore


class ResolvingEngagement(Action):
    def __init__(self, game_name: str, hexlabel: int):
        self.game_name = game_name
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(ResolvingEngagement, ResolvingEngagement)  # type: ignore


class Flee(Action):
    def __init__(
        self, game_name: str, markerid: str, enemy_markerid: str, hexlabel: int
    ):
        self.game_name = game_name
        self.markerid = markerid
        self.enemy_markerid = enemy_markerid
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(Flee, Flee)  # type: ignore


class DoNotFlee(Action):
    def __init__(
        self, game_name: str, markerid: str, enemy_markerid: str, hexlabel: int
    ):
        self.game_name = game_name
        self.markerid = markerid
        self.enemy_markerid = enemy_markerid
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(DoNotFlee, DoNotFlee)  # type: ignore


class Concede(Action):
    def __init__(
        self, game_name: str, markerid: str, enemy_markerid: str, hexlabel: int
    ):
        self.game_name = game_name
        self.markerid = markerid
        self.enemy_markerid = enemy_markerid
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(Concede, Concede)  # type: ignore


class Fight(Action):
    def __init__(
        self,
        game_name: str,
        attacker_markerid: str,
        defender_markerid: str,
        hexlabel: int,
    ):
        self.game_name = game_name
        self.attacker_markerid = attacker_markerid
        self.defender_markerid = defender_markerid
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(Fight, Fight)  # type: ignore


class MakeProposal(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        other_playername: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
    ):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markerid = attacker_markerid
        self.defender_markerid = defender_markerid
        self.attacker_creature_names = tuple(attacker_creature_names)
        self.defender_creature_names = tuple(defender_creature_names)


pb.setUnjellyableForClass(MakeProposal, MakeProposal)  # type: ignore


class AcceptProposal(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        other_playername: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
        hexlabel: int,
    ):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markerid = attacker_markerid
        self.defender_markerid = defender_markerid
        self.attacker_creature_names = tuple(
            attacker_creature_names
        )  # type: Tuple[str, ...]
        self.defender_creature_names = tuple(
            defender_creature_names
        )  # type: Tuple[str, ...]
        self.hexlabel = hexlabel


pb.setUnjellyableForClass(AcceptProposal, AcceptProposal)  # type: ignore


class RejectProposal(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        other_playername: str,
        attacker_markerid: str,
        attacker_creature_names: bag,
        defender_markerid: str,
        defender_creature_names: bag,
    ):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markerid = attacker_markerid
        self.defender_markerid = defender_markerid
        self.attacker_creature_names = tuple(attacker_creature_names)
        self.defender_creature_names = tuple(defender_creature_names)


pb.setUnjellyableForClass(RejectProposal, RejectProposal)  # type: ignore


class NoMoreProposals(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        attacker_markerid: str,
        defender_markerid: str,
    ):
        self.game_name = game_name
        self.playername = playername
        self.attacker_markerid = attacker_markerid
        self.defender_markerid = defender_markerid


pb.setUnjellyableForClass(NoMoreProposals, NoMoreProposals)  # type: ignore


class MoveCreature(Action):
    def __init__(
        self,
        game_name,
        playername: str,
        creature_name: str,
        old_hexlabel: str,
        new_hexlabel: str,
    ):
        self.game_name = game_name
        self.playername = playername
        self.creature_name = creature_name
        self.old_hexlabel = old_hexlabel
        self.new_hexlabel = new_hexlabel

    def undo_action(self):
        return UndoMoveCreature(
            self.game_name,
            self.playername,
            self.creature_name,
            self.old_hexlabel,
            self.new_hexlabel,
        )


pb.setUnjellyableForClass(MoveCreature, MoveCreature)  # type: ignore


class UndoMoveCreature(UndoAction):
    def __init__(
        self,
        game_name: str,
        playername: str,
        creature_name: str,
        old_hexlabel: str,
        new_hexlabel: str,
    ):
        self.game_name = game_name
        self.playername = playername
        self.creature_name = creature_name
        self.old_hexlabel = old_hexlabel
        self.new_hexlabel = new_hexlabel


pb.setUnjellyableForClass(UndoMoveCreature, UndoMoveCreature)  # type: ignore


class StartReinforceBattlePhase(Action):
    def __init__(self, game_name: str, playername: str, battle_turn: int):
        self.game_name = game_name
        self.playername = playername
        self.battle_turn = battle_turn


pb.setUnjellyableForClass(StartReinforceBattlePhase, StartReinforceBattlePhase)  # type: ignore


class StartManeuverBattlePhase(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(StartManeuverBattlePhase, StartManeuverBattlePhase)  # type: ignore


class StartStrikeBattlePhase(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(StartStrikeBattlePhase, StartStrikeBattlePhase)  # type: ignore


class StartCounterstrikeBattlePhase(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(  # type: ignore
    StartCounterstrikeBattlePhase, StartCounterstrikeBattlePhase
)


class DriftDamage(Action):
    def __init__(
        self, game_name: str, target_name: str, target_hexlabel: str, hits: int
    ):
        self.game_name = game_name
        self.target_name = target_name
        self.target_hexlabel = target_hexlabel
        self.hits = hits


pb.setUnjellyableForClass(DriftDamage, DriftDamage)  # type: ignore


class Strike(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        striker_name: str,
        striker_hexlabel: str,
        target_name: str,
        target_hexlabel: str,
        num_dice: int,
        strike_number: int,
        rolls: List[int],
        hits: int,
        carries: int,
    ):
        """hits is the total number of hits, including excess
        carries is the number of carries available
        """
        self.game_name = game_name
        self.playername = playername
        self.striker_name = striker_name
        self.striker_hexlabel = striker_hexlabel
        self.target_name = target_name
        self.target_hexlabel = target_hexlabel
        self.num_dice = num_dice
        self.strike_number = strike_number
        self.rolls = tuple(rolls)
        self.hits = hits
        self.carries = carries


pb.setUnjellyableForClass(Strike, Strike)  # type: ignore


class Carry(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        striker_name: str,
        striker_hexlabel: str,
        target_name: str,
        target_hexlabel: str,
        carry_target_name: str,
        carry_target_hexlabel: str,
        num_dice: int,
        strike_number: int,
        carries: int,
        carries_left: int,
    ):
        """carries is the number of carries that were applied.
        carries_left is the number of carries left over for another target.
        """
        self.game_name = game_name
        self.playername = playername
        self.striker_name = striker_name
        self.striker_hexlabel = striker_hexlabel
        self.target_name = target_name
        self.target_hexlabel = target_hexlabel
        self.carry_target_name = carry_target_name
        self.carry_target_hexlabel = carry_target_hexlabel
        self.num_dice = num_dice
        self.strike_number = strike_number
        self.carries = carries
        self.carries_left = carries_left


pb.setUnjellyableForClass(Carry, Carry)  # type: ignore


class SummonAngel(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        donor_markerid: str,
        creature_name: str,
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.donor_markerid = donor_markerid
        self.creature_name = creature_name


pb.setUnjellyableForClass(SummonAngel, SummonAngel)  # type: ignore


class UnsummonAngel(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        donor_markerid: str,
        creature_name: str,
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.donor_markerid = donor_markerid
        self.creature_name = creature_name


pb.setUnjellyableForClass(UnsummonAngel, UnsummonAngel)  # type: ignore


class DoNotSummonAngel(Action):
    def __init__(self, game_name: str, playername: str, markerid: str):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid


pb.setUnjellyableForClass(DoNotSummonAngel, DoNotSummonAngel)  # type: ignore


class CanAcquireAngels(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        angels: int,
        archangels: int,
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.angels = angels
        self.archangels = archangels


pb.setUnjellyableForClass(CanAcquireAngels, CanAcquireAngels)  # type: ignore


class AcquireAngels(Action):
    def __init__(
        self,
        game_name: str,
        playername: str,
        markerid: str,
        angel_names: List[str],
    ):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid
        self.angel_names = tuple(angel_names)


pb.setUnjellyableForClass(AcquireAngels, AcquireAngels)  # type: ignore


class DoNotAcquireAngels(Action):
    def __init__(self, game_name: str, playername: str, markerid: str):
        self.game_name = game_name
        self.playername = playername
        self.markerid = markerid


pb.setUnjellyableForClass(DoNotAcquireAngels, DoNotAcquireAngels)  # type: ignore


class BattleOver(Action):
    def __init__(
        self,
        game_name: str,
        winner_markerid: str,
        winner_survivors: List[str],
        winner_losses: List[str],
        loser_markerid: str,
        loser_survivors: List[str],
        loser_losses: List[str],
        time_loss: bool,
        hexlabel: int,
        mutual: bool,
    ):
        self.game_name = game_name
        self.winner_markerid = winner_markerid
        self.winner_survivors = tuple(winner_survivors)
        self.winner_losses = tuple(winner_losses)
        self.loser_markerid = loser_markerid
        self.loser_survivors = tuple(loser_survivors)
        self.loser_losses = tuple(loser_losses)
        self.time_loss = time_loss
        self.hexlabel = hexlabel
        self.mutual = mutual


pb.setUnjellyableForClass(BattleOver, BattleOver)  # type: ignore


class Withdraw(Action):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(Withdraw, Withdraw)  # type: ignore


class EliminatePlayer(Action):
    def __init__(
        self,
        game_name: str,
        winner_playername: str,
        loser_playername: str,
        check_for_victory: bool,
    ):
        self.game_name = game_name
        self.winner_playername = winner_playername
        self.loser_playername = loser_playername
        self.check_for_victory = check_for_victory


pb.setUnjellyableForClass(EliminatePlayer, EliminatePlayer)  # type: ignore


class GameOver(Action):
    def __init__(
        self, game_name: str, winner_names: List[str], finish_time: float
    ):
        self.game_name = game_name
        self.winner_names = tuple(winner_names)
        self.finish_time = finish_time


pb.setUnjellyableForClass(GameOver, GameOver)  # type: ignore


class PauseAI(EphemeralAction):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(PauseAI, PauseAI)  # type: ignore


class ResumeAI(EphemeralAction):
    def __init__(self, game_name: str, playername: str):
        self.game_name = game_name
        self.playername = playername


pb.setUnjellyableForClass(ResumeAI, ResumeAI)  # type: ignore


class ChatMessage(EphemeralAction):
    def __init__(self, source_playername: str, message: str):
        self.source_playername = source_playername
        self.message = message


pb.setUnjellyableForClass(ChatMessage, ChatMessage)  # type: ignore
