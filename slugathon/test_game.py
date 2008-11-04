__copyright__ = "Copyright (c) 2005 David Ripton"
__license__ = "GNU GPL v2"


import time

import Game

class TestMovement(object):
    def setup_method(self, method):
        now = time.time()
        self.game = game = Game.Game("g1", "p0", now, now, 2, 6)
        game.add_player("p1")
        player0 = game.players[0]
        player1 = game.players[1]
        player0.assign_starting_tower(200)
        player1.assign_starting_tower(100)
        game.sort_players()
        game.started = True
        game.assign_color("p0", "Red")
        game.assign_color("p1", "Blue")
        game.assign_first_marker("p0", "Rd01")
        game.assign_first_marker("p1", "Bu01")
        player0.pick_marker("Rd02")
        player0.split_legion("Rd01", "Rd02",
          ["Titan", "Centaur", "Centaur", "Gargoyle"],
          ["Angel", "Ogre", "Ogre", "Gargoyle"])
        player0.done_with_splits()

    def test_all_legions(self):
        game = self.game
        print game.all_legions()
        assert len(game.all_legions()) == 3
        assert len(game.all_legions(200)) == 2
        assert len(game.all_legions(100)) == 1
        assert len(game.all_legions(300)) == 0


    def test_find_normal_moves(self):
        game = self.game
        player = self.game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = self.game.find_normal_moves(legion, masterhex, 1)
        assert moves == set([(6, 5), (10, 1), (108, 3)])

        moves = self.game.find_normal_moves(legion, masterhex, 2)
        assert moves == set([(7, 3), (11, 5), (107, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 3)
        assert moves == set([(8, 1), (12, 5), (106, 5)])

        moves = self.game.find_normal_moves(legion, masterhex, 4)
        assert moves == set([(9, 5), (13, 1), (105, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 5)
        assert moves == set([(10, 3), (14, 3), (104, 1)])

        moves = self.game.find_normal_moves(legion, masterhex, 6)
        assert moves == set([(15, 1), (11, 5), (103, 5)])

    def test_find_all_teleport_moves(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = game.find_all_teleport_moves(legion, masterhex, 1)
        assert not moves

    def test_find_all_teleport_moves2(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = game.find_all_teleport_moves(legion, masterhex, 6)
        for move in moves:
            assert move[1] == Game.TELEPORT
        hexlabels = set([move[0] for move in moves])
        print sorted(hexlabels)

        assert hexlabels == set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          15, 16, 17, 21, 37, 41, 42, 101, 102, 103, 104, 105, 106, 107, 108,
          109, 110, 111, 112, 113, 114, 115, 300, 400, 500, 600, 1000, 2000,
          3000, 4000, 6000])

    def test_find_all_moves(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = game.find_all_moves(legion, masterhex, 1)
        assert moves == set([(6, 5), (10, 1), (108, 3)])

    def test_find_all_moves2(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        masterhex = game.board.hexes[legion.hexlabel]

        moves = game.find_all_moves(legion, masterhex, 6)
        print sorted(moves)
        hexlabels = set([move[0] for move in moves])
        assert hexlabels == set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          15, 16, 17, 21, 37, 41, 42, 101, 102, 103, 104, 105, 106, 107, 108,
          109, 110, 111, 112, 113, 114, 115, 300, 400, 500, 600, 1000, 2000,
          3000, 4000, 6000])
        for hexlabel in hexlabels:
            assert (hexlabel, Game.TELEPORT) in moves
        assert (11, 5) in moves
        assert (15, 1) in moves
        assert (103, 5) in moves

    def test_can_move_legion(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        player.movement_roll = 1
        assert game.can_move_legion(player, legion, 6, 5, False, None)
        assert game.can_move_legion(player, legion, 10, 1, False, None)
        assert game.can_move_legion(player, legion, 108, 3, False, None)
        assert not game.can_move_legion(player, legion, 108, 3, True, None)

    def test_can_move_legion2(self):
        game = self.game
        player = game.players[0]
        legion = player.legions["Rd01"]
        player.movement_roll = 6
        assert game.can_move_legion(player, legion, 15, 1, False, None)
        assert game.can_move_legion(player, legion, 11, 5, False, None)
        assert game.can_move_legion(player, legion, 103, 5, False, None)
        assert not game.can_move_legion(player, legion, 16, 1, False, None)
        assert game.can_move_legion(player, legion, 16, 1, True, "Titan")
        assert game.can_move_legion(player, legion, 16, 3, True, "Titan")
        assert game.can_move_legion(player, legion, 16, 5, True, "Titan")
        assert not game.can_move_legion(player, legion, 16, 4, True, "Titan")
        assert game.can_move_legion(player, legion, 4000, 1, True, "Titan")
