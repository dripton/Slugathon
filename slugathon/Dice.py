import random

class Dice:
    """Simulate rolling dice.

       Runs only on the server side, for security.
    """
    def __init__(self, seed=None):
        self.rand = random.Random()

    def roll(self, sides=6, numrolls=1):
        """Return a list of numrolls random integers from 1..sides"""
        return [self.rand.randint(1, sides) for unused in range(numrolls)]
