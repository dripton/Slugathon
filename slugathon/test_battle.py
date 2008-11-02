import time

import Game
import Battle
import Phase

class TestBattle(object):
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
          ["Titan", "Centaur", "Ogre", "Gargoyle"],
          ["Angel", "Centaur", "Ogre", "Gargoyle"])
        rd01 = player0.legions["Rd01"]
        rd01.move(6, False, None, 3)
        player1.pick_marker("Bu02")
        player1.split_legion("Bu01", "Bu02", 
          ["Titan", "Centaur", "Ogre", "Gargoyle"],
          ["Angel", "Centaur", "Ogre", "Gargoyle"])
        bu01 = player1.legions["Bu01"]
        bu01.move(6, False, None, 3)
        self.battle = Battle.Battle(game, bu01, rd01)

    def test_battle_init(self):
        assert self.battle.turn == 1
        assert self.battle.defender_legion.markername == "Rd01"
        assert self.battle.attacker_legion.markername == "Bu01"
        assert self.battle.phase == Phase.MANEUVER
        assert self.battle.active_player == self.battle.defender_legion.player

    def test_find_moves1(self):
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3", "A1", "B2", "C3", "D4", "E4", "F4"])
        assert self.battle.find_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2"])
        assert self.battle.find_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.battle.find_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3"])
        assert self.battle.find_moves(gargoyle) == set3
