import math
import time
import py

import MasterBoard
import Game
import Dice
import Player
import Legion
import Creature
import creaturedata


class TestAssignTowers(object):
    def setup_method(self, method):
        now = time.time()
        self.game = Game.Game("g1", "p1", now, now, 2, 6)

    def _simple_helper(self, num_players):
        for num in xrange(num_players-1):
            self.game.add_player("p%d" % (num+2))
        self.game.assign_towers()
        towers = set([player.starting_tower for player in self.game.players])
        assert len(towers) == num_players
        for tower in towers:
            assert tower in self.game.board.get_tower_labels()

    def test_1_player_simple(self):
        self._simple_helper(1)

    def test_6_player_simple(self):
        self._simple_helper(6)

    def _range_helper(self, num_players):
        trials = 100
        num_towers = 6
        counts = {}
        for num in xrange(num_players-1):
            self.game.add_player("p%d" % (num+2))
        for unused in xrange(trials):
            self.game.assign_towers()
            towers = set([player.starting_tower for player in 
              self.game.players])
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


class TestMovement(object):
    def setup_method(self, method):
        now = time.time()
        self.game = game = Game.Game("g1", "p0", now, now, 2, 6)
        game.add_player("p1")
        player0 = game.players[0]
        player1 = game.players[1]
        player0.assign_starting_tower(200)
        player1.assign_starting_tower(100)
        game.started = True
        game.assign_color("p1", "Blue")
        game.assign_color("p0", "Red")
        game.assign_first_marker("p0", "Rd01")
        game.assign_first_marker("p1", "Bu01")
        player0.pick_marker("Rd02")
        player0.split_legion("Rd01", "Rd02", 
          ["Titan", "Centaur", "Centaur", "Gargoyle"],
          ["Angel", "Ogre", "Ogre", "Gargoyle"])
        player0.done_with_splits()

    def test_friendly_legions(self):
        game = self.game
        player0 = game.players[0]
        legions = game.friendly_legions(200, player0)
        assert len(legions) == 2
        assert legions == player0.legions.values()

    def test_find_normal_moves(self):
        game = self.game
        player = self.game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = self.game.find_normal_moves(legion, masterhex, 1, 
          masterhex.find_block(), None)
        assert moves == set([(6, 5), (10, 1), (108, 3)])

        moves = self.game.find_normal_moves(legion, masterhex, 2, 
          masterhex.find_block(), None)
        assert moves == set([(7, 3), (11, 5), (107, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 3, 
          masterhex.find_block(), None)
        assert moves == set([(8, 1), (12, 5), (106, 5)])

        moves = self.game.find_normal_moves(legion, masterhex, 4, 
          masterhex.find_block(), None)
        assert moves == set([(9, 5), (13, 1), (105, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 5, 
          masterhex.find_block(), None)
        assert moves == set([(10, 3), (14, 3), (104, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 6, 
          masterhex.find_block(), None)
        assert moves == set([(15, 1), (11, 5), (103, 5)])

    def test_find_teleport_moves(self):
        game = self.game
        player = self.game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = self.game.find_all_teleport_moves(legion, masterhex, 1)
        assert not moves

        moves = self.game.find_all_teleport_moves(legion, masterhex, 6)
        for move in moves:
            assert move[1] == Game.ANY
        hexlabels = set([move[0] for move in moves])
        print sorted(hexlabels)

        assert hexlabels == set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          15, 16, 17, 21, 37, 41, 42, 101, 102, 103, 104, 105, 106, 107, 108,
          109, 110, 111, 112, 113, 114, 115, 300, 400, 500, 600, 1000, 2000,
          3000, 4000, 6000])

    def test_find_all_moves(self):
        game = self.game
        player = self.game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = self.game.find_all_moves(legion, masterhex, 1)
        assert moves == set([(6, 5), (10, 1), (108, 3)])

        moves = self.game.find_all_moves(legion, masterhex, 6)
        print sorted(moves)
        hexlabels = set([move[0] for move in moves])
        assert hexlabels == set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          15, 16, 17, 21, 37, 41, 42, 101, 102, 103, 104, 105, 106, 107, 108,
          109, 110, 111, 112, 113, 114, 115, 300, 400, 500, 600, 1000, 2000,
          3000, 4000, 6000])
        for move in moves:
            assert move[1] == Game.ANY
