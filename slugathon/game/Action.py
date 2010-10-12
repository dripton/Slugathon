__copyright__ = "Copyright (c) 2004-2010 David Ripton"
__license__ = "GNU GPL v2"


import ast

from twisted.spread import pb


def fromstring(st):
    """Construct and return the appropriate Action subclass from the given
    repr string."""
    classname, dictstr = st.split(" ", 1)
    classobj = globals()[classname]
    dic = ast.literal_eval(dictstr)
    obj = classobj(**dic)
    return obj


class Action(pb.Copyable, pb.RemoteCopy):
    def __repr__(self):
        return "%s %s" % (self.__class__.__name__, self.__dict__)

    def __hash__(self):
        """Based on all the attributes of the Action, but not its class,
        so that an Action and its matching UndoAction have the same hash.
        """
        return hash(tuple(sorted(list(self.__dict__.iteritems()))))

    def __eq__(self, other):
        """Based on all the attributes of the Action, and its class."""
        return self.__class__ == other.__class__ and hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def undo_action(self):
        """If this action is undoable, construct the appropriate UndoAction."""
        return None

    def undoable(self):
        return (self.undo_action() is not None)


pb.setUnjellyableForClass(Action, Action)

class UndoAction(Action):
    """Abstract base class for Undo actions"""
    pass


class AddUsername(Action):
    def __init__(self, username):
        self.username = username
pb.setUnjellyableForClass(AddUsername, AddUsername)

class DelUsername(Action):
    def __init__(self, username):
        self.username = username
pb.setUnjellyableForClass(DelUsername, DelUsername)


class FormGame(Action):
    def __init__(self, username, game_name, create_time, start_time,
      min_players, max_players):
        self.username = username
        self.game_name = game_name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
pb.setUnjellyableForClass(FormGame, FormGame)


