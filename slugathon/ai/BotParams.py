__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


"""Parameters for CleverBot."""


from collections import namedtuple
import random
import re


# TODO Use an OrderedDict to combine these, once we require Python 2.7

fields = [
    "SQUASH",
    "BE_SQUASHED",
    "FLEE_RATIO",
    "ATTACKER_AGGRESSION_BONUS",
    "ATTACKER_DISTANCE_PENALTY",
    "HIT_BONUS",
    "KILL_MULTIPLIER",
    "DAMAGE_PENALTY",
    "DEATH_MULTIPLIER",
    "ELEVATION_BONUS",
    "NATIVE_BRAMBLE_BONUS",
    "NON_NATIVE_BRAMBLE_PENALTY",
    "TOWER_BONUS",
    "FRONT_OF_TOWER_BONUS",
    "MIDDLE_OF_TOWER_BONUS",
    "CENTER_OF_TOWER_BONUS",
    "TITAN_IN_CENTER_OF_TOWER_BONUS",
    "NON_NATIVE_DRIFT_PENALTY",
    "NATIVE_VOLCANO_BONUS",
    "ADJACENT_ALLY_BONUS",
    "RANGESTRIKE_BONUS",
    "TITAN_FORWARD_PENALTY",
    "DEFENDER_FORWARD_PENALTY",
    "NATIVE_SLOPE_BONUS",
    "NATIVE_DUNE_BONUS",
    "NON_NATIVE_SLOPE_PENALTY",
    "NON_NATIVE_DUNE_PENALTY",
    "ENGAGE_RANGESTRIKER_BONUS",
]


defaults = {
    "SQUASH": 0.6,
    "BE_SQUASHED": 1.0,
    "FLEE_RATIO": 1.5,
    "ATTACKER_AGGRESSION_BONUS": 1.0,
    "ATTACKER_DISTANCE_PENALTY": -1.0,
    "HIT_BONUS": 1.0,
    "KILL_MULTIPLIER": 1.0,
    "DAMAGE_PENALTY": -1.0,
    "DEATH_MULTIPLIER": -1.0,
    "ELEVATION_BONUS": 0.5,
    "NATIVE_BRAMBLE_BONUS": 0.3,
    "NON_NATIVE_BRAMBLE_PENALTY": -0.7,
    "TOWER_BONUS": 1.0,
    "FRONT_OF_TOWER_BONUS": 0.5,
    "MIDDLE_OF_TOWER_BONUS": 0.25,
    "CENTER_OF_TOWER_BONUS": 1.0,
    "TITAN_IN_CENTER_OF_TOWER_BONUS": 2.0,
    "NON_NATIVE_DRIFT_PENALTY": -2.0,
    "NATIVE_VOLCANO_BONUS": 1.0,
    "ADJACENT_ALLY_BONUS": 0.5,
    "RANGESTRIKE_BONUS": 2.0,
    "TITAN_FORWARD_PENALTY": -1.0,
    "DEFENDER_FORWARD_PENALTY": -0.5,
    "NATIVE_SLOPE_BONUS": 0.5,
    "NATIVE_DUNE_BONUS": 0.5,
    "NON_NATIVE_SLOPE_PENALTY": -0.3,
    "NON_NATIVE_DUNE_PENALTY": -0.3,
    "ENGAGE_RANGESTRIKER_BONUS": 0.5,
}


class BotParams(namedtuple("BotParams", fields)):

    @classmethod
    def fromstring(klass, st):
        """Create a BotParams from a string."""
        match = re.search(r"BotParams\(.*\)", st)
        if match:
            st = match.group(0)
            return eval(st)
        else:
            return None

    def mutate_field(self, field, ratio=0.25):
        """Return a new BotParams with field mutated by up to ratio."""
        val = getattr(self, field)
        new = random.uniform(val * (1.0 - ratio), val * (1.0 + ratio))
        return self._replace(**{field: new})

    def mutate_random_field(self, ratio=0.25):
        """Return a new BotParams with a random field mutated."""
        field = random.choice(self._fields)
        return self.mutate_field(field, ratio)

    def mutate_all_fields(self, ratio=0.25):
        """Return a new BotParams with all fields mutated."""
        dct = self._asdict()
        for key, val in dct.iteritems():
            dct[key] = random.uniform(val * (1.0 - ratio), val * (1.0 + ratio))
        return BotParams(**dct)

    def cross(self, other):
        """Return a new BotParams based on self and other.

        Each field has a 1/3 chance of copying from self, a 1/3 chance of
        copying from other, and a 1/3 chance of averaging the two.
        """
        dct1 = self._asdict()
        dct2 = other._asdict()
        dct3 = {}
        for field in self._fields:
            rand = random.randrange(3)
            if rand == 0:
                dct3[field] = dct1[field]
            elif rand == 1:
                dct3[field] = dct2[field]
            else:
                dct3[field] = (dct1[field] + dct2[field]) / 2.0
        return BotParams(**dct3)


default_bot_params = BotParams(**defaults)
