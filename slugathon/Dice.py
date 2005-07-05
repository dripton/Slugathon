import random

class Dice(object):
    """Simulate rolling dice.

    Runs only on the server side, for security.
    """
    def __init__(self):
        self.rand = random.Random()

    def roll(self, sides=6, numrolls=1):
        """Return a list of numrolls random integers from 1..sides"""
        return [self.rand.randint(1, sides) for unused in xrange(numrolls)]

    def shuffle(self, lst):
        """Shuffle the list in place.

        Here so that we can reuse the same RNG for the whole game.
        """
        self.rand.shuffle(lst)
