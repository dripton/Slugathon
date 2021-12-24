import random
from typing import Any, List, Tuple

__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Simulate rolling dice.

Runs only on the server side, for security.
"""


_rand = random.Random()


def roll(numrolls: int = 1, sides: int = 6) -> List[int]:
    """Return a list of numrolls random integers from 1..sides"""
    return [_rand.randint(1, sides) for unused in range(numrolls)]


def shuffle(lst: List[Any]) -> None:
    """Shuffle the list in place.

    Here so that we can reuse the same RNG for the whole game.
    """
    _rand.shuffle(lst)


def weighted_random_choice(lst: List[Tuple[float, Any]]) -> Tuple[float, Any]:
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
    # Should be unreachable but makes mypy happy
    assert False
    return lst[-1]
