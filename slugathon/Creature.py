__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


import creaturedata
import recruitdata
import battlemapdata


def _terrain_to_hazards():
    """Return a dict of masterboard terrain type to a set of all
    battle hazards (hex and hexside) found there."""
    result = {}
    for mterrain, dic2 in battlemapdata.data.iteritems():
        for hexlabel, (bterrain, elevation, dic3) in dic2.iteritems():
            set1 = result.setdefault(mterrain, set())
            set1.add(bterrain)
            for hexside, border in dic3.iteritems():
                if border:
                    set1.add(border)
    return result

def _terrain_to_creature_names():
    """Return a dict of masterboard terrain type to a set of all
    Creature names that can be recruited there."""
    result = {}
    for terrain, tuples in recruitdata.data.iteritems():
        set1 = set()
        result[terrain] = set1
        for tup in tuples:
            if tup:
                creature_name, count = tup
                if count:
                    set1.add(creature_name)
    return result

def _compute_nativity():
    """Return a dict of creature name to a set of all hazards
    (battle terrain types and border types) to which it is
    native."""
    result = {}
    terrain_to_creature_names = _terrain_to_creature_names()
    terrain_to_hazards = _terrain_to_hazards()
    for terrain, creature_names in terrain_to_creature_names.iteritems():
        hazards = terrain_to_hazards.get(terrain, set())
        for creature_name in creature_names:
            set1 = result.setdefault(creature_name, set())
            for hazard in hazards:
                # Special case: Only Dragon is native to Volcano
                if hazard != "Volcano" or creature_name == "Dragon":
                    set1.add(hazard)
    return result

creature_name_to_native_hazards = _compute_nativity()


def n2c(names):
    """Make a list of Creatures from a list of creature names"""
    return [Creature(name) for name in names]


class Creature(object):
    """One instance of one Creature, Lord, or Demi-Lord."""
    def __init__(self, name):
        self.name = name
        (self.plural_name, self.power, self.skill, rangestrikes, self.flies,
          self.character_type, self.summonable, self.acquirable_every,
          self.max_count, self.color_name) = creaturedata.data[name]
        self.rangestrikes = bool(rangestrikes)
        self.magicmissile = (rangestrikes == 2)
        self.acquirable = bool(self.acquirable_every)
        self.hits = 0
        self.moved = False
        self.struck = False
        self.hexlabel = None
        self.previous_hexlabel = None
        self.legion = None

    def __repr__(self):
        if self.name == "Titan":
            return "%s(%d)" % (self.name, self.power)
        else:
            return self.name

    def score(self):
        """Return the point value of this creature."""
        return self.power * self.skill

    def sort_value(self):
        """Return a rough indication of creature value, for sorting."""
        return (self.score()
          + 0.2 * self.acquirable
          + 0.3 * self.flies
          + 0.25 * self.rangestrikes
          + 0.1 * self.magicmissile
          + 0.15 * (self.skill == 2)
          + 0.18 * (self.skill == 4)
          + 100 * (self.name == "Titan"))

    def is_dead(self):
        return self.hits >= self.power

    def engaged_enemies(self):
        """Return a set of enemy Creatures this Creature is engaged with."""
        enemies = set()
        if self.is_offboard():
            return enemies
        hexlabel_to_enemy = {}
        game = self.legion.player.game
        legion2 = game.other_battle_legion(self.legion)
        for creature in legion2.creatures:
            if not creature.is_dead():
                hexlabel_to_enemy[creature.hexlabel] = creature
        hex1 = game.battlemap.hexes[self.hexlabel]
        for hexside, hex2 in hex1.neighbors.iteritems():
            hexlabel = hex2.label
            if hexlabel in hexlabel_to_enemy:
                if (hex1.borders[hexside] != "Cliff" and
                  hex2.borders[(hexside + 3) % 6] != "Cliff"):
                    enemies.add(hexlabel_to_enemy[hexlabel])
        return enemies

    def is_engaged(self):
        """Return True iff this creature is engaged with an adjacent enemy."""
        return bool(self.engaged_enemies())

    def is_mobile(self):
        """Return True iff this creature can move."""
        return not self.moved and not self.is_dead() and not self.is_engaged()

    def is_native(self, hazard):
        """Return True iff this creature is native to the named hazard.

        Note that we define nativity even for hazards that don't provide any
        benefit for being native, like Wall and Plains.
        """
        return hazard in creature_name_to_native_hazards.get(self.name, set())

    def move(self, hexlabel):
        """Move this creature to a new battle hex"""
        self.previous_hexlabel = self.hexlabel
        self.hexlabel = hexlabel
        self.moved = True

    def undo_move(self):
        """Undo this creature's last battle move."""
        assert self.moved and self.previous_hexlabel
        self.hexlabel = self.previous_hexlabel
        self.previous_hexlabel = None
        self.moved = False

    def can_strike(self):
        """Return True iff this creature can strike."""
        return not self.struck and (self.is_engaged() or
          self.can_rangestrike())

    # TODO
    def can_rangestrike(self):
        """Return True iff this creature can rangestrike an enemy."""
        return False

    # TODO strike penalties to carry
    # TODO terrain bonuses and penalties
    # TODO rangestrike
    def number_of_dice(self, target):
        """Return the number of dice to use if striking target."""
        return self.power

    # TODO strike penalties to carry
    # TODO terrain bonuses and penalties
    def strike_number(self, target):
        """Return the strike number to use if striking target."""
        return min(4 - self.skill + target.skill, 6)

    def is_offboard(self):
        return self.hexlabel == "ATTACKER" or self.hexlabel == "DEFENDER"
