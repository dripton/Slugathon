from __future__ import annotations

from typing import Dict, Optional, Set

from slugathon.game import BattleMap

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


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

    def __init__(
        self,
        battlemap: BattleMap.BattleMap,
        label: str,
        x: int,
        y: float,
        terrain: str,
        elevation: int,
        borderdict: Dict[int, str],
    ):
        self.battlemap = battlemap
        self.label = label
        self.x = x
        self.y = y
        self.terrain = terrain
        self.elevation = elevation
        self.borders = []
        for ii in range(6):
            self.borders.append(borderdict.get(ii))
        self.down = self.x & 1 == 1
        self.label_side = 5
        self.terrain_side = 3
        self.entrance = self.label in ["ATTACKER", "DEFENDER"]
        self.neighbors = {}  # type: Dict[int, BattleHex]

    def __repr__(self) -> str:
        return f"BattleHex {self.label} ({self.x}, {self.y})"

    def init_neighbors(self) -> None:
        """Called from BattleMap after all hexes are initialized."""
        if self.entrance:
            # hexsides don't really matter for entrances
            hexside = 0
            for hex1 in self.battlemap.hexes.values():
                if abs(hex1.x - self.x) == 1:
                    self.neighbors[hexside] = hex1
                    hexside += 1
        else:
            for hex1 in self.battlemap.hexes.values():
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

    def hexsides_with_border(self, border: str) -> Set[int]:
        """Return the set of hexsides with this border."""
        result = set()
        for hexside, border2 in enumerate(self.borders):
            if border2 == border:
                result.add(hexside)
        return result

    def opposite_border(self, hexside: int) -> Optional[str]:
        """Return the border type of the adjacent hex in direction hexside.

        Raise if there's no hex there.
        """
        neighbor = self.neighbors[hexside]
        return neighbor.borders[(hexside + 3) % 6]

    @property
    def blocks_line_of_sight(self) -> bool:
        """Return True if this hex's terrain type blocks LOS."""
        return self.terrain == "Tree"

    def neighbor_to_hexside(self, neighbor: BattleHex) -> Optional[int]:
        """Return the hexside adjacent to neighbor, or None."""
        for hexside, neighbor2 in self.neighbors.items():
            if neighbor2 == neighbor:
                return hexside
        return None
