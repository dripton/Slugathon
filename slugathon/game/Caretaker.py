__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


"""Tracks creatures remaining, onboard, and dead."""


import logging

from slugathon.data import creaturedata
from slugathon.game import Creature


class Caretaker(object):
    """Tracks creatures remaining, onboard, and dead."""
    def __init__(self):
        self.counts = {}
        self.max_counts = {}
        self.graveyard = {}
        for creature_name in creaturedata.data:
            creature = Creature.Creature(creature_name)
            if not creature.is_unknown:
                self.counts[creature.name] = creature.max_count
                self.max_counts[creature.name] = creature.max_count
                self.graveyard[creature.name] = 0

    def num_left(self, creature_name):
        """Return the number of creature_name left in the stacks."""
        return self.counts[creature_name]

    def take_one(self, creature_name):
        """Take one of creature_name off the stack.  Need to ensure that one
        remains before calling this."""
        if self.counts[creature_name] >= 1:
            self.counts[creature_name] -= 1
        else:
            raise AssertionError("No %s left to take" % creature_name)

    def put_one_back(self, creature_name):
        """Put one of creature_name back onto the stack."""
        creature = Creature.Creature(creature_name)
        if creature.is_unknown:
            return
        if self.counts[creature_name] >= creature.max_count:
            logging.info("Tried to put too many %s back" % creature_name)
            self.counts[creature_name] = self.max_counts[creature_name]
        else:
            self.counts[creature_name] += 1

    def kill_one(self, creature_name):
        """If creature_name is mortal, put it in the graveyard.  Otherwise put
        it back onto the stack."""
        creature = Creature.Creature(creature_name)
        if creature.is_creature:
            self.graveyard[creature_name] += 1
        else:
            self.put_one_back(creature_name)

    def number_in_play(self, creature_name):
        """Return the number of creature_name that are currently onboard."""
        return (self.max_counts[creature_name] - self.counts[creature_name] -
          self.graveyard[creature_name])
