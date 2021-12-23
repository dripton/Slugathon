from __future__ import annotations

from typing import List, Optional, Tuple, Union

from slugathon.game import MasterBoard


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


BIGNUM = 99999999


class MasterHex(object):
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

    def __init__(
        self,
        board: "MasterBoard.MasterBoard",
        label: int,
        x: int,
        y: int,
        terrain: str,
        exits: Union[
            Tuple[int, str],
            Tuple[int, str, int, str],
            Tuple[int, str, int, str, int, str],
        ],
    ):
        self.board = board
        self.label = label
        self.x = x
        self.y = y
        self.inverted = (self.x + self.y) & 1 == 0
        self.terrain = terrain
        self._exits = exits
        self.exits = []  # type: List[Optional[str]]
        self.entrances = []  # type: List[Optional[str]]
        self.neighbors = []  # type: List[Optional[MasterHex]]
        for unused in range(6):
            self.exits.append(None)
            self.entrances.append(None)
            self.neighbors.append(None)
        self.build_overlay_filename()
        self.label_side = self.find_label_side()

    def __repr__(self) -> str:
        return f"{self.terrain} hex {self.label} at ({self.x},{self.y})"

    def connect_to_neighbors(self) -> None:
        it = iter(self._exits)
        for (neighbor_label, gate_type) in zip(it, it):
            assert isinstance(neighbor_label, int)
            assert isinstance(gate_type, str)
            direction = self.find_direction(neighbor_label)
            self.exits[direction] = gate_type
            neighbor = self.board.hexes[neighbor_label]
            self.neighbors[direction] = neighbor
            neighbor.neighbors[(direction + 3) % 6] = self
            neighbor.entrances[(direction + 3) % 6] = gate_type
        del self._exits

    def find_direction(self, neighbor_label: int) -> int:
        """Return the direction (0 to 5) from this hex to the adjacent hex
        with neighbor_label.
        """
        neighbor = self.board.hexes[neighbor_label]
        delta_x = neighbor.x - self.x
        delta_y = neighbor.y - self.y
        if delta_x == 0:
            if delta_y == -1:
                return 0
            elif delta_y == 1:
                return 3
            raise Exception("non-adjacent hex")
        elif delta_y == 0:
            if delta_x == 1:
                if self.inverted:
                    return 2
                else:
                    return 1
            elif delta_x == -1:
                if self.inverted:
                    return 4
                else:
                    return 5
        raise Exception("non-adjacent hex")

    def build_overlay_filename(self) -> None:
        if self.inverted:
            invert_indicator = "i"
        else:
            invert_indicator = "n"
        self.overlay_filename = f"{self.terrain}_{invert_indicator}.png"

    def find_label_side(self) -> int:
        """Return the hexside number where the hex label should go.

        This is always a short hexside, either the one closest to
        the center of the board, or the one farthest away from it.
        """
        delta_x = self.x - self.board.mid_x
        delta_y = (
            1.0
            * (self.y - self.board.mid_y)
            * self.board.width
            / self.board.height
        )
        try:
            ratio = delta_x / delta_y
        except ZeroDivisionError:
            ratio = delta_x * BIGNUM

        if abs(ratio) < 0.6:
            # Vertically dominated
            if self.inverted:
                return 3
            else:
                return 0
        else:
            # Horizontally dominated
            if delta_x * delta_y >= 0:
                if self.inverted:
                    return 5
                else:
                    return 2
            else:
                if self.inverted:
                    return 1
                else:
                    return 4

    @property
    def tower(self) -> bool:
        """Return True iff this hex is a tower."""
        return self.terrain == "Tower"

    def find_entry_side(self, came_from: int) -> int:
        """Find the entry side, relative to the hex label."""
        if self.tower:
            return 5
        else:
            return (6 + came_from - self.find_label_side()) % 6

    def find_block(self) -> Optional[int]:
        """Return the direction of a forced starting move from this hex,
        or None if there is not one."""
        for direction, gate in enumerate(self.exits):
            if gate == "BLOCK":
                return direction
        return None

    def get_neighbor(self, side: int) -> "MasterHex":
        """Return the neighbor at side, which must exist.

        This is used to guarantee that the neighbor will not be None.
        """
        neighbor = self.neighbors[side]
        assert neighbor is not None
        return neighbor
