from twisted.spread import pb

class Player(pb.Copyable, pb.RemoteCopy):
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
    def __init__(self, name):
        self.name = name
        self.starting_tower = None    # a numeric hex label
        self.score = 0
        self.observers = []

    def add_observer(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for obs in self.observers:
            obs.update(self)

    def __str__(self):
        return self.name

    def assign_starting_tower(self, tower):
        """Set this player's starting tower to the (int) tower"""
        self.starting_tower = tower
        self.notify_observers()


# TODO Create a client-side proxy without private data.
pb.setUnjellyableForClass(Player, Player)
