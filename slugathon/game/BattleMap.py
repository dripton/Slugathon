from __future__ import annotations

import logging
from sys import maxsize
from typing import Dict, Optional, Set, Tuple

from slugathon.data import battlemapdata
from slugathon.game import BattleHex, Game


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


all_labels = frozenset(
    [
        "A1",
        "A2",
        "A3",
        "B1",
        "B2",
        "B3",
        "B4",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "F1",
        "F2",
        "F3",
        "F4",
        "ATTACKER",
        "DEFENDER",
    ]
)


def label_to_coords(
    label: str, entry_side: int, down: bool = False
) -> Tuple[int, float]:
    """Convert a hex label to a tuple of X and Y coordinates, starting at the
    top left.

    We spin the map so that the attacker's entry side is always on the left.
    This works on the rotated map.

    If down is True, then increase the Y coordinate by 0.5 if the X coordinate
    is odd, reflecting the way hexes are shifted.

    0    *  *  *
    1 *  *  *  *  *  *
    2 *  *  *  *  *  *
    3 *  *  *  *  *  *
    4 *  *  *  *  *
    5       *
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

    entry_side 5:

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
    """
    if label not in all_labels:
        raise KeyError("bad battle hex label")
    l2c = {}
    l2c[1] = {
        "A1": (5, 1),
        "A2": (5, 2),
        "A3": (5, 3),
        "B1": (4, 1),
        "B2": (4, 2),
        "B3": (4, 3),
        "B4": (4, 4),
        "C1": (3, 0),
        "C2": (3, 1),
        "C3": (3, 2),
        "C4": (3, 3),
        "C5": (3, 4),
        "D1": (2, 0),
        "D2": (2, 1),
        "D3": (2, 2),
        "D4": (2, 3),
        "D5": (2, 4),
        "D6": (2, 5),
        "E1": (1, 0),
        "E2": (1, 1),
        "E3": (1, 2),
        "E4": (1, 3),
        "E5": (1, 4),
        "F1": (0, 1),
        "F2": (0, 2),
        "F3": (0, 3),
        "F4": (0, 4),
        "ATTACKER": (-1, 2),
        "DEFENDER": (6, 2),
    }
    l2c[3] = {
        "A1": (2, 5),
        "A2": (1, 4),
        "A3": (0, 4),
        "B1": (3, 4),
        "B2": (2, 4),
        "B3": (1, 3),
        "B4": (0, 3),
        "C1": (4, 4),
        "C2": (3, 3),
        "C3": (2, 3),
        "C4": (1, 2),
        "C5": (0, 2),
        "D1": (5, 3),
        "D2": (4, 3),
        "D3": (3, 2),
        "D4": (2, 2),
        "D5": (1, 1),
        "D6": (0, 1),
        "E1": (5, 2),
        "E2": (4, 2),
        "E3": (3, 1),
        "E4": (2, 1),
        "E5": (1, 0),
        "F1": (5, 1),
        "F2": (4, 1),
        "F3": (3, 0),
        "F4": (2, 0),
        "ATTACKER": (-1, 2),
        "DEFENDER": (6, 2),
    }
    l2c[5] = {
        "A1": (0, 1),
        "A2": (1, 0),
        "A3": (2, 0),
        "B1": (0, 2),
        "B2": (1, 1),
        "B3": (2, 1),
        "B4": (3, 0),
        "C1": (0, 3),
        "C2": (1, 2),
        "C3": (2, 2),
        "C4": (3, 1),
        "C5": (4, 1),
        "D1": (0, 4),
        "D2": (1, 3),
        "D3": (2, 3),
        "D4": (3, 2),
        "D5": (4, 2),
        "D6": (5, 1),
        "E1": (1, 4),
        "E2": (2, 4),
        "E3": (3, 3),
        "E4": (4, 3),
        "E5": (5, 2),
        "F1": (2, 5),
        "F2": (3, 4),
        "F3": (4, 4),
        "F4": (5, 3),
        "ATTACKER": (-1, 2),
        "DEFENDER": (6, 2),
    }
    x, y = l2c[entry_side][label]
    if down and x & 1:
        result = (x, y + 0.5)
    else:
        result = x, float(y)
    return result


