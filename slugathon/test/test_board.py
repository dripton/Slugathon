from slugathon.game import MasterBoard
from slugathon.util import guiutils

__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


board = MasterBoard.MasterBoard()
hex1 = board.hexes[1]
hex2 = board.hexes[2]


def test_init_hex():
    assert hex1.terrain == "Plains"
    assert hex1.x == 7
    assert hex1.y == 5


def test_find_direction():
    """Returns a direction (0 to 5) to the hex with the given label."""
    assert hex1.find_direction(2) == 2
    assert hex1.find_direction(1000) == 0


def test_hex_inverted():
    assert hex1.inverted
    assert not board.hexes[2].inverted


def test_exits():
    assert hex1.exits[0] == "ARCH"
    assert hex1.exits[1] is None
    assert hex1.exits[2] == "ARROWS"
    assert hex1.exits[3] is None
    assert hex1.exits[4] is None
    assert hex1.exits[5] is None
    assert hex2.exits[0] is None
    assert hex2.exits[1] == "ARCH"
    assert hex2.exits[2] is None
    assert hex2.exits[3] == "ARROWS"
    assert hex2.exits[4] is None
    assert hex2.exits[5] is None
    assert hex1.entrances[0] == "BLOCK"
    assert hex1.entrances[1] is None
    assert hex1.entrances[2] is None
    assert hex1.entrances[3] is None
    assert hex1.entrances[4] == "ARROWS"
    assert hex1.entrances[5] is None
    assert hex2.entrances[0] is None
    assert hex2.entrances[1] == "ARCH"
    assert hex2.entrances[2] is None
    assert hex2.entrances[3] is None
    assert hex2.entrances[4] is None
    assert hex2.entrances[5] == "ARROWS"


def test_neighbors():
    assert hex1.neighbors[0] == board.hexes[1000]
    assert hex1.neighbors[1] is None
    assert hex1.neighbors[2] == board.hexes[2]
    assert hex1.neighbors[3] is None
    assert hex1.neighbors[4] == board.hexes[42]
    assert hex1.neighbors[5] is None


def test_flatten_point_list():
    vertexes = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]
    assert guiutils.flatten_point_list(vertexes) == (
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
    )


def test_rgb_to_gtk():
    assert guiutils.rgb_to_gtk((0, 0, 0)) == ((0, 0, 0))
    assert guiutils.rgb_to_gtk((255, 255, 255)) == ((65280, 65280, 65280))
    assert guiutils.rgb_to_gtk((189, 0, 24)) == ((48384, 0, 6144))


def test_build_overlay_filename():
    assert hex1.overlay_filename == "Plains_i.png"
    assert hex2.overlay_filename == "Woods_n.png"


def test_find_label_side():
    assert hex1.find_label_side() == 3
    assert hex2.find_label_side() == 0
    assert board.hexes[115].find_label_side() == 1
    assert board.hexes[300].find_label_side() == 4
    assert board.hexes[5000].find_label_side() == 2
    assert board.hexes[105].find_label_side() == 5


def test_get_semicircle_points():
    assert guiutils.get_semicircle_points(0, 0, 1, 1, 0) == []

    li = guiutils.get_semicircle_points(100, 100, 200, 100, 4)
    assert len(li) == 4
    assert li[0] == (100, 100)
    assert li[1][0] > 100
    assert li[1][1] < 100
    assert li[2][0] > li[1][0]
    assert li[2][1] == li[1][1]
    assert li[3] == (200, 100)

    li = guiutils.get_semicircle_points(100, 100, 100, 200, 4)
    assert len(li) == 4
    assert li[0] == (100, 100)
    assert li[1][0] > 100
    assert li[1][1] > 100
    assert li[2][0] > 100
    assert li[2][0] == li[1][0]
    assert li[2][1] > 100
    assert li[3] == (100, 200)

    li = guiutils.get_semicircle_points(200, 100, 100, 100, 4)
    assert len(li) == 4
    assert li[0] == (200, 100)
    assert li[1][0] > 100
    assert li[1][1] > 100
    assert li[2][0] > 100
    assert li[2][1] > 100
    assert li[3] == (100, 100)


def test_scale_polygon():
    vertexes = [(100, 0), (200, 100), (100, 200), (0, 100)]
    nv = guiutils.scale_polygon(vertexes, 0.5)
    assert int(round(nv[0][0])) == 100
    assert int(round(nv[0][1])) == 50
    assert int(round(nv[1][0])) == 150
    assert int(round(nv[1][1])) == 100
    assert int(round(nv[2][0])) == 100
    assert int(round(nv[2][1])) == 150
    assert int(round(nv[3][0])) == 50
    assert int(round(nv[3][1])) == 100


def test_towers():
    labels = board.get_tower_labels()
    labels.sort()
    assert labels == [100, 200, 300, 400, 500, 600]


def test_hex_width():
    assert board.hex_width == 15


def test_hex_height():
    assert board.hex_height == 8
