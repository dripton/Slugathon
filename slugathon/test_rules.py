#!/usr/bin/env python2.3

import unittest
from sets import Set
import math
import MasterBoard
import rules
import Dice


class AssignTowersTestCase(unittest.TestCase):
    def setUp(self):
        self.board = MasterBoard.MasterBoard()
        self.labels = self.board.get_tower_labels()
        self.dice = Dice.Dice()

    def test_bad_input(self):
        try:
            rules.assign_towers(None, 1, self.dice)
        except TypeError:
            pass
        else:
            self.fail("Should have raised")

    def test_not_enough_towers(self):
        try:
            rules.assign_towers(self.labels, 7, self.dice)
        except AssertionError:
            pass
        else:
            self.fail("Should have raised")

    def _simple_helper(self, num_players):
        towers = rules.assign_towers(self.labels, num_players, self.dice)
        assert len(towers) == num_players
        for tower in towers:
            assert tower in self.labels

    def test_1_player_simple(self):
        self._simple_helper(1)

    def test_6_player_simple(self):
        self._simple_helper(6)

    def test_1_player(self):
        self._range_helper(1)

    def test_2_player(self):
        self._range_helper(2)

    def test_3_player(self):
        self._range_helper(3)

    def test_4_player(self):
        self._range_helper(4)

    def test_5_player(self):
        self._range_helper(5)

    def test_6_player(self):
        self._range_helper(6)

    def _range_helper(self, num_players):
        trials = 100
        num_towers = 6
        counts = {}
        for unused in range(trials):
            towers = rules.assign_towers(self.labels, num_players, self.dice)
            assert len(towers) == num_players
            for tower in towers:
                counts[tower] = counts.get(tower, 0) + 1
        assert len(counts) == num_towers, \
          "len(counts) is wrong: %s" % counts
        assert sum(counts.values()) == trials * num_players
        for count in counts.values():
            # XXX Do real statistical tests.
            mean = 1. * trials * num_players / num_towers
            assert math.floor(mean / 3) <= count <= math.ceil(2 * mean), \
              "counts out of range: %s" % counts

if __name__ == '__main__':
    unittest.main()
