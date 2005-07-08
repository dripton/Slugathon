from Observed import Observed
import Action
import playercolordata
import creaturedata
import Creature
import Legion
import rules
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

    def __repr__(self):
        return "Player " + self.name

    def assign_starting_tower(self, tower):
        """Set this player's starting tower to the (int) tower"""
        self.starting_tower = tower
        action = Action.AssignTower(self.game_name, self.name, tower)
        self.notify(action)

    def assign_color(self, color):
        """Set this player's color"""
        self.color = color
        action = Action.PickedColor(self.game_name, self.name, color)
        abbrev = playercolordata.name_to_abbrev[self.color]
        # TODO Un-hardcode
        for ii in xrange(12):
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
        if not rules.is_legal_split(parent, new_legion1, new_legion2):
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

    def done_with_splits(self):
        if not self.can_exit_split_phase():
            return
        self.movement_roll = Dice.roll()
        action = Action.RollMovement(self.game_name, self.name, 
          self.movement_roll)
        self.notify(action)
