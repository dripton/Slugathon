"""Procedural game rules code."""

import Dice
from bag import bag

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

def is_legal_split(parent, child1, child2):
    """Return whether the split of legion parent into legions child1 and
    child2 is legal."""
    if len(parent) < 4:
        return False
    if len(parent) != len(child1) + len(child2):
        return False
    if not bag(parent.creatures) == bag(child1.creatures + child2.creatures):
        return False
    if len(parent) == 8:
        if len(child1) != 4 or len(child2) != 4:
            return False
        if child1.num_lords() != 1 or child2.num_lords() != 1:
            return False
    return True
