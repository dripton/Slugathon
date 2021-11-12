__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"

from sys import maxsize

from slugathon.game import BattleMap
from slugathon.util import guiutils


map1 = BattleMap.BattleMap("Mountains", 1)
hex1 = map1.hexes["A2"]
hex2 = map1.hexes["A1"]
hex3 = map1.hexes["D4"]
hex4 = map1.hexes["E1"]
hex5 = map1.hexes["F1"]

map2 = BattleMap.BattleMap("Tower", 5)
hex6 = map2.hexes["B2"]
hex7 = map2.hexes["C3"]

map3 = BattleMap.BattleMap("Brush", 1)
map4 = BattleMap.BattleMap("Desert", 5)
map5 = BattleMap.BattleMap("Jungle", 5)


def test_all_labels():
    assert len(BattleMap.all_labels) == 29
    assert "A1" in BattleMap.all_labels
    assert "A4" not in BattleMap.all_labels
    assert "ATTACKER" in BattleMap.all_labels
    assert "DEFENDER" in BattleMap.all_labels


def test_default_hex_init():
    assert hex1.terrain == "Plain"
    assert hex1.elevation == 0
    for ii in range(6):
        assert hex1.borders[ii] is None
        assert hex6.borders[ii] is None


def test_non_default_hex_init():
    assert hex2.terrain == "Plain"
    assert hex2.elevation == 1
    assert hex2.borders[0] is None
    assert hex2.borders[1] is None
    assert hex2.borders[2] is None
    assert hex2.borders[3] == "Slope"
    assert hex2.borders[4] is None
    assert hex2.borders[5] is None

    assert hex3.terrain == "Volcano"
    assert hex3.elevation == 2
    assert hex3.borders[0] == "Slope"
    assert hex3.borders[1] == "Cliff"
    assert hex3.borders[2] == "Slope"
    assert hex3.borders[3] == "Slope"
    assert hex3.borders[4] == "Slope"
    assert hex3.borders[5] == "Slope"

    assert hex7.terrain == "Tower"
    assert hex7.elevation == 1
    assert hex7.borders[0] == "Wall"
    assert hex7.borders[1] is None
    assert hex7.borders[2] is None
    assert hex7.borders[3] is None
    assert hex7.borders[4] == "Wall"
    assert hex7.borders[5] == "Wall"


def test_label_to_coords():
    assert BattleMap.label_to_coords("A1", 1) == (5, 1)
    assert BattleMap.label_to_coords("A1", 1, True) == (5, 1.5)
    assert BattleMap.label_to_coords("B2", 1) == (4, 2)
    assert BattleMap.label_to_coords("B2", 1, True) == (4, 2)
    for label in ("", "A0", "A4", "A10", "G1"):
        try:
            BattleMap.label_to_coords(label, 1)
        except KeyError:
            pass
        else:
            assert False


def test_midpoint():
    assert guiutils.midpoint((1, 0), (6, 3)) == (3.5, 1.5)


def test_roundpoint():
    assert guiutils.roundpoint((1, 2)) == (1, 2)
    assert guiutils.roundpoint((1., 2.)) == (1, 2)
    assert guiutils.roundpoint((1.5, 2.4999)) == (2, 2)
    assert guiutils.roundpoint((-0.3, 9.5)) == (0, 10)


def test_hexsides_with_border():
    assert hex1.hexsides_with_border("Slope") == set()
    assert hex1.hexsides_with_border("Cliff") == set()
    assert hex1.hexsides_with_border("Wall") == set()
    assert hex2.hexsides_with_border("Slope") == set([3])
    assert hex3.hexsides_with_border("Slope") == set([0, 2, 3, 4, 5])
    assert hex3.hexsides_with_border("Cliff") == set([1])


