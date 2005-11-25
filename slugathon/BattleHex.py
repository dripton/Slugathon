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
        # XXX borders should probably not be 1-char strings
        self.borders = []
        for ii in xrange(6):
            self.borders.append(borderdict.get(ii, " "))
        self.down = (self.x & 1 == 0)
        self.label_side = 5
        self.terrain_side = 3
