__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


import types
import logging

from twisted.internet import reactor

from slugathon.util.Observed import Observed
from slugathon.game import Action, Creature, Legion, Phase
from slugathon.data import playercolordata, creaturedata, markerdata
from slugathon.util.bag import bag
from slugathon.util import Dice


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
    def __init__(self, playername, game, join_order, player_class="Human",
      player_info=""):
        logging.info("%s %s %s %s %s", playername, game, join_order,
          player_class, player_info)
        Observed.__init__(self)
        self.name = playername
        self.player_class = player_class
        self.player_info = player_info or playername
        self.game = game
        self.join_order = join_order
        self.starting_tower = None    # a numeric hex label
        self.created_starting_legion = False
        self.score = 0
        self.color = None
        # Currently available markers
        self.markerids_left = set()
        # Private to this instance; not shown to others until a
        # legion is actually split off with this marker.
        self.selected_markerid = None
        # {str markerid : Legion}
        self.markerid_to_legion = {}
        self.mulligans_left = 1
        self.movement_roll = None
        self.summoned = False
        self.eliminated_colors = set()
        self.last_donor = None
        self.has_titan = True

    @property
    def legions(self):
        return self.markerid_to_legion.values()

    @property
    def dead(self):
        return self.created_starting_legion and not self.markerid_to_legion

    @property
    def teleported(self):
        """Return True iff any of this player's legions have teleported
        this turn."""
        for legion in self.legions:
            if legion.teleported:
                return True
        return False

    @property
    def color_abbrev(self):
        return playercolordata.name_to_abbrev.get(self.color)

    def __repr__(self):
        return "Player " + self.name

    def assign_starting_tower(self, tower):
        """Set this player's starting tower to the (int) tower"""
        assert type(tower) == types.IntType
        self.starting_tower = tower
        action = Action.AssignTower(self.game.name, self.name, tower)
        self.notify(action)

    def assign_color(self, color):
        """Set this player's color"""
        self.color = color
        abbrev = self.color_abbrev
        num_markers = len(markerdata.data[color])
        for ii in xrange(num_markers):
            self.markerids_left.add("%s%02d" % (abbrev, ii + 1))
        logging.info(self.markerids_left)
        action = Action.PickedColor(self.game.name, self.name, color)
        self.notify(action)

    def pick_marker(self, markerid):
        if markerid not in self.markerids_left:
            logging.info("pick_marker with bad marker")
            return
        self.selected_markerid = markerid

    def take_marker(self, markerid):
        if markerid not in self.markerids_left:
            raise AssertionError("take_marker with bad marker")
        self.markerids_left.remove(markerid)
        self.selected_markerid = None
        return markerid

    def create_starting_legion(self):
        markerid = self.selected_markerid
        if markerid is None:
            raise AssertionError("create_starting_legion without marker")
        if markerid not in self.markerids_left:
            raise AssertionError("create_starting_legion with bad marker")
        if self.markerid_to_legion:
            raise AssertionError("create_starting_legion but have a legion")
        creatures = [Creature.Creature(name) for name in
          creaturedata.starting_creature_names]
        legion = Legion.Legion(self, self.take_marker(markerid), creatures,
          self.starting_tower)
        self.markerid_to_legion[markerid] = legion
        legion.add_observer(self.game)
        action = Action.CreateStartingLegion(self.game.name, self.name,
          markerid)
        caretaker = self.game.caretaker
        for creature in creatures:
            caretaker.take_one(creature.name)
        self.created_starting_legion = True
        self.notify(action)

    @property
    def can_split(self):
        """Return True if this player can split any legions."""
        if self.markerids_left:
            if self.game.turn == 1:
                return len(self.legions) == 1
            for legion in self.legions:
                if len(legion) >= 4:
                    return True
        return False

    def split_legion(self, parent_markerid, child_markerid,
      parent_creature_names, child_creature_names):
        logging.info("%s %s %s %s", parent_markerid, child_markerid,
          parent_creature_names, child_creature_names)
        parent = self.markerid_to_legion.get(parent_markerid)
        if parent is None:
            return
        if child_markerid not in self.markerids_left:
            raise AssertionError("illegal marker")
        if bag(parent.creature_names) != bag(parent_creature_names).union(
          bag(child_creature_names)) and bag(parent_creature_names).union(bag(
          child_creature_names)) != bag({"Unknown": len(parent)}):
            raise AssertionError("wrong creatures",
              "parent.creature_names", parent.creature_names,
              "parent_creature_names", parent_creature_names,
              "child_creature_names", child_creature_names)
        new_legion1 = Legion.Legion(self, parent_markerid,
          Creature.n2c(parent_creature_names), parent.hexlabel)
        new_legion2 = Legion.Legion(self, child_markerid,
          Creature.n2c(child_creature_names), parent.hexlabel)
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
        action = Action.SplitLegion(self.game.name, self.name,
         parent_markerid, child_markerid, parent_creature_names,
         child_creature_names)
        logging.info(action)
        self.notify(action, names=[self.name])
        # Another action for everyone (including our player, who will
        # ignore it as a duplicate) without creature names.
        action = Action.SplitLegion(self.game.name, self.name,
          parent_markerid, child_markerid, len(parent_creature_names) *
          ["Unknown"], len(child_creature_names) * ["Unknown"])
        logging.info(action)
        self.notify(action)

    def undo_split(self, parent_markerid, child_markerid):
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
        action = Action.UndoSplit(self.game.name, self.name,
          parent_markerid, child_markerid, parent_creature_names,
          child_creature_names)
        self.notify(action, names=[self.name])
        action = Action.UndoSplit(self.game.name, self.name,
          parent_markerid, child_markerid, len(parent_creature_names) *
          ["Unknown"], len(child_creature_names) * ["Unknown"])
        other_playernames = self.game.playernames
        other_playernames.remove(self.name)
        self.notify(action, names=other_playernames)

    @property
    def can_exit_split_phase(self):
        """Return True if legal to exit the split phase"""
        if self.game.phase != Phase.SPLIT:
            return False
        if self.dead:
            return True
        return (self.markerid_to_legion and max((len(legion) for legion in
          self.legions)) < 8)

    def _roll_movement(self):
        self.movement_roll = Dice.roll()[0]
        action = Action.RollMovement(self.game.name, self.name,
          self.movement_roll, self.mulligans_left)
        self.notify(action)

    def done_with_splits(self):
        if self.can_exit_split_phase:
            self._roll_movement()

    @property
    def can_take_mulligan(self):
        """Return True iff this player can take a mulligan"""
        return bool(self is self.game.active_player and self.game.turn == 1
          and self.game.phase == Phase.MOVE and self.mulligans_left)

    def take_mulligan(self):
        self.mulligans_left -= 1
        self._roll_movement()

    @property
    def can_titan_teleport(self):
        return self.score >= 400

    @property
    def titan_power(self):
        return 6 + self.score // 100

    @property
    def num_creatures(self):
        return sum(len(legion) for legion in self.legions)

    @property
    def moved_legions(self):
        """Return a set of this players legions that have moved this turn."""
        return set([legion for legion in self.legions if legion.moved])

    @property
    def unmoved_legions(self):
        """Return a set of this players legions that have not moved."""
        return set([legion for legion in self.legions if not legion.moved])

    def friendly_legions(self, hexlabel=None):
        """Return a set of this player's legions, in hexlabel if not None."""
        return set([legion for legion in self.legions if hexlabel in
          (None, legion.hexlabel)])

    def enemy_legions(self, hexlabel=None):
        """Return a set of other players' legions, in hexlabel if not None."""
        return set([legion for legion in self.game.all_legions(hexlabel)
          if legion.player is not self])

    @property
    def can_exit_move_phase(self):
        """Return True iff this player can finish the move phase."""
        if self.game.phase != Phase.MOVE:
            return False
        if self.dead:
            return True
        if not self.moved_legions:
            return False
        for legion in self.friendly_legions():
            if len(self.friendly_legions(legion.hexlabel)) >= 2:
                if not legion.moved and self.game.find_all_moves(legion,
                  self.game.board.hexes[legion.hexlabel], self.movement_roll):
                    return False
                # else will need to recombine
        return True

    def recombine(self):
        """Recombine split legions as necessary."""
        while True:
            for legion in self.friendly_legions():
                legions_in_hex = list(self.friendly_legions(legion.hexlabel))
                if len(legions_in_hex) >= 2:
                    split_action = self.game.history.find_last_split(self.name,
                      legions_in_hex[0].markerid,
                      legions_in_hex[1].markerid)
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

    def done_with_moves(self):
        if self.can_exit_move_phase:
            self.recombine()
            action = Action.StartFightPhase(self.game.name, self.name)
            self.notify(action)

    @property
    def can_exit_fight_phase(self):
        """Return True iff this player can finish the fight phase."""
        if self.game.phase != Phase.FIGHT:
            return False
        logging.info("can_exit_fight_phase %s %s %s %s",
          self.game.engagement_hexlabels, self.game.pending_summon,
          self.game.pending_reinforcement, self.pending_acquire)
        return (not self.game.engagement_hexlabels and not
          self.game.pending_summon and not self.game.pending_reinforcement
          and not self.game.pending_acquire)

    @property
    def pending_acquire(self):
        for legion in self.legions:
            if legion.angels_pending or legion.archangels_pending:
                return True
        return False

    def reset_angels_pending(self):
        for legion in self.legions:
            legion.reset_angels_pending()

    def remove_empty_legions(self):
        """Remove any legions with no creatures, caused by summoning out
        the only creature in the legion."""
        for legion in self.legions:
            if not legion.creatures:
                self.remove_legion(legion.markerid)

    def done_with_engagements(self):
        logging.info("Player.done_with_engagements")
        if self.can_exit_fight_phase:
            logging.info("can exit fight phase")
            action = Action.StartMusterPhase(self.game.name, self.name)
            self.notify(action)

    @property
    def can_recruit(self):
        """Return True if any of this player's legions can recruit."""
        for legion in self.legions:
            if legion.moved and legion.can_recruit:
                return True
        return False

    @property
    def has_forced_strikes(self):
        for creature in self.game.battle_active_legion.creatures:
            if creature.engaged and not creature.struck:
                return True
        return False

    def done_with_battle_phase(self):
        """Finish whatever battle phase it currently is."""
        if self.game.battle_phase == Phase.REINFORCE:
            self.done_with_reinforcements()
        elif self.game.battle_phase == Phase.MANEUVER:
            self.done_with_maneuvers()
        elif self.game.battle_phase == Phase.STRIKE:
            self.done_with_strikes()
        elif self.game.battle_phase == Phase.COUNTERSTRIKE:
            self.done_with_counterstrikes()

    def done_with_recruits(self):
        if self.game.active_player != self or self.game.phase != Phase.MUSTER:
            logging.info("illegal call to done_with_recruits")
            return
        (player, turn) = self.game.next_player_and_turn
        if player is not None:
            action = Action.StartSplitPhase(self.game.name, player.name, turn)
            self.notify(action)

    def done_with_reinforcements(self):
        action = Action.StartManeuverBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_maneuvers(self):
        action = Action.StartStrikeBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_strikes(self):
        if self.has_forced_strikes:
            logging.info("Forced strikes remain")
            return
        player = None
        for legion in self.game.battle_legions:
            if legion.player != self:
                player = legion.player
        action = Action.StartCounterstrikeBattlePhase(self.game.name,
          player.name)
        self.notify(action)

    def done_with_counterstrikes(self):
        if self.has_forced_strikes:
            logging.info("Forced strikes remain")
            return
        action = Action.StartReinforceBattlePhase(self.game.name, self.name,
          self.game.battle_turn)
        self.notify(action)

    def summon_angel(self, legion, donor, creature_name):
        """Summon an angel from donor to legion."""
        logging.info("Player.summon_angel %s %s %s", legion, donor,
          creature_name)
        assert not self.summoned, "player tried to summon twice"
        assert len(legion) < 7, "legion too tall to summon"
        donor.reveal_creatures([creature_name])
        donor.remove_creature_by_name(creature_name)
        legion.add_creature_by_name(creature_name)
        creature = legion.creatures[-1]
        creature.legion = legion
        self.summoned = True
        self.last_donor = donor

    def unsummon_angel(self, legion, creature_name):
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
        action = Action.UnsummonAngel(self.game.name, self.name,
          legion.markerid, donor.markerid, creature.name)
        self.notify(action)

    def do_not_summon_angel(self, legion):
        """Do not summon an angel into legion."""
        logging.info("Player.do_not_summon_angel %s", legion)
        action = Action.DoNotSummonAngel(self.game.name, self.name,
          legion.markerid)
        self.notify(action)

    def do_not_reinforce(self, legion):
        """Do not recruit a reinforcement into legion."""
        logging.info("Player.do_not_reinforce %s", legion)
        action = Action.DoNotReinforce(self.game.name, self.name,
          legion.markerid)
        self.notify(action)

    def new_turn(self):
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

    def clear_recruited(self):
        for legion in self.legions:
            legion.recruited = False

    def remove_legion(self, markerid):
        """Remove the legion with markerid."""
        assert type(markerid) == str
        if markerid in self.markerid_to_legion:
            legion = self.markerid_to_legion[markerid]
            legion.remove_observer(self)
            del self.markerid_to_legion[markerid]
            del legion
            self.markerids_left.add(markerid)

    def remove_all_legions(self):
        """Remove all legions, after being eliminated from the game."""
        for legion in self.legions:
            self.remove_legion(legion.markerid)

    def die(self, scoring_player, check_for_victory):
        """Die and give half points to scoring_player, except for legions
        which are engaged with someone else.
        """
        logging.info("Player.die %s %s %s", self, scoring_player,
          check_for_victory)
        # First reveal all this player's legions.
        for legion in self.legions:
            if (legion.all_known and legion not in self.game.battle_legions):
                # Only reveal the legion if we're sure about its contents,
                # to avoid spreading disinformation.
                # Do not reveal the legion that's currently in battle, because
                # its contents are in flux.
                action = Action.RevealLegion(self.game.name, legion.markerid,
                  legion.creature_names)
                self.notify(action)
        if scoring_player is None:
            scoring_player_name = ""
        else:
            scoring_player_name = scoring_player.name
        self.has_titan = False
        action = Action.EliminatePlayer(self.game.name, scoring_player_name,
          self.name, check_for_victory)
        reactor.callLater(0.1, self.notify, action)

    def add_points(self, points):
        """Add points.  Do not acquire.

        This is only used for half points when eliminating a player.
        """
        logging.info("Player.add_points %s %s", self, points)
        self.score += points

    def forget_enemy_legions(self):
        """Forget the contents of all enemy legions."""
        logging.info("forget_enemy_legions")
        for legion in self.enemy_legions():
            legion.forget_creatures()

    def withdraw(self):
        """Withdraw from the game."""
        action = Action.Withdraw(self.game.name, self.name)
        self.notify(action)