class RemoveGame(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(RemoveGame, RemoveGame)


class JoinGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name
pb.setUnjellyableForClass(JoinGame, JoinGame)

class DropFromGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name
pb.setUnjellyableForClass(DropFromGame, DropFromGame)


class AssignTower(Action):
    def __init__(self, game_name, playername, tower_num):
        self.game_name = game_name
        self.playername = playername
        self.tower_num = tower_num
pb.setUnjellyableForClass(AssignTower, AssignTower)

class AssignedAllTowers(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(AssignedAllTowers, AssignedAllTowers)


class PickedColor(Action):
    def __init__(self, game_name, playername, color):
        self.game_name = game_name
        self.playername = playername
        self.color = color
pb.setUnjellyableForClass(PickedColor, PickedColor)

class AssignedAllColors(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(AssignedAllColors, AssignedAllColors)


class CreateStartingLegion(Action):
    def __init__(self, game_name, playername, markername):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
pb.setUnjellyableForClass(CreateStartingLegion, CreateStartingLegion)


class SplitLegion(Action):
    def __init__(self, game_name, playername, parent_markername,
      child_markername, parent_creature_names, child_creature_names):
        """parent_creature_names and child_creature_names are lists of the
        actual creature names if known, or lists of height * None if not known
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markername = parent_markername
        self.child_markername = child_markername
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)

    def undo_action(self):
        return UndoSplit(self.game_name, self.playername,
          self.parent_markername, self.child_markername,
          self.parent_creature_names, self.child_creature_names)

pb.setUnjellyableForClass(SplitLegion, SplitLegion)


class UndoSplit(UndoAction):
    def __init__(self, game_name, playername, parent_markername,
      child_markername, parent_creature_names, child_creature_names):
        """Used for voluntarily undoing a split during the split phase.

        parent_creature_names and child_creature_names are lists of the
        actual creature names if known, or lists of height * None if not known
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markername = parent_markername
        self.child_markername = child_markername
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)
pb.setUnjellyableForClass(UndoSplit, UndoSplit)

class MergeLegions(Action):
    def __init__(self, game_name, playername, parent_markername,
      child_markername, parent_creature_names, child_creature_names):
        """Used for involuntarily undoing a split during the movement phase,
        because of a lack of legal non-teleport moves.

        parent_creature_names and child_creature_names are lists of the
        actual creature names if known, or lists of height * None if not known
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markername = parent_markername
        self.child_markername = child_markername
        self.parent_creature_names = tuple(parent_creature_names)
        self.child_creature_names = tuple(child_creature_names)
pb.setUnjellyableForClass(MergeLegions, MergeLegions)


class RollMovement(Action):
    def __init__(self, game_name, playername, movement_roll, mulligans_left):
        self.game_name = game_name
        self.playername = playername
        self.movement_roll = movement_roll
        self.mulligans_left = mulligans_left
pb.setUnjellyableForClass(RollMovement, RollMovement)

class MoveLegion(Action):
    def __init__(self, game_name, playername, markername, hexlabel,
      entry_side, teleport, teleporting_lord):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.hexlabel = hexlabel
        self.entry_side = entry_side
        self.teleport = teleport
        self.teleporting_lord = teleporting_lord

    def undo_action(self):
        return UndoMoveLegion(self.game_name, self.playername, self.markername,
          self.hexlabel, self.entry_side, self.teleport, self.teleporting_lord)

pb.setUnjellyableForClass(MoveLegion, MoveLegion)

class UndoMoveLegion(UndoAction):
    def __init__(self, game_name, playername, markername, hexlabel,
      entry_side, teleport, teleporting_lord):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.hexlabel = hexlabel
        self.entry_side = entry_side
        self.teleport = teleport
        self.teleporting_lord = teleporting_lord
pb.setUnjellyableForClass(UndoMoveLegion, UndoMoveLegion)

class StartSplitPhase(Action):
    def __init__(self, game_name, playername, turn):
        self.game_name = game_name
        self.playername = playername
        self.turn = turn
pb.setUnjellyableForClass(StartSplitPhase, StartSplitPhase)

class StartFightPhase(Action):
    def __init__(self, game_name, playername):
        self.game_name = game_name
        self.playername = playername
pb.setUnjellyableForClass(StartFightPhase, StartFightPhase)

class StartMusterPhase(Action):
    def __init__(self, game_name, playername):
        self.game_name = game_name
        self.playername = playername
pb.setUnjellyableForClass(StartMusterPhase, StartMusterPhase)


class RecruitCreature(Action):
    def __init__(self, game_name, playername, markername, creature_name,
      recruiter_names):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.creature_name = creature_name
        self.recruiter_names = tuple(recruiter_names)

    def undo_action(self):
        return UndoRecruit(self.game_name, self.playername, self.markername,
          self.creature_name, self.recruiter_names)

pb.setUnjellyableForClass(RecruitCreature, RecruitCreature)

class DoNotReinforce(Action):
    def __init__(self, game_name, playername, markername):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername

pb.setUnjellyableForClass(DoNotReinforce, DoNotReinforce)

class UnReinforce(UndoAction):
    def __init__(self, game_name, playername, markername, creature_name,
      recruiter_names):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.creature_name = creature_name
        self.recruiter_names = tuple(recruiter_names)
pb.setUnjellyableForClass(UnReinforce, UnReinforce)

class UndoRecruit(UndoAction):
    def __init__(self, game_name, playername, markername, creature_name,
      recruiter_names):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.creature_name = creature_name
        self.recruiter_names = tuple(recruiter_names)
pb.setUnjellyableForClass(UndoRecruit, UndoRecruit)

# TODO Act on this action.  Currently meaningless since all legion contents
# are public.
class RevealLegion(Action):
    def __init__(self, game_name, markername, creature_names):
        self.game_name = game_name
        self.markername = markername
        self.creature_names = tuple(creature_names)
pb.setUnjellyableForClass(RevealLegion, RevealLegion)


class ResolvingEngagement(Action):
    def __init__(self, game_name, hexlabel):
        self.game_name = game_name
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(ResolvingEngagement, ResolvingEngagement)


class Flee(Action):
    def __init__(self, game_name, markername, enemy_markername, hexlabel):
        self.game_name = game_name
        self.markername = markername
        self.enemy_markername = enemy_markername
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(Flee, Flee)


class DoNotFlee(Action):
    def __init__(self, game_name, markername, enemy_markername, hexlabel):
        self.game_name = game_name
        self.markername = markername
        self.enemy_markername = enemy_markername
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(DoNotFlee, DoNotFlee)


class Concede(Action):
    def __init__(self, game_name, markername, enemy_markername, hexlabel):
        self.game_name = game_name
        self.markername = markername
        self.enemy_markername = enemy_markername
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(Concede, Concede)


class Fight(Action):
    def __init__(self, game_name, attacker_markername, defender_markername,
      hexlabel):
        self.game_name = game_name
        self.attacker_markername = attacker_markername
        self.defender_markername = defender_markername
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(Fight, Fight)


class MakeProposal(Action):
    def __init__(self, game_name, playername, other_playername,
      attacker_markername, attacker_creature_names,
      defender_markername, defender_creature_names):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markername = attacker_markername
        self.defender_markername = defender_markername
        self.attacker_creature_names = tuple(attacker_creature_names)
        self.defender_creature_names = tuple(defender_creature_names)
pb.setUnjellyableForClass(MakeProposal, MakeProposal)

class AcceptProposal(Action):
    def __init__(self, game_name, playername, other_playername,
      attacker_markername, attacker_creature_names,
      defender_markername, defender_creature_names, hexlabel):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markername = attacker_markername
        self.defender_markername = defender_markername
        self.attacker_creature_names = tuple(attacker_creature_names)
        self.defender_creature_names = tuple(defender_creature_names)
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(AcceptProposal, AcceptProposal)

class RejectProposal(Action):
    def __init__(self, game_name, playername, other_playername,
      attacker_markername, attacker_creature_names,
      defender_markername, defender_creature_names):
        self.game_name = game_name
        self.playername = playername
        self.other_playername = other_playername
        self.attacker_markername = attacker_markername
        self.defender_markername = defender_markername
        self.attacker_creature_names = tuple(attacker_creature_names)
        self.defender_creature_names = tuple(defender_creature_names)
pb.setUnjellyableForClass(RejectProposal, RejectProposal)

class MoveCreature(Action):
    def __init__(self, game_name, playername, creature_name, old_hexlabel,
      new_hexlabel):
        self.game_name = game_name
        self.playername = playername
        self.creature_name = creature_name
        self.old_hexlabel = old_hexlabel
        self.new_hexlabel = new_hexlabel

    def undo_action(self):
        return UndoMoveCreature(self.game_name, self.playername,
          self.creature_name, self.old_hexlabel, self.new_hexlabel)

pb.setUnjellyableForClass(MoveCreature, MoveCreature)

class UndoMoveCreature(UndoAction):
    def __init__(self, game_name, playername, creature_name, old_hexlabel,
      new_hexlabel):
        self.game_name = game_name
        self.playername = playername
        self.creature_name = creature_name
        self.old_hexlabel = old_hexlabel
        self.new_hexlabel = new_hexlabel
pb.setUnjellyableForClass(UndoMoveCreature, UndoMoveCreature)

class StartReinforceBattlePhase(Action):
    def __init__(self, game_name, playername, battle_turn):
        self.game_name = game_name
        self.playername = playername
        self.battle_turn = battle_turn
pb.setUnjellyableForClass(StartReinforceBattlePhase, StartReinforceBattlePhase)

class StartManeuverBattlePhase(Action):
    def __init__(self, game_name, playername):
        self.game_name = game_name
        self.playername = playername
pb.setUnjellyableForClass(StartManeuverBattlePhase, StartManeuverBattlePhase)

class StartStrikeBattlePhase(Action):
    def __init__(self, game_name, playername):
        self.game_name = game_name
        self.playername = playername
pb.setUnjellyableForClass(StartStrikeBattlePhase, StartStrikeBattlePhase)

class StartCounterstrikeBattlePhase(Action):
    def __init__(self, game_name, playername):
        self.game_name = game_name
        self.playername = playername
pb.setUnjellyableForClass(StartCounterstrikeBattlePhase,
  StartCounterstrikeBattlePhase)


class DriftDamage(Action):
    def __init__(self, game_name, target_name, target_hexlabel, hits):
        self.game_name = game_name
        self.target_name = target_name
        self.target_hexlabel = target_hexlabel
        self.hits = hits
pb.setUnjellyableForClass(DriftDamage, DriftDamage)

class Strike(Action):
    def __init__(self, game_name, playername, striker_name, striker_hexlabel,
      target_name, target_hexlabel, num_dice, strike_number,
      rolls, hits, carries):
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
pb.setUnjellyableForClass(Strike, Strike)

class Carry(Action):
    def __init__(self, game_name, playername, striker_name, striker_hexlabel,
      target_name, target_hexlabel, carry_target_name, carry_target_hexlabel,
      num_dice, strike_number, carries, carries_left):
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
pb.setUnjellyableForClass(Carry, Carry)

class SummonAngel(Action):
    def __init__(self, game_name, playername, markername, donor_markername,
      creature_name):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.donor_markername = donor_markername
        self.creature_name = creature_name
pb.setUnjellyableForClass(SummonAngel, SummonAngel)

class UnSummon(Action):
    def __init__(self, game_name, playername, markername, donor_markername,
      creature_name):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.donor_markername = donor_markername
        self.creature_name = creature_name
pb.setUnjellyableForClass(UnSummon, UnSummon)

class DoNotSummon(Action):
    def __init__(self, game_name, playername, markername):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
pb.setUnjellyableForClass(DoNotSummon, DoNotSummon)

class CanAcquire(Action):
    def __init__(self, game_name, playername, markername, angels, archangels):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.angels = angels
        self.archangels = archangels
pb.setUnjellyableForClass(CanAcquire, CanAcquire)

class Acquire(Action):
    def __init__(self, game_name, playername, markername, angel_names):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.angel_names = tuple(angel_names)
pb.setUnjellyableForClass(Acquire, Acquire)

class DoNotAcquire(Action):
    def __init__(self, game_name, playername, markername):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
pb.setUnjellyableForClass(DoNotAcquire, DoNotAcquire)

class BattleOver(Action):
    def __init__(self, game_name, winner_markername, winner_survivors,
      winner_losses, loser_markername, loser_survivors, loser_losses,
      time_loss, hexlabel):
        self.game_name = game_name
        self.winner_markername = winner_markername
        self.winner_survivors = tuple(winner_survivors)
        self.winner_losses = tuple(winner_losses)
        self.loser_markername = loser_markername
        self.loser_survivors = tuple(loser_survivors)
        self.loser_losses = tuple(loser_losses)
        self.time_loss = time_loss
        self.hexlabel = hexlabel
pb.setUnjellyableForClass(BattleOver, BattleOver)

class EliminatePlayer(Action):
    def __init__(self, game_name, winner_playername, loser_playername):
        self.game_name = game_name
        self.winner_playername = winner_playername
        self.loser_playername = loser_playername
pb.setUnjellyableForClass(EliminatePlayer, EliminatePlayer)

class GameOver(Action):
    def __init__(self, game_name, winner_names):
        self.game_name = game_name
        self.winner_names = tuple(winner_names)
pb.setUnjellyableForClass(GameOver, GameOver)
