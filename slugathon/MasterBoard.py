#!/usr/bin/env python2

import boarddata
import MasterHex

BIGNUM = 999999

class MasterBoard:
    """Model of the Titan MasterBoard.  No GUI logic allowed."""
    def __init__(self):
        self.compute_hexes_metadata()
        self.hexes = {}
        for hexdata in boarddata.data:
            self.init_hex(hexdata)
        for hex in self.hexes.values():
            hex.connect_to_neighbors()
        self.minX = min([hex.x for hex in self.hexes.values()])
        self.maxX = max([hex.x for hex in self.hexes.values()])
        self.minY = min([hex.y for hex in self.hexes.values()])
        self.maxY = max([hex.y for hex in self.hexes.values()])
        self.midX = (self.minX + self.maxX) / 2.0
        self.midY = (self.minY + self.maxY) / 2.0
        self.width = (self.maxX - self.minX) + 1
        self.height = (self.maxY - self.minY) + 1

    def compute_hexes_metadata(self):
        """Find the min, max, midpoint, width, and height of the hexes."""
        self.minX = BIGNUM
        self.maxX = -BIGNUM
        self.minY = BIGNUM
        self.maxY = -BIGNUM
        for hexdata in boarddata.data:
            x = hexdata[1]
            y = hexdata[2]
            self.minX = min(self.minX, x)
            self.minY = min(self.minY, y)
            self.maxX = max(self.maxX, x)
            self.maxY = max(self.maxY, y)
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
