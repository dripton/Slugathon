from twisted.spread import pb

from Observed import Observed
import Action

class Player(Observed):
    """A person or AI who is (or was) actively playing in a game.

       Note that players are distinct from users.  A user could be just
       chatting or observing, not playing.  A user could be playing in
       more than one game, or could be controlling more than one player
       in a game.  (Server owners might disallow these scenarios to 
       prevent cheating or encourage quick play, but that's policy not 
       mechanism, and our mechanisms should be flexible enough to handle
       these cases.)  A user might drop his connection, and another user 
       might take over his player can continue the game.
    """
    def __init__(self, name, join_order):
        Observed.__init__(self)
        self.name = name
        self.join_order = join_order
        self.starting_tower = None    # a numeric hex label
        self.score = 0
        self.color = None

    def __str__(self):
        return self.name

    def assign_starting_tower(self, tower):
        """Set this player's starting tower to the (int) tower"""
        self.starting_tower = tower
        action = Action.AssignTower(self.name, tower)
        self.notify(action)

    def assign_color(self, color):
        """Set this player's color"""
        self.color = color
