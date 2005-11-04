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

def label_to_coords(label):
    """Convert a hex label to a tuple of X and Y coordinates, starting at the
    bottom left.

    This works on the unrotated map.
   
    5          *
    4    *  *  *  *  *
    3 *  *  *  *  *  *
    2 *  *  *  *  *  *
    1 *  *  *  *  *  *
    0       *  *  *
      0  1  2  3  4  5
     
    """
    if label not in all_labels:
        raise KeyError, "bad battle hex label"
    letter = label[0]
    xx = ord(letter) - ord("A")
    number = label[1]
    if 2 <= xx <= 4:
        yy = int(number) - 1
    else:
        yy = int(number)
    return (xx, yy)


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
            x, y = label_to_coords(label)
            if label in mydata:
                self.hexes[label] = BattleHex.BattleHex(self, label, x, y, 
                  *mydata[label])
            else:
                self.hexes[label] = BattleHex.BattleHex(self, label, x, y, 
                  "Plains", 0, {})

    def hex_width(self):
        """Width of the map, in hexes."""
        return 6

    def hex_height(self):
        """Height of the map, in hexes."""
        return 6

