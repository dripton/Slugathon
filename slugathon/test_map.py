import py

import BattleMap
import guiutils

map1 = BattleMap.BattleMap("Mountains", 1)
hex1 = map1.hexes["A2"]
hex2 = map1.hexes["A1"]
hex3 = map1.hexes["D4"]

def test_all_labels():
    assert len(BattleMap.all_labels) == 29
    assert "A1" in BattleMap.all_labels
    assert "A4" not in BattleMap.all_labels
    assert "ATTACKER" in BattleMap.all_labels
    assert "DEFENDER" in BattleMap.all_labels

def test_default_hex_init():
    assert hex1.terrain == "Plains"
    assert hex1.elevation == 0
    for ii in xrange(6):
        assert hex1.borders[ii] is None

def test_non_default_hex_init():
    assert hex2.terrain == "Plains"
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

def test_label_to_coords():
    assert BattleMap.label_to_coords("A1", 1) == (5, 1)
    for label in ("", "A0", "A4", "A10", "G1"):
        try:
            BattleMap.label_to_coords(label, 1)
        except KeyError:
            pass
        else:
            py.test.fail()

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
