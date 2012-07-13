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


def weighted_random_choice(lst):
    """Return an tuple from a list of tuples, selected randomly but with
    the odds weighted by the value of the first element of each tuple.
    """
    total_score = sum(tup[0] for tup in lst)
    rand = _rand.uniform(0.0, total_score)
    for tup in lst:
        if rand < tup[0]:
            return tup
        else:
            rand -= tup[0]
