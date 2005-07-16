"""Tracks creatures remaining, onboard, and dead."""

import creaturedata
import Creature

class Caretaker(object):
    """Tracks creatures remaining, onboard, and dead."""
    def __init__(self):
        self.counts = {}
        self.max_counts = {}
        self.graveyard = {}
        for creaturename in creaturedata.data:
            creature = Creature.Creature(creaturename)
            self.counts[creature.name] = creature.max_count
            self.max_counts[creature.name] = creature.max_count
            self.graveyard[creature.name] = 0

    def num_left(self, creaturename):
        """Return the number of creaturename left in the stacks."""
        return self.counts[creaturename]

    def take_one(self, creaturename):
        """Take one of creaturename off the stack.  Need to ensure that one
        remains before calling this."""
        if self.counts[creaturename] >= 1:
            self.counts[creaturename] -= 1
        else:
            raise AssertionError("No %s left to take" % creaturename)

    def put_one_back(self, creaturename):
        """Put one of creaturename back onto the stack."""
        creature = Creature.Creature(creaturename)
        if self.counts[creaturename] >= creature.max_count:
            raise AssertionError("Put too many %s back" % creaturename)
        self.counts[creaturename] += 1

    def kill_one(self, creaturename):
        """If creaturename is mortal, put it in the graveyard.  Otherwise put
        it back onto the stack."""
        creature = Creature.Creature(creaturename)
        if creature.character_type == "creature":
            self.graveyard[creaturename] += 1
        else:
            self.put_one_back(creaturename)

    def number_in_play(self, creaturename):
        """Return the number of creaturename that are currently onboard."""
        return (self.max_counts[creaturename] - self.counts[creaturename] - 
          self.graveyard[creaturename])
