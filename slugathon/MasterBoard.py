import boarddata
import MasterHex
from twisted.spread import pb


class MasterBoard(pb.Copyable, pb.RemoteCopy):
    """Model of the Titan MasterBoard.  No GUI logic allowed."""
    def __init__(self):
        self.compute_hexes_metadata()
        self.hexes = {}
        for hexdata in boarddata.data:
            self.init_hex(hexdata)
        for hex in self.hexes.values():
            hex.connect_to_neighbors()

    def compute_hexes_metadata(self):
        """Find the min, max, midpoint, width, and height of the hexes."""
        xs = [hexdata[1] for hexdata in boarddata.data]
        ys = [hexdata[2] for hexdata in boarddata.data]
        self.minX = min(xs)
        self.minY = min(ys)
        self.maxX = max(xs)
        self.maxY = max(ys)
        self.midX = (self.minX + self.maxX) / 2.
        self.midY = (self.minY + self.maxY) / 2.
        self.width = self.maxX - self.minX + 1
        self.height = self.maxY - self.minY + 1

    def init_hex(self, hexdata):
        assert len(hexdata) in (6, 8, 10)
        (label, x, y, terrain) = hexdata[:4]
        exits = hexdata[4:]
        hex = MasterHex.MasterHex(self, label, x, y, terrain, exits)
        self.hexes[label] = hex

    def hex_width(self):
        return self.maxX - self.minX + 1

    def hex_height(self):
        return self.maxY - self.minY + 1

    def get_tower_labels(self):
        """Return a list of int labels for this board's tower hexes."""
        return [hex.label for hex in self.hexes.values()
                if hex.is_tower()]

pb.setUnjellyableForClass(MasterBoard, MasterBoard)
