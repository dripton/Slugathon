from __future__ import annotations

import random
import re
from collections import namedtuple
from typing import Optional

__copyright__ = "Copyright (c) 2012-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Parameters for CleverBot."""


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
    "THIRD_CREATURE_RATIO": 0.5,
}

default_keys = [
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
    "THIRD_CREATURE_RATIO",
]

default_keys = list(defaults.keys())


class BotParams(namedtuple("BotParams", default_keys)):  # type: ignore[misc]
    @classmethod
    def fromstring(klass, st: str) -> Optional[BotParams]:
        """Create a BotParams from a string.

        If any fields are missing, populate them with the default then
        mutate them.
        """
        match = re.search(r"BotParams\(.*\)", st)
        if match:
            fields_to_mutate = set()
            st = match.group(0)
            for field, val in defaults.items():
                if field + "=" not in st:
                    st = st.replace(")", f", {field}={val})")
                    fields_to_mutate.add(field)
            bp = eval(st)
            while fields_to_mutate:
                field = fields_to_mutate.pop()
                bp = bp.mutate_field(field)
            return bp
        else:
            return None

    def mutate_field(self, field: str, ratio: float = 0.25) -> BotParams:
        """Return a new BotParams with field mutated by up to ratio."""
        val = getattr(self, field)
        new = random.uniform(val * (1.0 - ratio), val * (1.0 + ratio))
        return self._replace(**{field: new})  # type: ignore

    def mutate_random_field(self, ratio: float = 0.25) -> BotParams:
        """Return a new BotParams with a random field mutated."""
        field = random.choice(self._fields)  # type: str
        return self.mutate_field(field, ratio)

    def mutate_all_fields(self, ratio: float = 0.25) -> BotParams:
        """Return a new BotParams with all fields mutated."""
        dct = self._asdict()
        for key, val in dct.items():
            dct[key] = random.uniform(val * (1.0 - ratio), val * (1.0 + ratio))
        return BotParams(**dct)  # type: ignore

    def cross(self, other: BotParams) -> BotParams:
        """Return a new BotParams based on self and other.

        Each field has a 1/3 chance of copying from self, a 1/3 chance of
        copying from other, and a 1/3 chance of averaging the two.
        """
        dct1 = self._asdict()
        dct2 = other._asdict()
        dct3 = {}
        for field in self._fields:  # type: str
            rand = random.randrange(3)
            if rand == 0:
                dct3[field] = dct1[field]
            elif rand == 1:
                dct3[field] = dct2[field]
            else:
                dct3[field] = (dct1[field] + dct2[field]) / 2.0
        return BotParams(**dct3)  # type: ignore


default_bot_params = BotParams(**defaults)  # type: ignore[call-arg]
