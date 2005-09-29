import BattleMap

map1 = BattleMap.BattleMap("Mountains")
hex1 = map1.hexes["A1"]
hex2 = map1.hexes["A3"]
hex3 = map1.hexes["D3"]

def test_all_labels():
    assert len(BattleMap.all_labels) == 27
    assert "A1" in BattleMap.all_labels
    assert "A4" not in BattleMap.all_labels

def test_default_hex_init():
    assert hex1.terrain == "Plains"
    assert hex1.elevation == 0
    for ii in xrange(6):
        assert hex1.borders[ii] == " "

def test_non_default_hex_init():
    assert hex2.terrain == "Plains"
    assert hex2.elevation == 1
    assert hex2.borders[0] == "s"
    assert hex2.borders[1] == " "
    assert hex2.borders[2] == " "
    assert hex2.borders[3] == " "
    assert hex2.borders[4] == " "
    assert hex2.borders[5] == " "

    assert hex3.terrain == "Volcano"
    assert hex3.elevation == 2
    assert hex3.borders[0] == "s"
    assert hex3.borders[1] == "s"
    assert hex3.borders[2] == "s"
    assert hex3.borders[3] == "s"
    assert hex3.borders[4] == "c"
    assert hex3.borders[5] == "s"

def test_label_to_coords():
    assert BattleMap.label_to_coords("A1") == (0,1)
    assert BattleMap.label_to_coords("B1") == (1,1)
    assert BattleMap.label_to_coords("C1") == (2,0)
    assert BattleMap.label_to_coords("D1") == (3,0)
    assert BattleMap.label_to_coords("E1") == (4,0)
    assert BattleMap.label_to_coords("F1") == (5,1)
    assert BattleMap.label_to_coords("A3") == (0,3)
    assert BattleMap.label_to_coords("D6") == (3,5)
    assert BattleMap.label_to_coords("E4") == (4,3)
    for label in ("", "A0", "A4", "A10", "G1"):
        try:
            BattleMap.label_to_coords(label)
        except KeyError:
            pass
        else:
            py.test.fail()

