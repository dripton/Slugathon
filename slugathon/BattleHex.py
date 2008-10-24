class BattleHex(object):
    """A logical hex on a battle map.  No GUI logic.

    Hex vertexes are numbered like:
     
        0        1
         --------
        /        \
       /          \
      /            \ 2
    5 \            /
       \          /
        \        /
         --------
        4        3
    """

    def __init__(self, battlemap, label, x, y, terrain, elevation, borderdict):
        self.battlemap = battlemap
        self.label = label
        self.x = x
        self.y = y
        self.terrain = terrain
        self.elevation = elevation
        # TODO Perhaps borders should be objects rather than strings?
        self.borders = []
        for ii in xrange(6):
            self.borders.append(borderdict.get(ii))
        self.down = (self.x & 1 == 1)
        self.label_side = 5
        self.terrain_side = 3
        self.entrance = (self.label in ["ATTACKER", "DEFENDER"])
        self.visible = not self.entrance
        self.neighbors = {}   # hexside : BattleHex

    def __repr__(self):
        return "BattleHex %s (%d, %d)" % (self.label, self.x, self.y)

    def init_neighbors(self):
        """Called from BattleMap after all hexes are initialized."""
        if self.entrance:
            # hexsides don't really matter for entrances
            hexside = 0
            for hex1 in self.battlemap.hexes.itervalues():
                if abs(hex1.x - self.x) == 1:
                    self.neighbors[hexside] = hex1
                    hexside += 1
        else:
            for hex1 in self.battlemap.hexes.itervalues():
                if hex1.entrance:
                    pass
                elif hex1.x == self.x:
                    if hex1.y == self.y - 1:
                        self.neighbors[0] = hex1
                    elif hex1.y == self.y + 1:
                        self.neighbors[3] = hex1
                elif hex1.x == self.x + 1:
                    if hex1.y == self.y:
                        if self.x & 1:
                            self.neighbors[1] = hex1
                        else:
                            self.neighbors[2] = hex1
                    elif hex1.y == self.y - 1:
                        if self.x & 1 == 0:
                            self.neighbors[1] = hex1
                    elif hex1.y == self.y + 1:
                        if self.x & 1:
                            self.neighbors[2] = hex1
                elif hex1.x == self.x - 1:
                    if hex1.y == self.y:
                        if self.x & 1:
                            self.neighbors[5] = hex1
                        else:
                            self.neighbors[4] = hex1
                    elif hex1.y == self.y - 1:
                        if self.x & 1 == 0:
                            self.neighbors[5] = hex1
                    elif hex1.y == self.y + 1:
                        if self.x & 1:
                            self.neighbors[4] = hex1


    def hexsides_with_border(self, border):
        """Return the set of hexsides with this border."""
        result = set()
        for hexside, border2 in enumerate(self.borders):
            if border2 == border:
                result.add(hexside)
        return result

