#!/usr/bin/env python

import unittest
import math
import guiutils
import MasterBoard
import GUIMasterBoard


EPSILON = 0.00001

def assertClose(a, b, epsilon=EPSILON):
    assert (abs(a - b) <= epsilon)


class MasterBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.board = MasterBoard.MasterBoard()
        self.hex = self.board.hexes[1]
        self.hex2 = self.board.hexes[2]

    def test_init_hex(self):
        assert self.hex.terrain == "Plains" 
        assert self.hex.x == 7
        assert self.hex.y == 5

    def test_find_direction(self):
        """Returns a direction (0 to 5) to the hex with the given label."""
        assert self.hex.find_direction(2) == 2
        assert self.hex.find_direction(1000) == 0

    def test_hex_inverted(self):
        assert self.hex.inverted
        assert not self.board.hexes[2].inverted

    def test_exits(self):
        assert self.hex.exits[0] == "ARCH"
        assert self.hex.exits[1] == None
        assert self.hex.exits[2] == "ARROWS"
        assert self.hex.exits[3] == None
        assert self.hex.exits[4] == None
        assert self.hex.exits[5] == None
        assert self.hex2.exits[0] == None
        assert self.hex2.exits[1] == "ARCH"
        assert self.hex2.exits[2] == None
        assert self.hex2.exits[3] == "ARROWS"
        assert self.hex2.exits[4] == None
        assert self.hex2.exits[5] == None
        assert self.hex.entrances[0] == "BLOCK"
        assert self.hex.entrances[1] == None
        assert self.hex.entrances[2] == None
        assert self.hex.entrances[3] == None
        assert self.hex.entrances[4] == "ARROWS"
        assert self.hex.entrances[5] == None
        assert self.hex2.entrances[0] == None
        assert self.hex2.entrances[1] == "ARCH"
        assert self.hex2.entrances[2] == None
        assert self.hex2.entrances[3] == None
        assert self.hex2.entrances[4] == None
        assert self.hex2.entrances[5] == "ARROWS"


    def test_neighbors(self):
        assert self.hex.neighbors[0] == self.board.hexes[1000]
        assert self.hex.neighbors[1] == None
        assert self.hex.neighbors[2] == self.board.hexes[2]
        assert self.hex.neighbors[3] == None
        assert self.hex.neighbors[4] == self.board.hexes[42]
        assert self.hex.neighbors[5] == None

    def test_flatten_point_list(self):
        vertexes = [(0,1), (2,3), (4,5), (6,7), (8,9), (10,11)]
        assert (guiutils.flatten_point_list(vertexes) ==
                (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    def test_rgb_to_gtk(self):
        assert guiutils.rgb_to_gtk((0, 0, 0)) == ((0, 0, 0))
        assert guiutils.rgb_to_gtk((255, 255, 255)) == ((65280, 65280, 65280))
        assert guiutils.rgb_to_gtk((189, 0, 24)) == ((48384, 0, 6144))

    def test_build_overlay_filename(self):
        assert self.hex.overlay_filename == "Plains_i.png"
        assert self.hex2.overlay_filename == "Woods_n.png"

    def test_find_label_side(self):
        assert self.hex.find_label_side() == 3
        assert self.hex2.find_label_side() == 0
        assert self.board.hexes[115].find_label_side() == 1
        assert self.board.hexes[300].find_label_side() == 4
        assert self.board.hexes[5000].find_label_side() == 2
        assert self.board.hexes[105].find_label_side() == 5

    def test_get_semicircle_points(self):
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

    def test_scale_polygon(self):
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

    def test_point_in_polygon(self):
        points = [
            (450, 441.67295593006367),
            (480, 441.67295593006367),
            (485.0, 450.33320996790803),
            (494.9230748895809, 450.37762270111597),
            (490.0, 458.99346400575246),
            (500.0, 476.31397208144119),
            (495.0769251104191, 484.92981338607768),
            (505.0, 484.97422611928562),
            (510, 493.63448015712999),
            (495, 519.6152422706632),
            (485.0, 519.6152422706632),
            (485.0, 528.18667084209176),
            (475.0, 528.18667084209176),
            (475.0, 519.6152422706632),
            (455.0, 519.6152422706632),
            (455.0, 515.32952798494887),
            (455, 515),
            (455, 514),
            (454, 512),
            (453, 511),
            (451, 510),
            (449, 510),
            (448, 511),
            (446, 512),
            (445, 514),
            (445, 515),
            (445.0, 515.32952798494887),
            (445.0, 519.6152422706632),
            (435, 519.6152422706632),
            (420, 493.63448015712999),
            (425.0, 484.97422611928562),
            (420.0769251104191, 476.35838481464913),
            (430.0, 476.31397208144119),
            (440.0, 458.99346400575246),
            (449.9230748895809, 458.94905127254452),
            (445.0, 450.33320996790803)
        ]
        assert guiutils.point_in_polygon((459, 485), points)
        assert guiutils.point_in_polygon((480, 523), points)
        assert guiutils.point_in_polygon((426, 480), points)
        assert guiutils.point_in_polygon((489, 455), points)
        assert not guiutils.point_in_polygon((386, 447), points)
        assert not guiutils.point_in_polygon((445, 455), points)
        assert not guiutils.point_in_polygon((500, 481), points)
        assert not guiutils.point_in_polygon((451, 514), points)

    def test_towers(self):
        labels = self.board.get_tower_labels()
        labels.sort()
        assert labels == [100, 200, 300, 400, 500, 600]


if __name__ == '__main__':
    unittest.main()
