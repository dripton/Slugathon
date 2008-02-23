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

def label_to_coords(label, entry_side):
    """Convert a hex label to a tuple of X and Y coordinates, starting at the
    bottom left.

    We spin the map so that the attacker's entry side is always on the left.
    This works on the rotated map.
   
    5       *   
    4 *  *  *  *  *   
    3 *  *  *  *  *  *
    2 *  *  *  *  *  *
    1 *  *  *  *  *  *
    0    *  *  *   
      0  1  2  3  4  5

    entry_side 1:

               D1 
            E1    C1 
    A    F1    D2    B1       D
    T       E2    C2    A1    E
    T    F2    D3    B2       F
    A       E3    C3    A2    E
    C    F3    D4    B3       N
    K       E4    C4    A3    D
    E    F4    D5    B4       E
    R       E5    C5          R
               D6

    entry_side 3:

               A3 
            A2    B4 
    A    A1    B3    C1       D
    T       B2    C4    D6    E
    T    B1    C3    D5       F
    A       C2    D4    E5    E
    C    C1    D3    E4       N
    K       D2    E3    F4    D
    E    D1    E2    F3       E
    R       E1    F2          R
               F1

    entry_side 5:

               F4 
            E5    F3 
    A    D6    E4    F2       D
    T       D5    E3    F1    E
    T    C5    D4    E2       F
    A       C4    D3    E1    E
    C    B4    C3    D2       N
    K       B3    C2    D1    D
    E    A3    B2    C1       E
    R       A2    B1          R
               A1
    """
    if label not in all_labels:
        raise KeyError, "bad battle hex label"
    l2c = {}
    l2c[1] = {
        "A1": (5, 1), "A2": (5, 2), "A3": (5, 3),
        "B1": (4, 1), "B2": (4, 2), "B3": (4, 3), "B4": (4, 4),
        "C1": (3, 0), "C2": (3, 1), "C3": (3, 2), "C4": (3, 3), "C5": (3, 4),
        "D1": (2, 0), "D2": (2, 1), "D3": (2, 2), "D4": (2, 3), "D5": (2, 4), 
          "D6": (2, 5),
        "E1": (1, 0), "E2": (1, 1), "E3": (1, 2), "E4": (1, 3), "E5": (1, 4),
        "F1": (0, 1), "F2": (0, 2), "F3": (0, 3), "F4": (0, 4),
    }
    l2c[3] = {
        "A1": (2, 5), "A2": (1, 4), "A3": (0, 4),
        "B1": (3, 4), "B2": (2, 4), "B3": (1, 3), "B4": (0, 3),
        "C1": (4, 4), "C2": (3, 3), "C3": (2, 3), "C4": (1, 2), "C5": (0, 2),
        "D1": (5, 3), "D2": (4, 3), "D3": (3, 2), "D4": (2, 2), "D5": (1, 1), 
          "D6": (0, 1),
        "E1": (5, 2), "E2": (4, 2), "E3": (3, 1), "E4": (2, 1), "E5": (1, 0),
        "F1": (5, 1), "F2": (4, 1), "F3": (3, 0), "F4": (2, 0),
    }
    l2c[5] = {
        "A1": (0, 1), "A2": (1, 0), "A3": (2, 0),
        "B1": (0, 2), "B2": (1, 1), "B3": (2, 1), "B4": (3, 0),
        "C1": (0, 3), "C2": (1, 2), "C3": (2, 2), "C4": (3, 1), "C5": (4, 1),
        "D1": (0, 4), "D2": (1, 3), "D3": (2, 3), "D4": (3, 2), "D5": (4, 2), 
          "D6": (5, 1),
        "E1": (1, 4), "E2": (2, 4), "E3": (3, 3), "E4": (4, 3), "E5": (5, 2),
        "F1": (2, 5), "F2": (3, 4), "F3": (4, 4), "F4": (5, 3),
    }
    return l2c[entry_side][label]



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

    def __init__(self, terrain, entry_side):
        self.hexes = {}
        self.entry_side = entry_side
        mydata = battlemapdata.data[terrain]
        for label in all_labels:
            x, y = label_to_coords(label, entry_side)
            if label in mydata:
                terrain, elevation, hexside_dict = mydata[label]
                spun_hexside_dict = self.spin_border_dict(hexside_dict, 
                  entry_side)
                self.hexes[label] = BattleHex.BattleHex(self, label, x, y, 
                  terrain, elevation, spun_hexside_dict)
            else:
                self.hexes[label] = BattleHex.BattleHex(self, label, x, y, 
                  "Plains", 0, {})

    def hex_width(self):
        """Width of the map, in hexes."""
        return 6

    def hex_height(self):
        """Height of the map, in hexes."""
        return 6

    def spin_border_dict(self, border_dict, entry_side):
        """Return a new dict with the keys (hexsides) rotated by entry_side"""
        spun = {}
        entry_side_to_delta = {1: 3, 3: 1, 5: 5}
        delta = entry_side_to_delta[entry_side]
        for key, val in border_dict.iteritems():
            spun[(key + delta) % 6] = val
        return spun
