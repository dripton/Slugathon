import types

from Observed import Observed
import Action
import playercolordata
import creaturedata
import markerdata
import Creature
import Legion
from bag import bag
import Dice


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
    def __init__(self, playername, game_name, join_order):
        Observed.__init__(self)
        self.name = playername
        self.game_name = game_name
        self.join_order = join_order
        self.starting_tower = None    # a numeric hex label
        self.score = 0
        self.color = None
        self.markernames = set()
        # Private to this instance; not shown to others until a
        # legion is actually split off with this marker.
        self.selected_markername = None
        self.legions = {}
        self.mulligans_left = 1
        self.movement_roll = None
        self.teleported = False

    def __repr__(self):
        return "Player " + self.name

    def assign_starting_tower(self, tower):
        """Set this player's starting tower to the (int) tower"""
        assert type(tower) == types.IntType
        self.starting_tower = tower
        action = Action.AssignTower(self.game_name, self.name, tower)
        self.notify(action)

    def assign_color(self, color):
        """Set this player's color"""
        self.color = color
        action = Action.PickedColor(self.game_name, self.name, color)
        abbrev = playercolordata.name_to_abbrev[self.color]
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
        action = Action.CreateStartingLegion(self.game_name, self.name,
          markername)
        self.notify(action)

    def split_legion(self, parent_markername, child_markername,
      parent_creaturenames, child_creaturenames):
        parent = self.legions[parent_markername]
        if not child_markername in self.markernames:
            raise AssertionError("illegal marker")
        if bag(parent.creature_names()) != bag(parent_creaturenames).union(
          bag(child_creaturenames)):
            raise AssertionError("wrong creatures")
        new_legion1 = Legion.Legion(self, parent_markername, 
          Creature.n2c(parent_creaturenames), parent.hexlabel)
        new_legion2 = Legion.Legion(self, child_markername, 
          Creature.n2c(child_creaturenames), parent.hexlabel)
        if not parent.is_legal_split(new_legion1, new_legion2):
            raise AssertionError("illegal split")
        self.take_marker(child_markername)
        for creaturename in child_creaturenames:
            parent.remove_creature_by_name(creaturename)
        self.legions[child_markername] = new_legion2
        # TODO One action for our player with creature names, and a 
        # different action for other players without.
        action = Action.SplitLegion(self.game_name, self.name, 
          parent_markername, child_markername, parent_creaturenames, 
          child_creaturenames)
        self.notify(action)

    def can_exit_split_phase(self):
        """Return True if legal to exit the split phase"""
        return max([len(legion) for legion in self.legions.values()]) < 8

    def _roll_movement(self):
        self.movement_roll = Dice.roll()[0]
        action = Action.RollMovement(self.game_name, self.name, 
          self.movement_roll)
        self.notify(action)

    def done_with_splits(self):
        if self.can_exit_split_phase():
            self._roll_movement()

    def can_take_mulligan(self, game):
        """Return True iff this player can take a mulligan"""
        return bool(self is game.active_player and game.turn == 1 
          and game.phase == Phase.MOVE and self.mulligans_left)

    def take_mulligan(self):
        self.mulligans_left -= 1
        self._roll_movement()

    def can_titan_teleport(self):
        return self.score >= 400

    def moved_legions(self):
        return [legion for legion in self.legions if legion.moved]

    def friendly_legions(self, hexlabel=None):
        """Return a list of this player's legions, in hexlabel if not None."""
        return [legion for legion in self.legions.values() if hexlabel in
          (None, legion.hexlabel)]

    def enemy_legions(self, game, hexlabel=None):
        """Return a list of other players' legions, in hexlabel if not None."""
        return [legion for legion in game.all_legions(hexlabel) 
          if legion.player is not self]

    def can_exit_move_phase(self, game):
        """Return True iff this player can finish the move phase."""
        if not self.moved_legions():
            return False
        for legion in self.friendly_legions():
            if self.friendly_legions(legion.hexlabel) >= 2:
                if not legion.moved and game.find_all_moves(legion, 
                  game.board.hexes[legion.hexlabel], self.movement_roll):
                    return False
            # else will need to recombine
        return True

    def done_with_moves(self, game):
        if self.can_exit_move_phase(game):
            action = Action.DoneMoving(self.game_name, self.name)
            self.notify(action)
