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

    def is_engaged(self):
        """Return True iff this creature is engaged with an adjacent enemy"""
        # TODO
        return False

    def is_native(self, hazard):
        """Return True iff this creature is native to the named hazard.
        
        Note that we define nativity even for hazards that don't provide any
        benefit for being native, like Wall and Plains.
        """
        return hazard in creature_name_to_native_hazards.get(self.name, set())
