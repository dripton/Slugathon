#!/usr/bin/env python2

import unittest
import Tkinter as tk
import ImageTk
import MasterBoard
import GUIMasterBoard
import guiutils


class MasterBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.board = MasterBoard.MasterBoard()
        self.hex = self.board.hexes[1]
        self.hex2 = self.board.hexes[2]
        self.guiboard = GUIMasterBoard.GUIMasterBoard(None, self.board)

    def testInitHex(self):
        assert self.hex.terrain == "Plains" 
        assert self.hex.x == 7
        assert self.hex.y == 5

    def testFindDirection(self):
        """Returns a direction (0 to 5) to the hex with the given label."""
        assert self.hex.find_direction(2) == 2
        assert self.hex.find_direction(1000) == 0

    def testHexInverted(self):
        assert self.hex.inverted
        assert not self.board.hexes[2].inverted

    def testExits(self):
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


    def testNeighbors(self):
        assert self.hex.neighbors[0] == self.board.hexes[1000]
        assert self.hex.neighbors[1] == None
        assert self.hex.neighbors[2] == self.board.hexes[2]
        assert self.hex.neighbors[3] == None
        assert self.hex.neighbors[4] == self.board.hexes[42]
        assert self.hex.neighbors[5] == None

    def testFlattenPointList(self):
        vertexes = [(0,1), (2,3), (4,5), (6,7), (8,9), (10,11)]
        assert (guiutils.flatten_point_list(vertexes) ==
                (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    def testRgbToTk(self):
        assert guiutils.RgbToTk((0, 0, 0)) == '#000000'
        assert guiutils.RgbToTk((255, 255, 255)) == '#FFFFFF'
        assert guiutils.RgbToTk((189, 0, 24)) == '#BD0018'

    def testBuildOverlayFilename(self):
        assert self.hex.overlay_filename == "Plains.gif"
        assert self.hex2.overlay_filename == "Woods_i.gif"

    def testFindLabelSide(self):
        assert self.hex.find_label_side() == 3
        assert self.hex2.find_label_side() == 0
        assert self.board.hexes[115].find_label_side() == 1
        assert self.board.hexes[300].find_label_side() == 4
        assert self.board.hexes[5000].find_label_side() == 2
        assert self.board.hexes[105].find_label_side() == 5


if __name__ == '__main__':
    unittest.main()
