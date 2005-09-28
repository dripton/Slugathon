import battlemapdata
import BattleHex


def init_all_labels():
    """Return a frozen set containing all hex labels mentioned in 
    battlemapdata"""
    labelset = set()
    for v in battlemapdata.data.itervalues():
        for k in v.iterkeys():
            labelset.add(k)
    return frozenset(labelset)

all_labels = init_all_labels()


class BattleMap(object):
    """A logical battle map.  No GUI code.
    
    Hexes are labeled like:

             D6 
          C5    E5
       B4    D5    F4
    A3    C4    E4
       B3    D4    F3
    A2    C3    E3
       B2    D3    F2
    A1    C2    E2
       B1    D2    F1
          C1    E1
             D1
    """

    def __init__(self, terrain):
        self.hexes = {}
        mydata = battlemapdata.data[terrain]
        for label in all_labels:
            if label in mydata:
                self.hexes[label] = BattleHex.BattleHex(*mydata[label])
            else:
                self.hexes[label] = BattleHex.BattleHex("Plains", 0, {})