def test_spin_border_dict():
    assert map1.spin_border_dict({}, 1) == {}
    assert map1.spin_border_dict({}, 3) == {}
    assert map1.spin_border_dict({}, 5) == {}
    assert map1.spin_border_dict({0: "Slope"}, 1) == {3: "Slope"}
    assert map1.spin_border_dict({0: "Slope"}, 3) == {5: "Slope"}
    assert map1.spin_border_dict({0: "Slope"}, 5) == {1: "Slope"}


def test_startlist():
    assert map1.startlist is None
    map2 = BattleMap.BattleMap("Tower", 1)
    assert map2.startlist == ["C3", "C4", "D3", "D4", "D5", "E3", "E4"]


def test_neighbors():
    assert len(hex1.neighbors) == 4
    assert hex1.neighbors[0].label == "A1"
    assert hex1.neighbors[3].label == "A3"
    assert hex1.neighbors[4].label == "B3"
    assert hex1.neighbors[5].label == "B2"

    assert len(hex2.neighbors) == 3
    assert hex2.neighbors[3].label == "A2"
    assert hex2.neighbors[4].label == "B2"
    assert hex2.neighbors[5].label == "B1"

    assert len(hex3.neighbors) == 6
    assert hex3.neighbors[0].label == "D3"
    assert hex3.neighbors[1].label == "C3"
    assert hex3.neighbors[2].label == "C4"
    assert hex3.neighbors[3].label == "D5"
    assert hex3.neighbors[4].label == "E4"
    assert hex3.neighbors[5].label == "E3"

    assert len(hex4.neighbors) == 4
    assert hex4.neighbors[1].label == "D1"
    assert hex4.neighbors[2].label == "D2"
    assert hex4.neighbors[3].label == "E2"
    assert hex4.neighbors[4].label == "F1"

    assert len(hex5.neighbors) == 3
    assert hex5.neighbors[1].label == "E1"
    assert hex5.neighbors[2].label == "E2"
    assert hex5.neighbors[3].label == "F2"


def test_range():
    assert map1.range("A1", "A1") == 1
    assert map1.range("A1", "A2") == 2
    assert map1.range("A2", "A1") == 2
    assert map1.range("A1", "B1") == 2
    assert map1.range("A1", "B2") == 2
    assert map1.range("ATTACKER", "A1") == maxsize
    assert map1.range("A1", "ATTACKER") == maxsize
    assert map1.range("A1", "A3") == 3
    assert map1.range("A1", "B3") == 3
    assert map1.range("A1", "C1") == 3
    assert map1.range("A1", "C2") == 3
    assert map1.range("A1", "C3") == 3
    assert map1.range("A1", "D1") == 4
    assert map1.range("A1", "D2") == 4
    assert map1.range("A1", "D3") == 4
    assert map1.range("A1", "D4") == 4
    assert map1.range("A1", "C4") == 4
    assert map1.range("A1", "B4") == 4
    assert map1.range("A1", "E1") == 5
    assert map1.range("A1", "E2") == 5
    assert map1.range("A1", "E3") == 5
    assert map1.range("A1", "E4") == 5
    assert map1.range("A1", "E4") == 5
    assert map1.range("A1", "D5") == 5
    assert map1.range("A1", "C5") == 5
    assert map1.range("A1", "F1") == 6
    assert map1.range("A1", "F2") == 6
    assert map1.range("A1", "F3") == 6
    assert map1.range("A1", "F4") == 6
    assert map1.range("A1", "E5") == 6
    assert map1.range("A1", "D6") == 6
    assert map1.range("A1", "DEFENDER") == maxsize
    assert map1.range("DEFENDER", "A1") == maxsize
    assert map1.range("ATTACKER", "A1", True) == 7
    assert map1.range("A1", "ATTACKER", True) == 7
    assert map1.range("A1", "DEFENDER", True) == 2
    assert map1.range("DEFENDER", "A1", True) == 2


