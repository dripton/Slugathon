import time
from twisted.spread import pb

class Game(pb.Copyable, pb.RemoteCopy):
    """Central class holding information about one game.
    
       This class is remote-copyable, and so must contain only public
       information.
    """

    def __init__(self, name, owner, create_time, start_time, min_players,
      max_players):
        self.name = name
        self.owner = owner
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
        self.players = [owner]
        self.started = False

    def __eq__(self, other):
        return isinstance(other, Game) and self.name == other.name

    def to_tuple(self):
        """Return state as a tuple of strings for GUI presentation."""
        return (self.name, self.owner, time.ctime(self.create_time),
          time.ctime(self.start_time), self.min_players, self.max_players,
          ', '.join(self.players))

    def remove_player(self, player):
        self.players.remove(player)
        if player == self.owner:
            self.owner = self.players[0]

    def add_player(self, player):
        self.players.append(player)

pb.setUnjellyableForClass(Game, Game)
