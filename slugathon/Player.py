class Player:
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
