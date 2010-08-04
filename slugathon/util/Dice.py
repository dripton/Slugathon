__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"

"""Simulate rolling dice.

Runs only on the server side, for security.
"""

import random


_rand = random.Random()

def roll(numrolls=1, sides=6):
    """Return a list of numrolls random integers from 1..sides"""
    return [_rand.randint(1, sides) for unused in xrange(numrolls)]

def shuffle(lst):
    """Shuffle the list in place.

    Here so that we can reuse the same RNG for the whole game.
    """
    _rand.shuffle(lst)
