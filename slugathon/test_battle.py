import time
import sys

import Game
import Battle
import Phase
import Creature

class TestBattle(object):
    def setup_method(self, method):
        now = time.time()
        self.game = Game.Game("g1", "p0", now, now, 2, 6)
        self.game.add_player("p1")
        self.player0 = self.game.players[0]
        self.player1 = self.game.players[1]
        self.player0.assign_starting_tower(200)
        self.player1.assign_starting_tower(100)
        self.game.sort_players()
        self.game.started = True
        self.game.assign_color("p0", "Red")
        self.game.assign_color("p1", "Blue")
        self.game.assign_first_marker("p0", "Rd01")
        self.game.assign_first_marker("p1", "Bu01")
        self.player0.pick_marker("Rd02")
        self.player0.split_legion("Rd01", "Rd02",
          ["Titan", "Centaur", "Ogre", "Gargoyle"],
          ["Angel", "Centaur", "Ogre", "Gargoyle"])
        self.rd01 = self.player0.legions["Rd01"]
        self.player1.pick_marker("Bu02")
        self.player1.split_legion("Bu01", "Bu02",
          ["Titan", "Centaur", "Ogre", "Gargoyle"],
          ["Angel", "Centaur", "Ogre", "Gargoyle"])
        self.bu01 = self.player1.legions["Bu01"]

    def test_battle_init(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        assert self.battle.turn == 1
        assert self.battle.defender_legion.markername == "Rd01"
        assert self.battle.attacker_legion.markername == "Bu01"
        assert self.battle.phase == Phase.MANEUVER
        assert self.battle.active_player == self.battle.defender_legion.player

    def test_hex_entry_cost(self):
        titan = Creature.Creature("Titan")
        assert self.battle.hex_entry_cost(titan, "Bramble", None) == 2
        assert self.battle.hex_entry_cost(titan, "Plains", None) == 1
        assert self.battle.hex_entry_cost(titan, "Sand", None) == 2
        assert self.battle.hex_entry_cost(titan, "Sand", "Dune") == 2
        assert self.battle.hex_entry_cost(titan, "Tower", None) == 1
        assert self.battle.hex_entry_cost(titan, "Tower", "Wall") == 2
        assert self.battle.hex_entry_cost(titan, "Drift", None) == 2
        assert self.battle.hex_entry_cost(titan, "Volcano", None) == sys.maxint
        lion = Creature.Creature("Lion")
        assert self.battle.hex_entry_cost(lion, "Bramble", None) == 2
        assert self.battle.hex_entry_cost(lion, "Plains", None) == 1
        assert self.battle.hex_entry_cost(lion, "Sand", None) == 1
        assert self.battle.hex_entry_cost(lion, "Sand", "Dune") == 1
        assert self.battle.hex_entry_cost(lion, "Tower", None) == 1
        assert self.battle.hex_entry_cost(lion, "Tower", "Wall") == 2
        assert self.battle.hex_entry_cost(lion, "Drift", None) == 2
        assert self.battle.hex_entry_cost(lion, "Volcano", None) == sys.maxint
        giant = Creature.Creature("Giant")
        assert self.battle.hex_entry_cost(giant, "Bramble", None) == 2
        assert self.battle.hex_entry_cost(giant, "Plains", None) == 1
        assert self.battle.hex_entry_cost(giant, "Sand", None) == 2
        assert self.battle.hex_entry_cost(giant, "Sand", "Dune") == 2
        assert self.battle.hex_entry_cost(giant, "Tower", None) == 1
        assert self.battle.hex_entry_cost(giant, "Tower", "Wall") == 2
        assert self.battle.hex_entry_cost(giant, "Drift", None) == 1
        assert self.battle.hex_entry_cost(giant, "Volcano", None) == sys.maxint
        dragon = Creature.Creature("Dragon")
        assert self.battle.hex_entry_cost(dragon, "Bramble", None) == 2
        assert self.battle.hex_entry_cost(dragon, "Plains", None) == 1
        assert self.battle.hex_entry_cost(dragon, "Sand", None) == 2
        assert self.battle.hex_entry_cost(dragon, "Sand", "Dune") == 2
        assert self.battle.hex_entry_cost(dragon, "Tower", None) == 1
        assert self.battle.hex_entry_cost(dragon, "Tower", "Wall") == 1
        assert self.battle.hex_entry_cost(dragon, "Drift", None) == 2
        assert self.battle.hex_entry_cost(dragon, "Volcano", None) == 1

    def test_find_moves_plains(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
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

    def test_find_moves_marsh(self):
        self.rd01.move(41, False, None, 3)
        self.bu01.move(41, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "F1", "C1", "D2", "E2", "F2", "B1", "D3", "F3",
          "A1", "B2", "D4", "E4", "F4"])
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
        set3 = set(["D1", "F1", "C1", "D2", "E2", "F2", "B1", "D3", "F3"])
        assert self.battle.find_moves(gargoyle) == set3

    def test_find_moves_brush(self):
        self.rd01.move(3, False, None, 3)
        self.bu01.move(3, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3", "C3", "D4", "E4"])
        assert self.battle.find_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "E2", "F2"])
        assert self.battle.find_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.battle.find_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2", "D3",
          "E3", "F3"])
        assert self.battle.find_moves(gargoyle) == set3

    def test_find_moves_tower(self):
        self.rd01.move(200, False, None, 3)
        self.bu01.move(200, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D5", "E4", "C4", "D4", "E3", "C3", "D3"])
        assert self.battle.find_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        assert self.battle.find_moves(ogre) == set1
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.battle.find_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        assert self.battle.find_moves(gargoyle) == set1

    def test_find_moves_jungle(self):
        self.rd01.move(26, False, None, 3)
        self.bu01.move(26, False, None, 3)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "E3", "B2", "E4"])
        assert self.battle.find_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "D2", "F2"])
        assert self.battle.find_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.battle.find_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2", 
          "E3"])
        assert self.battle.find_moves(gargoyle) == set3

    def test_find_moves_desert(self):
        self.rd01.move(7, False, None, 5)
        self.bu01.move(7, False, None, 5)
        self.battle = Battle.Battle(self.game, self.bu01, self.rd01)
        defender = self.battle.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["F4", "E5", "D6", "F3", "E4", "D5", "C5", "F2", "E3", "C4",
          "B4"])
        assert self.battle.find_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["F4", "E5", "D6"])
        assert self.battle.find_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.battle.find_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        assert self.battle.find_moves(gargoyle) == set1