EPSILON = 0.000001


def close(x: float, y: float) -> bool:
    """Return True iff x and y are within EPSILON."""
    return abs(x - y) <= EPSILON


def is_obstacle(border: str) -> bool:
    """Return True iff the border feature is an obstacle."""
    return bool(border)


class BattleMap(object):

    """A logical battle map.  No GUI code.

    See label_to_coords for hex labeling docs.
    """

    def __init__(self, mterrain: str, entry_side: int):
        logging.info(f"{mterrain=} {entry_side=}")
        self.hexes = {}
        self.entry_side = entry_side
        self.mterrain = mterrain
        mydata = battlemapdata.data[mterrain]
        for label in all_labels:
            x, y = label_to_coords(label, entry_side)
            if label in mydata:
                bterrain, elevation, hexside_dict = mydata[label]
                spun_hexside_dict = self.spin_border_dict(
                    hexside_dict, entry_side
                )
                self.hexes[label] = BattleHex.BattleHex(
                    self, label, x, y, bterrain, elevation, spun_hexside_dict
                )
            else:
                self.hexes[label] = BattleHex.BattleHex(
                    self, label, x, y, "Plain", 0, {}
                )
        for hex1 in self.hexes.values():
            hex1.init_neighbors()
        self.startlist = battlemapdata.startlist.get(mterrain)

    @property
    def hex_width(self) -> int:
        """Width of the map, in hexes, including entrances."""
        return 8

    @property
    def hex_height(self) -> int:
        """Height of the map, in hexes."""
        return 6

    def spin_border_dict(
        self, border_dict: Dict[int, str], entry_side: int
    ) -> Dict[int, str]:
        """Return a new dict with the keys (hexsides) rotated by the correct
        amount for entry_side"""
        spun = {}
        entry_side_to_delta = {1: 3, 3: 5, 5: 1}
        delta = entry_side_to_delta[entry_side]
        for key, val in border_dict.items():
            spun[(key + delta) % 6] = val
        return spun

    def range(
        self, hexlabel1: str, hexlabel2: str, allow_entrance: bool = False
    ) -> int:
        """Return the range from hexlabel1 to hexlabel2.

        Titan ranges are inclusive on both ends, so one more than
        you'd expect.

        If either hex is an entrance, return a huge number, unless
        allow_entrance is True, in which case return the normal range.
        """
        if hexlabel1 not in self.hexes or hexlabel2 not in self.hexes:
            logging.info(
                f"BattleMap.range invalid hexlabel {hexlabel1} {hexlabel2} "
                f"{allow_entrance}"
            )
            return maxsize
        if hexlabel1 == hexlabel2:
            return 1
        hex1 = self.hexes[hexlabel1]
        hex2 = self.hexes[hexlabel2]
        if hex1.entrance or hex2.entrance:
            if not allow_entrance or (hex1.entrance and hex2.entrance):
                return maxsize
            elif hex2.entrance:
                # We need to start from the entrance.
                hex1, hex2 = hex2, hex1
        result = 2
        prev = {hex1}
        ignore = set()  # type: Set[BattleHex.BattleHex]
        while True:
            neighbors = set()  # type: Set[BattleHex.BattleHex]
            for hex3 in prev:
                neighbors.update(iter(hex3.neighbors.values()))
            if hex2 in neighbors:
                return result
            neighbors -= ignore
            result += 1
            ignore = prev
            prev = neighbors

    def _to_left(self, delta_x: float, delta_y: float) -> bool:
        """Return True iff the path of displacement (delta_x, delta_y)
        passes to the left of the hexspine.

        delta_y must be nonzero.
        """
        ratio = delta_x / delta_y
        return (
            ratio >= 1.5
            or (ratio >= 0 and ratio <= 0.75)
            or (ratio >= -1.5 and ratio <= -0.75)
        )

    def _get_direction(
        self, hex1: BattleHex.BattleHex, hex2: BattleHex.BattleHex, left: bool
    ) -> int:
        """Return the hexside direction of the path from hex1 to hex2.

        Sometimes two directions are possible.  If the left parameter
        is set, the direction further left will be given.  Otherwise,
        the direction further right will be given.

        Return -1 on error.
        """
        assert hex1 != hex2
        # Offboard creatures are not allowed.
        assert not hex1.entrance
        assert not hex2.entrance
        x1 = hex1.x
        y1 = hex1.y
        x2 = hex2.x
        y2 = hex2.y
        # Hexes with odd X coordinates are pushed down half a hex.
        if (x1 & 1) == 1:
            y1 += 0.5
        if (x2 & 1) == 1:
            y2 += 0.5
        delta_x = x2 - x1
        delta_y = y2 - y1
        delta_x_times_one_point_five = 1.5 * delta_x
        if delta_x >= 0:
            if delta_y > delta_x_times_one_point_five:
                return 3
            elif close(delta_y, delta_x_times_one_point_five):
                if left:
                    return 2
                else:
                    return 3
            elif delta_y < -delta_x_times_one_point_five:
                return 0
            elif close(delta_y, -delta_x_times_one_point_five):
                if left:
                    return 0
                else:
                    return 1
            elif delta_y > 0:
                return 2
            elif delta_y < 0:
                return 1
            else:
                if left:
                    return 1
                else:
                    return 2
        else:
            if delta_y < delta_x_times_one_point_five:
                return 0
            elif close(delta_y, delta_x_times_one_point_five):
                if left:
                    return 5
                else:
                    return 0
            elif delta_y > -delta_x_times_one_point_five:
                return 3
            elif close(delta_y, -delta_x_times_one_point_five):
                if left:
                    return 3
                else:
                    return 4
            elif delta_y > 0:
                return 4
            elif delta_y < 0:
                return 5
            else:
                if left:
                    return 4
                else:
                    return 5

    def _is_los_blocked_dir(
        self,
        initial_hex: BattleHex.BattleHex,
        current_hex: BattleHex.BattleHex,
        final_hex: BattleHex.BattleHex,
        left: bool,
        strike_elevation: int,
        striker_atop: bool = False,
        striker_atop_cliff: bool = False,
        striker_atop_wall: bool = False,
        mid_obstacle: bool = False,
        mid_cliff: bool = False,
        mid_chit: bool = False,
        total_obstacles: int = 0,
        total_walls: int = 0,
        game: Optional[Game.Game] = None,
    ) -> bool:
        """Return True iff the line of sight from hexlabel1 to
        hexlabel2 is blocked by terrain or creatures, going to the left of
        hexspines if left is True.
        """
        target_atop = False
        target_atop_cliff = False
        target_atop_wall = False
        if current_hex == final_hex:
            return False
        # Offboard hexes are not allowed.
        assert not current_hex.entrance
        assert not final_hex.entrance
        direction = self._get_direction(current_hex, final_hex, left)
        next_hex = current_hex.neighbors.get(direction)
        assert next_hex is not None
        border = current_hex.borders[direction]
        border2 = current_hex.opposite_border(direction)
        if current_hex == initial_hex:
            if border is not None and is_obstacle(border):
                striker_atop = True
                total_obstacles += 1
                if border == "Cliff":
                    striker_atop_cliff = True
                    if next_hex == final_hex:
                        return True
                elif border == "Wall":
                    striker_atop_wall = True
                    total_walls += 1
            if border2 is not None and is_obstacle(border2):
                mid_obstacle = True
                total_obstacles += 1
                if border2 == "Cliff" or border2 == "Dune":
                    mid_cliff = True
                    if next_hex == final_hex:
                        return True
                elif border2 == "Wall":
                    return True
        elif next_hex == final_hex:
            if border is not None and is_obstacle(border):
                mid_obstacle = True
                total_obstacles += 1
                if border == "Cliff" or border == "Dune":
                    mid_cliff = True
                elif border == "Wall":
                    return True
            if border2 is not None and is_obstacle(border2):
                target_atop = True
                total_obstacles += 1
                if border2 == "Cliff":
                    target_atop_cliff = True
                elif border2 == "Wall":
                    total_walls += 1
                    target_atop_wall = True
            if mid_chit and not target_atop_cliff:
                return True
            if mid_cliff and (not striker_atop_cliff or not target_atop_cliff):
                return True
            if mid_obstacle and not striker_atop and not target_atop:
                return True
            if (
                total_obstacles >= 3
                and (not striker_atop or not target_atop)
                and (not striker_atop_cliff and not target_atop_cliff)
            ):
                return True
            if total_walls >= 2:
                if not (striker_atop_wall or target_atop_wall):
                    return True
            elif total_walls == 1 and not (
                striker_atop_wall or target_atop_wall
            ):
                return True
            return False
        else:
            if mid_chit:
                # We're not in the initial or final hex, and we have already
                # marked a mid chit, so it's not adjacent to the base of a
                # cliff that the target is atop.
                return True
            if (
                border is not None
                and is_obstacle(border)
                or border2 is not None
                and is_obstacle(border2)
            ):
                mid_obstacle = True
                total_obstacles += 1
                if (
                    border == "Cliff"
                    or border2 == "Cliff"
                    or border == "Dune"
                    or border2 == "Dune"
                ):
                    mid_cliff = True
        if next_hex.blocks_line_of_sight:
            return True
        # Creatures block LOS, unless both striker and target are at higher
        # elevation than the creature, or unless the creature is at
        # the base of a cliff and the striker or target is atop it.
        if (
            game is not None
            and game.is_battle_hex_occupied(next_hex.label)
            and next_hex.elevation >= strike_elevation
            and (not striker_atop_cliff or current_hex != initial_hex)
        ):
            mid_chit = True
        return self._is_los_blocked_dir(
            initial_hex=initial_hex,
            current_hex=next_hex,
            final_hex=final_hex,
            left=left,
            strike_elevation=strike_elevation,
            striker_atop=striker_atop,
            striker_atop_cliff=striker_atop_cliff,
            striker_atop_wall=striker_atop_wall,
            mid_obstacle=mid_obstacle,
            mid_cliff=mid_cliff,
            mid_chit=mid_chit,
            total_obstacles=total_obstacles,
            total_walls=total_walls,
            game=game,
        )

    def is_los_blocked(
        self, hexlabel1: str, hexlabel2: str, game: Optional[Game.Game]
    ) -> bool:
        """Return True iff the line of sight from hexlabel1 to
        hexlabel2 is blocked by terrain or creatures.

        game is optional, but needed to check creatures.
        """
        assert hexlabel1 in self.hexes and hexlabel2 in self.hexes
        if hexlabel1 == hexlabel2:
            return False
        x1, y1 = label_to_coords(hexlabel1, self.entry_side, True)
        x2, y2 = label_to_coords(hexlabel2, self.entry_side, True)
        delta_x = x2 - x1
        delta_y = y2 - y1
        hex1 = self.hexes[hexlabel1]
        hex2 = self.hexes[hexlabel2]
        strike_elevation = min(hex1.elevation, hex2.elevation)
        if close(delta_y, 0) or close(abs(delta_y), 1.5 * abs(delta_x)):
            return self._is_los_blocked_dir(
                initial_hex=hex1,
                current_hex=hex1,
                final_hex=hex2,
                left=True,
                strike_elevation=strike_elevation,
                game=game,
            ) and self._is_los_blocked_dir(
                initial_hex=hex1,
                current_hex=hex1,
                final_hex=hex2,
                left=False,
                strike_elevation=strike_elevation,
                game=game,
            )
        else:
            return self._is_los_blocked_dir(
                initial_hex=hex1,
                current_hex=hex1,
                final_hex=hex2,
                left=self._to_left(delta_x, delta_y),
                strike_elevation=strike_elevation,
                game=game,
            )

    def _count_bramble_hexes_dir(
        self,
        hex1: BattleHex.BattleHex,
        hex2: BattleHex.BattleHex,
        left: bool,
        count: int,
    ) -> int:
        """Return the number of intervening bramble hexes.

        If LOS is along a hexspine, go left if argument left is True, right
        otherwise.   If LOS is blocked, return a large number.
        """
        assert not hex1.entrance
        assert not hex2.entrance
        direction = self._get_direction(hex1, hex2, left)
        next_hex = hex1.neighbors.get(direction)
        assert next_hex is not None
        if next_hex == hex2:
            return count
        if next_hex.terrain == "Bramble":
            count += 1
        return self._count_bramble_hexes_dir(next_hex, hex2, left, count)

    def count_bramble_hexes(
        self, hexlabel1: str, hexlabel2: str, game: Optional[Game.Game]
    ) -> int:
        """Return the minimum number of intervening bramble hexes along a valid
        line of sight between hexlabel1 and hexlabel2.

        game is optional, but needed to check creatures.
        """
        if hexlabel1 == hexlabel2:
            logging.info(
                f"count_bramble_hexes hexlabel1 == hexlabel2 == {hexlabel1}"
            )
            return 0
        if self.is_los_blocked(hexlabel1, hexlabel2, game):
            logging.info(
                f"count_bramble_hexes {hexlabel1} {hexlabel2} los blocked"
            )
            return 0
        hex1 = self.hexes[hexlabel1]
        hex2 = self.hexes[hexlabel2]
        if hex1.entrance or hex2.entrance:
            logging.info("count_bramble_hexes entrance hex")
            return 0
        x1, y1 = label_to_coords(hexlabel1, self.entry_side, True)
        x2, y2 = label_to_coords(hexlabel2, self.entry_side, True)
        delta_x = x2 - x1
        delta_y = y2 - y1

        if close(delta_y, 0) or close(delta_y, 1.5 * abs(delta_x)):
            strike_elevation = min(hex1.elevation, hex2.elevation)
            # Hexspine try unblocked side(s).
            if self._is_los_blocked_dir(
                initial_hex=hex1,
                current_hex=hex1,
                final_hex=hex2,
                left=True,
                strike_elevation=strike_elevation,
                striker_atop=False,
                striker_atop_cliff=False,
                striker_atop_wall=False,
                mid_obstacle=False,
                mid_cliff=False,
                mid_chit=False,
                total_obstacles=0,
                total_walls=0,
                game=game,
            ):
                return self._count_bramble_hexes_dir(hex1, hex2, False, 0)
            elif self._is_los_blocked_dir(
                initial_hex=hex1,
                current_hex=hex1,
                final_hex=hex2,
                left=False,
                strike_elevation=strike_elevation,
                striker_atop=False,
                striker_atop_cliff=False,
                striker_atop_wall=False,
                mid_obstacle=False,
                mid_cliff=False,
                mid_chit=False,
                total_obstacles=0,
                total_walls=0,
                game=game,
            ):
                return self._count_bramble_hexes_dir(hex1, hex2, True, 0)
            else:
                return min(
                    self._count_bramble_hexes_dir(hex1, hex2, True, 0),
                    self._count_bramble_hexes_dir(hex1, hex2, False, 0),
                )
        else:
            return self._count_bramble_hexes_dir(
                hex1, hex2, self._to_left(delta_x, delta_y), 0
            )

    # XXX Hardcoded to default Tower map
    def count_walls(
        self, hexlabel1: str, hexlabel2: str, game: Optional[Game.Game]
    ) -> int:
        """Return the number of uphill wall hazards between hexlabel1 and
        hexlabel2.

        game is optional, but needed to check creatures.
        """
        if self.mterrain != "Tower":
            return 0
        hex1 = self.hexes[hexlabel1]
        hex2 = self.hexes[hexlabel2]
        return max(hex2.elevation - hex1.elevation, 0)
