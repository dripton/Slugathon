import creaturedata

class Creature(object):
    """One instance of one Creature, Lord, or Demi-Lord."""
    def __init__(self, name):
        self.name = name
        (self.plural_name, self.power, self.skill, rangestrikes, self.flies,
          self.characterType, self.summonable, acquirable_every, 
          self.max_count, self.color_name) = creaturedata.data[name]
        self.rangestrikes = bool(rangestrikes)
        self.magicmissile = (rangestrikes == 2)
        self.acquirable = bool(acquirable_every)
        self.acquirable_every = acquirable_every
