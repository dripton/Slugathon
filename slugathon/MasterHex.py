from twisted.spread import pb

BIGNUM = 99999999

class MasterHex:
    """A logical MasterBoard hex.  No GUI logic.

    Hex vertexes are numbered like this:

                   normal                     inverted

                  0------1                  0------------1
                 /        \                /              \
                /          \              /                \
               /            \            /                  \
              /              \          5                    2
             /                \          \                  /
            /                  \          \                /
           5                    2          \              /
            \                  /            \            /
             \                /              \          /
              \              /                \        /
               4------------3                  4------3
    """

    def __init__(self, board, label, x, y, terrain, exits):
        self.board = board
        self.label = label
        self.x = x
        self.y = y
        self.inverted = ((self.x + self.y) & 1 == 0)
        self.terrain = terrain
        self._exits = exits
        self.exits = []
        self.entrances = []
        self.neighbors = []
        for unused in range(6):
            self.exits.append(None)
            self.entrances.append(None)
            self.neighbors.append(None)
        self.build_overlay_filename()
        self.label_side = self.find_label_side()

    def __str__(self):
        return "%s hex %d at (%d,%d)" % (self.terrain, self.label,
                                         self.x, self.y)

    def connect_to_neighbors(self):
        it = iter(self._exits)
        for (neighbor_label, gate_type) in zip(it, it):
            direct = self.find_direction(neighbor_label)
            self.exits[direct] = gate_type
            neighbor = self.board.hexes[neighbor_label]
            self.neighbors[direct] = neighbor
            neighbor.neighbors[(direct + 3) % 6] = self
            neighbor.entrances[(direct + 3) % 6] = gate_type
        del (self._exits)

    def find_direction(self, neighbor_label):
        """Return the direction (0 to 5) from this hex to the adjacent hex
           with neighbor_label.
        """
        neighbor = self.board.hexes[neighbor_label]
        deltax = neighbor.x - self.x
        deltay = neighbor.y - self.y
        if deltax == 0:
            if deltay == -1:
                return 0
            elif deltay == 1:
                return 3
            raise Exception("non-adjacent hex")
        elif deltay == 0:
            if deltax == 1:
                if self.inverted:
                    return 2
                else:
                    return 1
            elif deltax == -1:
                if self.inverted:
                    return 4
                else:
                    return 5
        raise Exception("non-adjacent hex")

    def build_overlay_filename(self):
        if self.inverted:
            invert_indicator = 'i'
        else:
            invert_indicator = 'n'
        self.overlay_filename = "%s_%s.png" % (self.terrain, invert_indicator)

    def find_label_side(self):
        """Return the hexside number where the hex label should go.

           This is always a short hexside, either the one closest to
           the center of the board, or the one farthest away from it.
        """
        deltaX = self.x - self.board.midX
        deltaY = (1.0 * (self.y - self.board.midY) *
                  self.board.width / self.board.height)
        try:
            ratio = deltaX / deltaY
        except ZeroDivisionError:
            ratio = deltaX * BIGNUM

        if abs(ratio) < 0.6:
            # Vertically dominated
            if self.inverted:
                return 3
            else:
                return 0
        else:
            # Horizontally dominated
            if deltaX * deltaY >= 0:
                if self.inverted:
                    return 5
                else:
                    return 2
            else:
                if self.inverted:
                    return 1
                else:
                    return 4

    def is_tower(self):
        """Return True iff this hex is a tower."""
        return self.terrain == "Tower"
