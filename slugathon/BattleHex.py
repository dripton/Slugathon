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

    def hexsides_with_border(self, border):
        """Return the set of hexsides with this border."""
        result = set()
        for hexside, border2 in enumerate(self.borders):
            if border2 == border:
                result.add(hexside)
        return result

