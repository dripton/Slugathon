from twisted.spread import pb

from Observed import Observed
import Action
import playercolordata
import creaturedata
import Creature
import Legion


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
        self.markers = set()
        # Private to this instance; not shown to others until a
        # legion is actually split off with this marker.
        self.selected_marker = None
        self.legions = []

    def __str__(self):
        return self.name

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
        for ii in range(12):
            self.markers.add("%s%02d" % (abbrev, ii + 1))
        self.notify(action)

    def pick_marker(self, marker):
        if marker in self.markers:
            self.selected_marker = marker

    def init_starting_legion(self):
        assert self.selected_marker 
        assert self.selected_marker in self.markers
        action = Action.CreateStartingLegion(self.game_name, self.name,
          self.selected_marker)
        self.notify(action)

    def take_marker(self, marker):
        assert marker in self.markers
        self.markers.remove(marker)
        self.selected_marker = None
        return marker

    def create_starting_legion(self, marker):
        assert marker in self.markers
        assert len(self.legions) == 0
        creatures = [Creature.Creature(name) for name in 
          creaturedata.starting_creature_names]
        legion = Legion.Legion(self, self.take_marker(marker), creatures,
          self.starting_tower)
        self.legions.append(legion)