def test_opposite_border():
    hex1 = map1.hexes["D3"]
    assert hex1.opposite_border(0) is None
    assert hex1.opposite_border(1) is None
    assert hex1.opposite_border(2) is None
    assert hex1.opposite_border(3) == "Slope"
    assert hex1.opposite_border(4) is None
    assert hex1.opposite_border(5) is None
    hex1 = map1.hexes["C2"]
    assert hex1.opposite_border(0) == "Slope"
    assert hex1.opposite_border(1) == "Cliff"
    assert hex1.opposite_border(2) == "Slope"
    assert hex1.opposite_border(3) is None
    assert hex1.opposite_border(4) == "Slope"
    assert hex1.opposite_border(5) is None


def test_is_los_blocked():
    # Mountains
    assert map1.is_los_blocked("D5", "D3", None)
    assert not map1.is_los_blocked("D5", "E3", None)
    assert not map1.is_los_blocked("D5", "E4", None)
    assert not map1.is_los_blocked("D5", "E5", None)
    assert not map1.is_los_blocked("D5", "D6", None)
    assert not map1.is_los_blocked("D5", "C5", None)
    assert not map1.is_los_blocked("D5", "C4", None)
    assert not map1.is_los_blocked("D5", "B4", None)
    assert map1.is_los_blocked("D5", "B3", None)
    assert map1.is_los_blocked("D5", "A2", None)
    assert not map1.is_los_blocked("D5", "F2", None)
    assert map1.is_los_blocked("D5", "E2", None)
    assert map1.is_los_blocked("D5", "F1", None)
    assert map1.is_los_blocked("F3", "E2", None)
    assert not map1.is_los_blocked("B2", "D4", None)

    # Brush
    assert not map3.is_los_blocked("C4", "D6", None)

    # Desert
    assert map4.is_los_blocked("D4", "D3", None)
    assert map4.is_los_blocked("D3", "D4", None)
    assert not map4.is_los_blocked("D4", "C4", None)

    # Tower
    assert map2.is_los_blocked("D4", "B4", None)
    assert map2.is_los_blocked("B4", "D4", None)
    assert map2.is_los_blocked("D4", "B3", None)
    assert map2.is_los_blocked("B3", "D4", None)
    assert map2.is_los_blocked("D4", "B2", None)
    assert map2.is_los_blocked("B2", "D4", None)
    assert map2.is_los_blocked("D4", "C2", None)
    assert map2.is_los_blocked("C2", "D4", None)
    assert map2.is_los_blocked("C2", "E5", None)
    assert map2.is_los_blocked("D3", "D5", None)
    assert not map2.is_los_blocked("D4", "E1", None)
    assert not map2.is_los_blocked("E1", "D4", None)
    assert not map2.is_los_blocked("D4", "A1", None)
    assert not map2.is_los_blocked("A1", "D4", None)
    assert not map2.is_los_blocked("A1", "A1", None)

    # Jungle
    assert map5.is_los_blocked("C2", "E3", None)
    assert map5.is_los_blocked("E3", "C2", None)
    assert map5.is_los_blocked("B2", "E3", None)
    assert not map5.is_los_blocked("B3", "E3", None)
    assert not map5.is_los_blocked("C2", "E2", None)
    assert not map5.is_los_blocked("E2", "C2", None)
    assert not map5.is_los_blocked("C2", "D4", None)
    assert not map5.is_los_blocked("D4", "C2", None)
    assert not map5.is_los_blocked("C3", "D2", None)
    assert not map5.is_los_blocked("D2", "C3", None)
    assert not map5.is_los_blocked("D4", "E2", None)
    assert not map5.is_los_blocked("E2", "D4", None)
    assert not map5.is_los_blocked("E2", "E2", None)


def test_battlehex_repr():
    assert repr(hex1) == "BattleHex A2 (5, 2)"


def test_neighbor_to_hexside():
    assert hex1.neighbor_to_hexside(hex2) == 0
    assert hex2.neighbor_to_hexside(hex1) == 3
    assert hex1.neighbor_to_hexside(hex3) is None


def test_width_and_height():
    assert map1.hex_width == 8
    assert map1.hex_height == 6
