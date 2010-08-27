__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"


import types

from zope.interface import implements

from slugathon.util.Observed import Observed
from slugathon.util.Observer import IObserver
from slugathon.game import Action, Creature, Legion, Phase
from slugathon.data import playercolordata, creaturedata, markerdata
from slugathon.util.bag import bag
from slugathon.util import Dice
from slugathon.util.log import log


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

    implements(IObserver)

    def __init__(self, playername, game, join_order):
        Observed.__init__(self)
        self.name = playername
        self.game = game
        self.join_order = join_order
        self.starting_tower = None    # a numeric hex label
        self.score = 0
        self.color = None
        # Currently available markers
        self.markernames = set()
        # Private to this instance; not shown to others until a
        # legion is actually split off with this marker.
        self.selected_markername = None
        # {str markername : Legion}
        self.legions = {}
        self.mulligans_left = 1
        self.movement_roll = None
        self.summoned = False
        self.eliminated_colors = set()

    @property
    def dead(self):
        return self.color and self.starting_tower and not self.legions

    @property
    def teleported(self):
        """Return True iff any of this player's legions have teleported
        this turn."""
        for legion in self.legions.itervalues():
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
        action = Action.PickedColor(self.game.name, self.name, color)
        abbrev = self.color_abbrev
        num_markers = len(markerdata.data[color])
        for ii in xrange(num_markers):
            self.markernames.add("%s%02d" % (abbrev, ii + 1))
        self.notify(action)

    def pick_marker(self, markername):
        if markername in self.markernames:
            self.selected_markername = markername

    def take_marker(self, markername):
        if markername not in self.markernames:
            raise AssertionError("take_marker with bad marker")
        self.markernames.remove(markername)
        self.selected_markername = None
        return markername

    def create_starting_legion(self):
        markername = self.selected_markername
        if markername is None:
            raise AssertionError("create_starting_legion without marker")
        if markername not in self.markernames:
            raise AssertionError("create_starting_legion with bad marker")
        if self.legions:
            raise AssertionError("create_starting_legion but have a legion")
        creatures = [Creature.Creature(name) for name in
          creaturedata.starting_creature_names]
        legion = Legion.Legion(self, self.take_marker(markername), creatures,
          self.starting_tower)
        self.legions[markername] = legion
        legion.add_observer(self)
        action = Action.CreateStartingLegion(self.game.name, self.name,
          markername)
        caretaker = self.game.caretaker
        for creature in creatures:
            caretaker.take_one(creature.name)
        self.notify(action)

    def can_split(self):
        """Return True if this player can split any legions."""
        if self.markernames:
            for legion in self.legions.itervalues():
                if len(legion) >= 4:
                    return True
        return False

    def split_legion(self, parent_markername, child_markername,
      parent_creature_names, child_creature_names):
        parent = self.legions[parent_markername]
        if child_markername not in self.markernames:
            raise AssertionError("illegal marker")
        if bag(parent.creature_names) != bag(parent_creature_names).union(
          bag(child_creature_names)):
            raise AssertionError("wrong creatures")
        new_legion1 = Legion.Legion(self, parent_markername,
          Creature.n2c(parent_creature_names), parent.hexlabel)
        new_legion1.add_observer(self)
        new_legion2 = Legion.Legion(self, child_markername,
          Creature.n2c(child_creature_names), parent.hexlabel)
        new_legion2.add_observer(self)
        if not parent.is_legal_split(new_legion1, new_legion2):
            raise AssertionError("illegal split")
        self.take_marker(child_markername)
        for creature_name in child_creature_names:
            parent.remove_creature_by_name(creature_name)
        self.legions[child_markername] = new_legion2
        # TODO One action for our player with creature names, and a
        # different action for other players without.
        action = Action.SplitLegion(self.game.name, self.name,
          parent_markername, child_markername, parent_creature_names,
          child_creature_names)
        self.notify(action)

    def undo_split(self, parent_markername, child_markername):
        parent = self.legions[parent_markername]
        child = self.legions[child_markername]
        parent_creature_names = parent.creature_names
        child_creature_names = child.creature_names
        parent.creatures += child.creatures
        child.remove_observer(self)
        del self.legions[child_markername]
        self.markernames.add(child.markername)
        del child
        # TODO One action for our player with creature names, and a
        # different action for other players without.
        action = Action.UndoSplit(self.game.name, self.name,
          parent_markername, child_markername, parent_creature_names,
          child_creature_names)
        self.notify(action)


    def can_exit_split_phase(self):
        """Return True if legal to exit the split phase"""
        return (self.legions and max([len(legion) for legion in
          self.legions.itervalues()]) < 8)

    def _roll_movement(self):
        self.movement_roll = Dice.roll()[0]
        action = Action.RollMovement(self.game.name, self.name,
          self.movement_roll)
        self.notify(action)

    def done_with_splits(self):
        if self.can_exit_split_phase():
            self._roll_movement()

    def can_take_mulligan(self):
        """Return True iff this player can take a mulligan"""
        return bool(self is self.game.active_player and self.game.turn == 1
          and self.game.phase == Phase.MOVE and self.mulligans_left)

    def take_mulligan(self):
        self.mulligans_left -= 1
        self._roll_movement()

    def can_titan_teleport(self):
        return self.score >= 400

    def titan_power(self):
        return 6 + self.score // 100

    def num_creatures(self):
        return sum(len(legion) for legion in self.legions.itervalues())

    def moved_legions(self):
        """Return a set of this players legions that have moved this turn."""
        return set([legion for legion in self.legions.itervalues() if
          legion.moved])

    def friendly_legions(self, hexlabel=None):
        """Return a set of this player's legions, in hexlabel if not None."""
        return set([legion for legion in self.legions.itervalues()
          if hexlabel in (None, legion.hexlabel)])

    def enemy_legions(self, hexlabel=None):
        """Return a set of other players' legions, in hexlabel if not None."""
        return set([legion for legion in self.game.all_legions(hexlabel)
          if legion.player is not self])

    def can_exit_move_phase(self):
        """Return True iff this player can finish the move phase."""
        if not self.moved_legions():
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
                      legions_in_hex[0].markername,
                      legions_in_hex[1].markername)
                    if split_action is not None:
                        parent_markername = split_action.parent_markername
                        child_markername = split_action.child_markername
                    else:
                        parent_markername = legions_in_hex[0].markername
                        child_markername = legions_in_hex[1].markername
                    self.undo_split(parent_markername, child_markername)
                    # TODO Add an UndoSplit action to history?
                    break
            else:
                return

    def done_with_moves(self):
        if self.can_exit_move_phase():
            self.recombine()
            action = Action.StartFightPhase(self.game.name, self.name)
            self.notify(action)

    def can_exit_fight_phase(self):
        """Return True iff this player can finish the move phase."""
        return (not self.game.engagement_hexlabels and not
          self.game.pending_summon and not self.game.pending_reinforcement
          and not self.game.pending_acquire)

    @property
    def pending_acquire(self):
        for legion in self.legions.itervalues():
            if legion.angels_pending or legion.archangels_pending:
                return True
        return False

    def reset_angels_pending(self):
        for legion in self.legions.itervalues():
            legion.reset_angels_pending()

    def remove_empty_legions(self):
        """Remove any legions with no creatures, caused by summoning out
        the only creature in the legion."""
        for legion in self.legions.itervalues():
            if not legion.creatures:
                self.remove_legion(legion.markername)

    def done_with_engagements(self):
        if self.can_exit_fight_phase():
            action = Action.StartMusterPhase(self.game.name, self.name)
            self.notify(action)

    def can_recruit(self):
        """Return True if any of this player's legions can recruit."""
        for legion in self.legions.itervalues():
            hexlabel = legion.hexlabel
            if (legion.moved and not legion.recruited and len(legion) < 7 and
              legion.can_recruit(self.game.board.hexes[hexlabel].terrain,
              self.game.caretaker)):
                return True
        return False

    def has_forced_strikes(self):
        for creature in self.game.battle_active_legion.creatures:
            if creature.engaged and not creature.struck:
                return True
        return False

    def done_with_recruits(self):
        (player, turn) = self.game.get_next_player_and_turn()
        action = Action.StartSplitPhase(self.game.name, player.name, turn)
        self.notify(action)

    def done_with_reinforcements(self):
        action = Action.StartManeuverBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_maneuvers(self):
        action = Action.StartStrikeBattlePhase(self.game.name, self.name)
        self.notify(action)

    def done_with_strikes(self):
        if self.has_forced_strikes():
            log("Forced strikes remain")
            return
        player = None
        for legion in self.game.battle_legions:
            if legion.player != self:
                player = legion.player
        action = Action.StartCounterstrikeBattlePhase(self.game.name,
          player.name)
        self.notify(action)

    def done_with_counterstrikes(self):
        if self.has_forced_strikes():
            log("Forced strikes remain")
            return
        action = Action.StartReinforceBattlePhase(self.game.name, self.name,
          self.game.battle_turn)
        self.notify(action)

    def summon(self, legion, donor, creature_name):
        """Summon an angel from donor to legion."""
        assert not self.summoned, "player tried to summon twice"
        assert len(legion) < 7, "legion too tall to summon"
        donor.remove_creature_by_name(creature_name)
        legion.add_creature_by_name(creature_name)
        creature = legion.creatures[-1]
        creature.legion = legion
        self.summoned = True
        action = Action.SummonAngel(self.game.name, self.name,
          legion.markername, donor.markername, creature.name)
        self.notify(action)

    def do_not_summon(self, legion):
        """Do not summon an angel into legion."""
        action = Action.DoNotSummon(self.game.name, self.name,
          legion.markername)
        self.notify(action)

    def do_not_reinforce(self, legion):
        """Do not recruit a reinforcement into legion."""
        action = Action.DoNotReinforce(self.game.name, self.name,
          legion.markername)
        self.notify(action)

    def new_turn(self):
        self.selected_markername = None
        self.movement_roll = None
        self.summoned = False
        for legion in self.legions.itervalues():
            legion.moved = False
            legion.teleported = False
            legion.entry_side = None
            legion.previous_hexlabel = None
            legion.recruited = False

    def remove_legion(self, markername):
        """Remove the legion with markername."""
        assert type(markername) == str
        if markername in self.legions:
            legion = self.legions[markername]
            legion.remove_observer(self)
            del self.legions[markername]
            del legion
            self.markernames.add(markername)

    def die(self, scoring_legion, check_for_victory):
        points = sum(legion.score for legion in self.legions.itervalues())
        half_points = points // 2
        scoring_legion.add_points(half_points, False)
        # Make a list to avoid changing size while iterating.
        for legion in self.legions.values():
            self.remove_legion(legion.markername)
        scoring_legion.player.eliminated_colors.add(self.color_abbrev)
        scoring_legion.player.markernames.update(self.markernames)
        action = Action.EliminatePlayer(self.game.name,
          scoring_legion.player.name, self.name)
        self.notify(action)
        if check_for_victory:
            self.game.check_for_victory()

    def update(self, observed, action):
        """Pass updates up to the game"""
        log("update", self, observed, action)
        self.notify(action)
