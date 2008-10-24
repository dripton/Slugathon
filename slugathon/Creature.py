import creaturedata

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

    def find_moves(self):
        """Return a set of all hexlabels to which this creature can move.
        
        Its current hex is not included.
        """
        result = set()
        if self.moved or self.is_engaged():
            return result
        movement_points = self.skill
