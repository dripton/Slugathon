import creaturedata

class Creature:
    """One instance of one Creature, Lord, or Demi-Lord."""
    def __init__(self, name, legion=None):
        self.name = name
        (self.pluralName, self.power, self.skill, rangestrikes, self.flies,
          self.characterType, self.summonable, acquirableEvery, self.maxCount,
          self.colorName) = creaturedata.data[name]
        self.rangestrikes = bool(rangestrikes)
        self.magicmissile = (rangestrikes == 2)
        self.acquirable = bool(acquirableEvery)
        self.acquirableEvery = acquirableEvery
        self.legion = legion
