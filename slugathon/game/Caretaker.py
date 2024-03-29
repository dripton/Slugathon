import logging

from slugathon.data import creaturedata
from slugathon.game import Creature

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Tracks creatures remaining, onboard, and dead."""


class Caretaker(object):

    """Tracks creatures remaining, onboard, and dead."""

    def __init__(self) -> None:
        self.counts = {}
        self.max_counts = {}
        self.graveyard = {}
        for creature_name in creaturedata.data:
            creature = Creature.Creature(creature_name)
            if not creature.is_unknown:
                self.counts[creature.name] = creature.max_count
                self.max_counts[creature.name] = creature.max_count
                self.graveyard[creature.name] = 0

    def num_left(self, creature_name: str) -> int:
        """Return the number of creature_name left in the stacks."""
        return self.counts[creature_name]

    def take_one(self, creature_name: str) -> None:
        """Take one of creature_name off the stack.  Need to ensure that one
        remains before calling this."""
        if self.counts[creature_name] >= 1:
            self.counts[creature_name] -= 1
        else:
            raise AssertionError(f"No {creature_name} left to take")

    def put_one_back(self, creature_name: str) -> None:
        """Put one of creature_name back onto the stack."""
        creature = Creature.Creature(creature_name)
        if creature.is_unknown:
            return
        if self.counts[creature_name] >= creature.max_count:
            logging.info(f"Tried to put too many {creature_name} back")
            self.counts[creature_name] = self.max_counts[creature_name]
        else:
            self.counts[creature_name] += 1

    def kill_one(self, creature_name: str) -> None:
        """If creature_name is mortal, put it in the graveyard.  Otherwise put
        it back onto the stack."""
        creature = Creature.Creature(creature_name)
        if creature.is_creature:
            self.graveyard[creature_name] += 1
        else:
            self.put_one_back(creature_name)

    def number_in_play(self, creature_name: str) -> int:
        """Return the number of creature_name that are currently onboard."""
        return (
            self.max_counts[creature_name]
            - self.counts[creature_name]
            - self.graveyard[creature_name]
        )
