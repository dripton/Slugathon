"""Procedural game rules code."""

import Dice

def assign_towers(towers, num_players, dice=None):
    """Return a list of num_players distinct random tower assignments, in 
    random order.

    towers should be a sequence of distinct numeric tower labels.
    len(towers) must be >= num_players
    """
    if dice is None:
        dice = Dice.Dice()
    assert len(towers) >= num_players
    towers2 = towers[:]
    dice.shuffle(towers2)
    return towers2[:num_players]
