from typing import Dict, List, Tuple, Union

from slugathon.data import boarddata
from slugathon.game import MasterHex


__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


class MasterBoard(object):
    """Model of the Titan MasterBoard.  No GUI logic allowed."""

    def __init__(self) -> None:
        self.compute_hexes_metadata()
        # str hexlabel to MasterHex
        self.hexes = {}  # type: Dict[int, MasterHex.MasterHex]
        for hexdata in boarddata.data:
            self.init_hex(hexdata)
        for hex1 in self.hexes.values():
            hex1.connect_to_neighbors()

    def compute_hexes_metadata(self) -> None:
        """Find the min, max, midpoint, width, and height of the hexes."""
        xs = [hexdata[1] for hexdata in boarddata.data]
        ys = [hexdata[2] for hexdata in boarddata.data]
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.max_x = max(xs)
        self.max_y = max(ys)
        self.mid_x = (self.min_x + self.max_x) / 2.0
        self.mid_y = (self.min_y + self.max_y) / 2.0
        self.width = self.max_x - self.min_x + 1
        self.height = self.max_y - self.min_y + 1

    def init_hex(
        self,
        hexdata: Union[
            Tuple[int, int, int, str, int, str],
            Tuple[int, int, int, str, int, str, int, str],
            Tuple[int, int, int, str, int, str, int, str, int, str],
        ],
    ) -> None:
        assert len(hexdata) in (6, 8, 10)
        (label, x, y, terrain) = hexdata[:4]
        exits = hexdata[4:]
        hex1 = MasterHex.MasterHex(self, label, x, y, terrain, exits)
        self.hexes[label] = hex1

    @property
    def hex_width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def hex_height(self) -> int:
        return self.max_y - self.min_y + 1

    def get_tower_labels(self) -> List[int]:
        """Return a list of int labels for this board's tower hexes."""
        return [hex1.label for hex1 in self.hexes.values() if hex1.tower]
