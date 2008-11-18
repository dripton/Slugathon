__copyright__ = "Copyright (c) 2008 David Ripton"
__license__ = "GNU GPL v2"


import time
import sys

import Game
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
        self.game._init_battle(self.bu01, self.rd01)
        assert self.game.battle_turn == 1
        assert self.game.defender_legion.markername == "Rd01"
        assert self.game.attacker_legion.markername == "Bu01"
        assert self.game.battle_phase == Phase.MANEUVER
        assert self.game.battle_active_player == \
          self.game.defender_legion.player

    def test_hex_entry_cost(self):
        titan = Creature.Creature("Titan")
        assert self.game.battle_hex_entry_cost(titan, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(titan, "Plains", None) == 1
        assert self.game.battle_hex_entry_cost(titan, "Sand", None) == 2
        assert self.game.battle_hex_entry_cost(titan, "Sand", "Dune") == 2
        assert self.game.battle_hex_entry_cost(titan, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(titan, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(titan, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(titan, "Volcano", None) == \
          sys.maxint
        lion = Creature.Creature("Lion")
        assert self.game.battle_hex_entry_cost(lion, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(lion, "Plains", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Sand", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Sand", "Dune") == 1
        assert self.game.battle_hex_entry_cost(lion, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(lion, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(lion, "Volcano", None) == \
          sys.maxint
        giant = Creature.Creature("Giant")
        assert self.game.battle_hex_entry_cost(giant, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(giant, "Plains", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Sand", None) == 2
        assert self.game.battle_hex_entry_cost(giant, "Sand", "Dune") == 2
        assert self.game.battle_hex_entry_cost(giant, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(giant, "Drift", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Volcano", None) == \
          sys.maxint
        dragon = Creature.Creature("Dragon")
        assert self.game.battle_hex_entry_cost(dragon, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(dragon, "Plains", None) == 1
        assert self.game.battle_hex_entry_cost(dragon, "Sand", None) == 2
        assert self.game.battle_hex_entry_cost(dragon, "Sand", "Dune") == 2
        assert self.game.battle_hex_entry_cost(dragon, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(dragon, "Tower", "Wall") == 1
        assert self.game.battle_hex_entry_cost(dragon, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(dragon, "Volcano", None) == 1

    def test_find_moves_plains(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3", "A1", "B2", "C3", "D4", "E4", "F4"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2"])
        assert self.game.find_battle_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3"])
        assert self.game.find_battle_moves(gargoyle) == set3

    def test_find_moves_marsh(self):
        self.rd01.move(41, False, None, 3)
        self.bu01.move(41, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "F1", "C1", "D2", "E2", "F2", "B1", "D3", "F3",
          "A1", "B2", "D4", "E4", "F4"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2"])
        assert self.game.find_battle_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "F1", "C1", "D2", "E2", "F2", "B1", "D3", "F3"])
        assert self.game.find_battle_moves(gargoyle) == set3

    def test_find_moves_brush(self):
        self.rd01.move(3, False, None, 3)
        self.bu01.move(3, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3", "C3", "D4", "E4"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "E2", "F2"])
        assert self.game.find_battle_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2", "D3",
          "E3", "F3"])
        assert self.game.find_battle_moves(gargoyle) == set3

    def test_find_moves_tower(self):
        self.rd01.move(200, False, None, 3)
        self.bu01.move(200, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D5", "E4", "C4", "D4", "E3", "C3", "D3"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        assert self.game.find_battle_moves(ogre) == set1
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        assert self.game.find_battle_moves(gargoyle) == set1

    def test_find_moves_jungle(self):
        self.rd01.move(26, False, None, 3)
        self.bu01.move(26, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "E3", "B2", "E4"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["D1", "E1", "F1", "D2", "F2"])
        assert self.game.find_battle_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set3 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "E3"])
        assert self.game.find_battle_moves(gargoyle) == set3

    def test_find_moves_desert(self):
        self.rd01.move(7, False, None, 5)
        self.bu01.move(7, False, None, 5)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["F4", "E5", "D6", "F3", "E4", "D5", "C5", "F2", "E3", "C4",
          "B4"])
        assert self.game.find_battle_moves(titan) == set1
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["F4", "E5", "D6"])
        assert self.game.find_battle_moves(ogre) == set2
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        assert self.game.find_battle_moves(centaur) == set1
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        assert self.game.find_battle_moves(gargoyle) == set1

    def test_find_moves_flyover(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        self.game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan = defender.creatures[0]
        assert titan.name == "Titan"
        set1 = set(["D1", "E1", "F1", "C1", "D2", "E2", "F2", "B1", "C2",
          "D3", "E3", "F3", "A1", "B2", "C3", "D4", "E4", "F4"])
        assert self.game.find_battle_moves(titan) == set1
        # Just Move It, without going through the server
        titan.move("D1")
        ogre = defender.creatures[1]
        assert ogre.name == "Ogre"
        set2 = set(["E1", "F1", "D2", "E2", "F2"])
        assert self.game.find_battle_moves(ogre) == set2
        ogre.move("E1")
        centaur = defender.creatures[2]
        assert centaur.name == "Centaur"
        set3 = set(["F1", "C1", "D2", "E2", "F2", "C2",
          "D3", "E3", "F3", "C3", "D4", "E4", "F4"])
        assert self.game.find_battle_moves(centaur) == set3
        centaur.move("F1")
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        set4 = set(["C1", "D2", "E2", "F2", "B1", "C2", "D3", "E3", "F3"])
        assert self.game.find_battle_moves(gargoyle) == set4

    def test_strikes_plains(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan1 = defender.creatures[0]
        assert game.find_target_hexlabels(titan1) == set()
        titan1.move("F2")
        assert game.find_target_hexlabels(titan1) == set()
        ogre1 = defender.creatures[1]
        assert game.find_target_hexlabels(ogre1) == set()
        ogre1.move("E2")
        assert game.find_target_hexlabels(ogre1) == set()
        centaur1 = defender.creatures[2]
        assert game.find_target_hexlabels(centaur1) == set()
        centaur1.move("D2")
        assert game.find_target_hexlabels(centaur1) == set()
        gargoyle1 = defender.creatures[3]
        assert game.find_target_hexlabels(gargoyle1) == set()
        gargoyle1.move("C1")
        assert game.find_target_hexlabels(gargoyle1) == set()
        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        titan2 = attacker.creatures[0]
        assert game.find_target_hexlabels(titan2) == set()
        titan2.move("B1")
        ogre2 = attacker.creatures[1]
        assert game.find_target_hexlabels(ogre2) == set()
        ogre2.move("B3")
        centaur2 = attacker.creatures[2]
        assert game.find_target_hexlabels(centaur2) == set()
        centaur2.move("C2")
        gargoyle2 = attacker.creatures[3]
        assert game.find_target_hexlabels(gargoyle2) == set()
        gargoyle2.move("C3")
        game.battle_phase = Phase.STRIKE
        assert game.find_target_hexlabels(titan2) == set(["C1"])
        assert titan2.number_of_dice(gargoyle1) == 6
        assert titan2.strike_number(gargoyle1) == 3
        assert game.find_target_hexlabels(ogre2) == set()
        assert game.find_target_hexlabels(centaur2) == set(["C1", "D2"])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(centaur1) == 3
        assert centaur2.strike_number(centaur1) == 4
        assert game.find_target_hexlabels(gargoyle2) == set()
        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert game.find_target_hexlabels(titan1) == set()
        assert game.find_target_hexlabels(ogre1) == set()
        assert game.find_target_hexlabels(centaur1) == set(["C2"])
        assert centaur1.number_of_dice(gargoyle2) == 3
        assert centaur1.strike_number(gargoyle2) == 3
        assert game.find_target_hexlabels(gargoyle1) == set(["B1", "C2"])
        assert gargoyle1.number_of_dice(titan2) == 4
        assert gargoyle1.strike_number(titan2) == 5
        assert gargoyle1.number_of_dice(centaur2) == 4
        assert gargoyle1.strike_number(centaur2) == 5
        game.clear_battle_flags()
        game.battle_turn = 2
        game.battle_phase = Phase.MANEUVER
        assert game.find_battle_moves(titan1)
        assert game.find_battle_moves(ogre1)
        assert not game.find_battle_moves(centaur1)
        assert not game.find_battle_moves(gargoyle1)
        titan1.move("D4")
        ogre1.move("D3")
        game.battle_phase = Phase.STRIKE
        assert game.find_target_hexlabels(titan1) == set(["C3"])
        assert titan1.number_of_dice(gargoyle2) == 6
        assert titan1.strike_number(gargoyle2) == 3
        assert game.find_target_hexlabels(ogre1) == set(["C2", "C3"])
        assert ogre1.number_of_dice(gargoyle2) == 6
        assert ogre1.strike_number(gargoyle2) == 5
        assert ogre1.number_of_dice(centaur2) == 6
        assert ogre1.strike_number(centaur2) == 6
        assert game.find_target_hexlabels(centaur1) == set(["C2"])
        assert centaur1.number_of_dice(centaur2) == 3
        assert centaur1.strike_number(centaur2) == 4
        assert game.find_target_hexlabels(gargoyle1) == set(["B1", "C2"])
        assert gargoyle1.number_of_dice(centaur2) == 4
        assert gargoyle1.strike_number(centaur2) == 5
        assert gargoyle1.number_of_dice(titan2) == 4
        assert gargoyle1.strike_number(titan2) == 5
        game.battle_active_legion = attacker
        game.battle_phase = Phase.COUNTERSTRIKE
        assert game.find_target_hexlabels(titan2) == set(["C1"])
        assert titan2.number_of_dice(gargoyle1) == 6
        assert titan2.strike_number(gargoyle1) == 3
        assert game.find_target_hexlabels(ogre2) == set()
        assert game.find_target_hexlabels(centaur2) == set(["C1", "D2", "D3"])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(centaur1) == 3
        assert centaur2.strike_number(centaur1) == 4
        assert centaur2.number_of_dice(ogre1) == 3
        assert centaur2.strike_number(ogre1) == 2
        assert game.find_target_hexlabels(gargoyle2) == set(["D3", "D4"])
        assert gargoyle2.number_of_dice(titan1) == 4
        assert gargoyle2.strike_number(titan1) == 5
        assert gargoyle2.number_of_dice(ogre1) == 4
        assert gargoyle2.strike_number(ogre1) == 3
