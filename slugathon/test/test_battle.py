__copyright__ = "Copyright (c) 2008-2009 David Ripton"
__license__ = "GNU GPL v2"


import time
from sys import maxint

from slugathon.game import Game, Phase, Creature, Legion

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
        assert self.game.battle_hex_entry_cost(titan, "Plain", None) == 1
        assert self.game.battle_hex_entry_cost(titan, "Sand", None) == 2
        assert self.game.battle_hex_entry_cost(titan, "Sand", "Dune") == 2
        assert self.game.battle_hex_entry_cost(titan, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(titan, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(titan, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(titan, "Volcano", None) == \
          maxint
        lion = Creature.Creature("Lion")
        assert self.game.battle_hex_entry_cost(lion, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(lion, "Plain", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Sand", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Sand", "Dune") == 1
        assert self.game.battle_hex_entry_cost(lion, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(lion, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(lion, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(lion, "Volcano", None) == \
          maxint
        giant = Creature.Creature("Giant")
        assert self.game.battle_hex_entry_cost(giant, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(giant, "Plain", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Sand", None) == 2
        assert self.game.battle_hex_entry_cost(giant, "Sand", "Dune") == 2
        assert self.game.battle_hex_entry_cost(giant, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Tower", "Wall") == 2
        assert self.game.battle_hex_entry_cost(giant, "Drift", None) == 1
        assert self.game.battle_hex_entry_cost(giant, "Volcano", None) == \
          maxint
        dragon = Creature.Creature("Dragon")
        assert self.game.battle_hex_entry_cost(dragon, "Bramble", None) == 2
        assert self.game.battle_hex_entry_cost(dragon, "Plain", None) == 1
        assert self.game.battle_hex_entry_cost(dragon, "Sand", None) == 1
        assert self.game.battle_hex_entry_cost(dragon, "Sand", "Dune") == 1
        assert self.game.battle_hex_entry_cost(dragon, "Tower", None) == 1
        assert self.game.battle_hex_entry_cost(dragon, "Tower", "Wall") == 1
        assert self.game.battle_hex_entry_cost(dragon, "Drift", None) == 2
        assert self.game.battle_hex_entry_cost(dragon, "Volcano", None) == 1

    def test_find_moves_plain(self):
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
        set3 = set(["F4", "E5", "D6", "F3", "E4", "D5", "C5", "F2", "E3", "C4",
          "B4", "D4"])
        gargoyle = defender.creatures[3]
        assert gargoyle.name == "Gargoyle"
        assert self.game.find_battle_moves(gargoyle) == set3

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

    def test_strikes_plain(self):
        self.rd01.move(6, False, None, 3)
        self.bu01.move(6, False, None, 3)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("F2")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("E2")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("D2")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("C1")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        titan2.move("B1")
        ogre2 = attacker.creatures[1]
        assert ogre2.engaged_enemies == set()
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("B3")
        centaur2 = attacker.creatures[2]
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        centaur2.move("C2")
        assert centaur2.find_target_hexlabels() == set(["C1", "D2"])
        assert centaur2.engaged_enemies == set([centaur1, gargoyle1])
        gargoyle2 = attacker.creatures[3]
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        gargoyle2.move("C3")
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()

        game.battle_phase = Phase.STRIKE
        assert titan2.find_target_hexlabels() == set(["C1"])
        assert titan2.number_of_dice(gargoyle1) == 6
        assert titan2.strike_number(gargoyle1) == 3
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        assert centaur2.find_target_hexlabels() == set(["C1", "D2"])
        assert centaur2.engaged_enemies == set([centaur1, gargoyle1])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(centaur1) == 3
        assert centaur2.strike_number(centaur1) == 4
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        assert centaur1.find_target_hexlabels() == set(["C2"])
        assert centaur1.engaged_enemies == set([centaur2])
        assert centaur1.number_of_dice(gargoyle2) == 0
        assert centaur1.strike_number(gargoyle2) == 3
        assert gargoyle1.find_target_hexlabels() == set(["B1", "C2"])
        assert gargoyle1.engaged_enemies == set([centaur2, titan2])
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
        assert titan1.find_target_hexlabels() == set(["C3"])
        assert titan1.engaged_enemies == set([gargoyle2])
        assert titan1.number_of_dice(gargoyle2) == 6
        assert titan1.strike_number(gargoyle2) == 3
        assert ogre1.find_target_hexlabels() == set(["C2", "C3"])
        assert ogre1.engaged_enemies == set([centaur2, gargoyle2])
        assert ogre1.number_of_dice(gargoyle2) == 6
        assert ogre1.strike_number(gargoyle2) == 5
        assert ogre1.number_of_dice(centaur2) == 6
        assert ogre1.strike_number(centaur2) == 6
        assert centaur1.find_target_hexlabels() == set(["C2"])
        assert centaur1.engaged_enemies == set([centaur2])
        assert centaur1.number_of_dice(centaur2) == 3
        assert centaur1.strike_number(centaur2) == 4
        assert gargoyle1.find_target_hexlabels() == set(["B1", "C2"])
        assert gargoyle1.engaged_enemies == set([centaur2, titan2])
        assert gargoyle1.number_of_dice(centaur2) == 4
        assert gargoyle1.strike_number(centaur2) == 5
        assert gargoyle1.number_of_dice(titan2) == 4
        assert gargoyle1.strike_number(titan2) == 5

        game.battle_active_legion = attacker
        game.battle_phase = Phase.COUNTERSTRIKE
        assert titan2.find_target_hexlabels() == set(["C1"])
        assert titan2.engaged_enemies == set([gargoyle1])
        assert titan2.number_of_dice(gargoyle1) == 6
        assert titan2.strike_number(gargoyle1) == 3
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        assert centaur2.find_target_hexlabels() == set(["C1", "D2", "D3"])
        assert centaur2.engaged_enemies == set([centaur1, ogre1, gargoyle1])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(centaur1) == 3
        assert centaur2.strike_number(centaur1) == 4
        assert centaur2.number_of_dice(ogre1) == 3
        assert centaur2.strike_number(ogre1) == 2
        assert gargoyle2.find_target_hexlabels() == set(["D3", "D4"])
        assert gargoyle2.engaged_enemies == set([ogre1, titan1])
        assert gargoyle2.number_of_dice(titan1) == 4
        assert gargoyle2.strike_number(titan1) == 5
        assert gargoyle2.number_of_dice(ogre1) == 4
        assert gargoyle2.strike_number(ogre1) == 3

    def test_strikes_plain2(self):
        rd02 = Legion.Legion(self.player0, "Rd02", Creature.n2c(["Angel",
          "Ranger"]), 1)
        self.player0.legions["Rd02"] = rd02
        bu02 = Legion.Legion(self.player0, "Bu02", Creature.n2c(["Troll"]), 1)
        self.player1.legions["Bu02"] = bu02
        troll1 = bu02.creatures[0]
        angel1 = rd02.creatures[0]
        ranger1 = rd02.creatures[1]
        game = self.game
        defender = bu02
        attacker = rd02

        rd02.entry_side = 1
        game._init_battle(rd02, bu02)
        troll1.move("B2")
        game.battle_active_legion = attacker
        game.battle_phase = Phase.MANEUVER
        angel1.move("C2")
        ranger1.move("C1")
        game.battle_phase = Phase.STRIKE
        assert angel1.engaged_enemies == set([troll1])
        assert angel1.number_of_dice(troll1) == 6
        assert angel1.strike_number(troll1) == 2
        assert ranger1.engaged_enemies == set()
        assert ranger1.has_los_to("B2")
        assert ranger1.rangestrike_targets == set([troll1])
        assert ranger1.number_of_dice(troll1) == 2
        assert ranger1.strike_number(troll1) == 2

        rd02.entry_side = 3
        game._init_battle(rd02, bu02)
        troll1.move("B2")
        game.battle_active_legion = attacker
        game.battle_phase = Phase.MANEUVER
        angel1.move("C2")
        ranger1.move("C1")
        game.battle_phase = Phase.STRIKE
        assert angel1.engaged_enemies == set([troll1])
        assert angel1.number_of_dice(troll1) == 6
        assert angel1.strike_number(troll1) == 2
        assert ranger1.engaged_enemies == set()
        assert ranger1.has_los_to("B2")
        assert ranger1.rangestrike_targets == set([troll1])
        assert ranger1.number_of_dice(troll1) == 2
        assert ranger1.strike_number(troll1) == 2

        rd02.entry_side = 5
        game._init_battle(rd02, bu02)
        troll1.move("B2")
        game.battle_active_legion = attacker
        game.battle_phase = Phase.MANEUVER
        angel1.move("C2")
        ranger1.move("C1")
        game.battle_phase = Phase.STRIKE
        assert angel1.engaged_enemies == set([troll1])
        assert angel1.number_of_dice(troll1) == 6
        assert angel1.strike_number(troll1) == 2
        assert ranger1.engaged_enemies == set()
        assert ranger1.has_los_to("B2")
        assert ranger1.rangestrike_targets == set([troll1])
        assert ranger1.number_of_dice(troll1) == 2
        assert ranger1.strike_number(troll1) == 2

    def test_strikes_marsh(self):
        self.rd01.move(41, False, None, 5)
        self.bu01.move(41, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("D5")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("C5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("E4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()

    def test_strikes_bramble(self):
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.rd01.creatures.append(Creature.Creature("Gorgon"))
        self.bu01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Gorgon"))
        self.rd01.move(3, False, None, 5)
        self.bu01.move(3, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("E4")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("C5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("C4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        ranger1 = defender.creatures[4]
        ranger1.legion = defender
        ranger1.move("D4")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()
        gorgon1 = defender.creatures[5]
        gorgon1.legion = defender
        gorgon1.move("E3")
        assert gorgon1.find_target_hexlabels() == set()
        assert gorgon1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("A2")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        centaur2.move("D3")
        assert centaur2.find_target_hexlabels() == set(["D4", "E3"])
        assert centaur2.engaged_enemies == set([ranger1, gorgon1])
        assert centaur2.number_of_dice(ranger1) == 3
        assert centaur2.strike_number(ranger1) == 4
        assert centaur2.number_of_dice(gorgon1) == 3
        assert centaur2.strike_number(gorgon1) == 4
        gargoyle2 = attacker.creatures[3]
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        gargoyle2.move("B3")
        assert gargoyle2.find_target_hexlabels() == set(["C4"])
        assert gargoyle2.engaged_enemies == set([gargoyle1])
        assert gargoyle2.number_of_dice(gargoyle1) == 4
        assert gargoyle2.strike_number(gargoyle1) == 4
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("A1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        ranger2 = attacker.creatures[4]
        ranger2.legion = attacker
        ranger2.move("C2")
        assert ranger2.find_target_hexlabels() == set(["C4", "D4"])
        assert ranger2.engaged_enemies == set([])
        assert ranger2.number_of_dice(gargoyle1) == 2
        assert ranger2.strike_number(gargoyle1) == 4
        assert ranger2.number_of_dice(ranger1) == 2
        assert ranger2.strike_number(ranger1) == 4
        gorgon2 = attacker.creatures[5]
        gorgon2.legion = attacker
        gorgon2.move("D2")
        assert gorgon2.find_target_hexlabels() == set(["E3"])
        assert gorgon2.engaged_enemies == set([])
        assert gorgon2.number_of_dice(gorgon1) == 3
        assert gorgon2.strike_number(gorgon1) == 4

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set([gargoyle2])
        assert gargoyle1.number_of_dice(gargoyle2) == 4
        assert gargoyle1.strike_number(gargoyle2) == 4
        assert ranger1.engaged_enemies == set([centaur2])
        assert ranger1.number_of_dice(centaur2) == 4
        assert ranger1.strike_number(centaur2) == 4
        assert gorgon1.engaged_enemies == set([centaur2])
        assert gorgon1.number_of_dice(centaur2) == 6
        assert gorgon1.strike_number(centaur2) == 5

        centaur1.move("A3")
        titan1.move("F2")
        game.battle_phase = Phase.STRIKE
        assert centaur1.engaged_enemies == set([ogre2, gargoyle2])
        assert centaur1.number_of_dice(ogre2) == 3
        assert centaur1.strike_number(ogre2) == 3
        assert centaur1.number_of_dice(gargoyle2) == 3
        assert centaur1.strike_number(gargoyle2) == 4

        game.battle_active_legion = attacker
        assert gorgon2.find_target_hexlabels() == set(["E3"])
        ranger2.move("D6")
        assert ranger2.find_target_hexlabels() == set(["E4", "D4", "C4", "A3"])
        assert ranger2.number_of_dice(gargoyle1) == 2
        assert ranger2.strike_number(gargoyle1) == 4
        assert ranger2.number_of_dice(ranger1) == 2
        assert ranger2.strike_number(ranger1) == 5
        assert ranger2.number_of_dice(ogre1) == 2
        assert ranger2.strike_number(ogre1) == 2
        assert ranger2.number_of_dice(centaur1) == 2
        assert ranger2.strike_number(centaur1) == 5

    def test_strikes_tower(self):
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.rd01.creatures.append(Creature.Creature("Gorgon"))
        self.bu01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Gorgon"))
        self.rd01.move(100, False, None, 5)
        self.bu01.move(100, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("C3")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("D3")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("C4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("D4")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        ranger1 = defender.creatures[4]
        ranger1.legion = defender
        ranger1.move("E3")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()
        gorgon1 = defender.creatures[5]
        gorgon1.legion = defender
        gorgon1.move("D5")
        assert gorgon1.find_target_hexlabels() == set()
        assert gorgon1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("C2")
        assert ogre2.find_target_hexlabels() == set(["C3", "D3"])
        assert ogre2.engaged_enemies == set([ogre1, centaur1])
        assert ogre2.number_of_dice(ogre1) == 6
        assert ogre2.strike_number(ogre1) == 5
        assert ogre2.number_of_dice(centaur1) == 6
        assert ogre2.strike_number(centaur1) == 6
        centaur2 = attacker.creatures[2]
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        centaur2.move("E2")
        assert centaur2.find_target_hexlabels() == set(["D3", "E3"])
        assert centaur2.engaged_enemies == set([ranger1, centaur1])
        assert centaur2.number_of_dice(ranger1) == 3
        assert centaur2.strike_number(ranger1) == 5
        assert centaur2.number_of_dice(centaur1) == 3
        assert centaur2.strike_number(centaur1) == 5
        gargoyle2 = attacker.creatures[3]
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        gargoyle2.move("B2")
        assert gargoyle2.find_target_hexlabels() == set(["C3"])
        assert gargoyle2.engaged_enemies == set([ogre1])
        assert gargoyle2.number_of_dice(ogre1) == 4
        assert gargoyle2.strike_number(ogre1) == 4
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        ranger2 = attacker.creatures[4]
        ranger2.legion = attacker
        ranger2.move("F1")
        assert ranger2.find_target_hexlabels() == set(["E3"])
        assert ranger2.engaged_enemies == set([])
        assert ranger2.number_of_dice(ranger1) == 2
        assert ranger2.strike_number(ranger1) == 5
        gorgon2 = attacker.creatures[5]
        gorgon2.legion = attacker
        gorgon2.move("D2")
        assert gorgon2.find_target_hexlabels() == set(["D3"])
        assert gorgon2.engaged_enemies == set([centaur1])
        assert gorgon2.number_of_dice(centaur1) == 6
        assert gorgon2.strike_number(centaur1) == 6

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert gorgon1.engaged_enemies == set()
        assert ranger1.engaged_enemies == set([centaur2])
        assert ranger1.number_of_dice(centaur2) == 4
        assert ranger1.strike_number(centaur2) == 3
        assert ogre1.engaged_enemies == set([gargoyle2, ogre2])
        assert ogre1.number_of_dice(gargoyle2) == 6
        assert ogre1.strike_number(gargoyle2) == 4
        assert ogre1.number_of_dice(ogre2) == 6
        assert ogre1.strike_number(ogre2) == 3

    def test_strikes_tower2(self):
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Gorgon"))
        self.rd01.move(100, False, None, 5)
        self.bu01.move(100, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("C3")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("D5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("C4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("E4")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        ranger1 = defender.creatures[4]
        ranger1.legion = defender
        ranger1.move("D4")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("C2")
        assert ogre2.find_target_hexlabels() == set(["C3"])
        assert ogre2.engaged_enemies == set([ogre1])
        assert ogre2.number_of_dice(ogre1) == 6
        assert ogre2.strike_number(ogre1) == 5
        centaur2 = attacker.creatures[2]
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        centaur2.move("E1")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        gargoyle2.move("B2")
        assert gargoyle2.find_target_hexlabels() == set(["C3"])
        assert gargoyle2.engaged_enemies == set([ogre1])
        assert gargoyle2.number_of_dice(ogre1) == 4
        assert gargoyle2.strike_number(ogre1) == 4
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set([])
        ranger2 = attacker.creatures[4]
        ranger2.legion = attacker
        ranger2.move("F1")
        assert ranger2.engaged_enemies == set()
        assert ranger2.find_target_hexlabels() == set(["D4"])
        assert ranger2.number_of_dice(ranger1) == 2
        assert ranger2.strike_number(ranger1) == 6
        gorgon2 = attacker.creatures[5]
        gorgon2.legion = attacker
        gorgon2.move("D2")
        assert gorgon2.find_target_hexlabels() == set()
        assert gorgon2.engaged_enemies == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert ranger1.engaged_enemies == set()
        assert ranger1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set([gargoyle2, ogre2])
        assert ogre1.number_of_dice(gargoyle2) == 6
        assert ogre1.strike_number(gargoyle2) == 4
        assert ogre1.number_of_dice(ogre2) == 6
        assert ogre1.strike_number(ogre2) == 3

        game.battle_phase = Phase.STRIKE
        assert ranger1.find_target_hexlabels() == set(["E1", "F1"])
        assert ranger1.number_of_dice(centaur2) == 2
        assert ranger1.strike_number(centaur2) == 5
        assert ranger1.number_of_dice(ranger2) == 2
        assert ranger1.strike_number(ranger2) == 5

    def test_strikes_tower3(self):
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Ranger"))
        self.rd01.move(100, False, None, 5)
        self.bu01.move(100, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("D5")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("D4")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("C4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("E4")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        ranger1 = defender.creatures[4]
        ranger1.legion = defender
        ranger1.move("C3")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("A2")
        assert ogre2.find_target_hexlabels() == set()
        centaur2 = attacker.creatures[2]
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        centaur2.move("E1")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        gargoyle2.move("A1")
        assert gargoyle2.find_target_hexlabels() == set()
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set([])
        ranger2 = attacker.creatures[4]
        ranger2.legion = attacker
        ranger2.move("E2")
        assert ranger2.engaged_enemies == set()
        assert ranger2.find_target_hexlabels() == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert ranger1.engaged_enemies == set()
        assert ranger1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()

        game.battle_phase = Phase.STRIKE
        assert ranger1.find_target_hexlabels() == set(["A1", "A2"])
        assert ranger1.number_of_dice(gargoyle2) == 2
        assert ranger1.strike_number(gargoyle2) == 3
        assert ranger1.number_of_dice(ogre2) == 2
        assert ranger1.strike_number(ogre2) == 2


    def test_strikes_mountains(self):
        self.rd01.creatures.append(Creature.Creature("Lion"))
        self.rd01.creatures.append(Creature.Creature("Dragon"))
        self.bu01.creatures.append(Creature.Creature("Minotaur"))
        self.bu01.creatures.append(Creature.Creature("Unicorn"))
        self.rd01.move(1000, False, None, 5)
        self.bu01.move(1000, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        ogre1 = defender.creatures[1]
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        ogre1.move("C5")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        centaur1 = defender.creatures[2]
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        centaur1.move("B4")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        gargoyle1.move("E3")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        titan1.move("D5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        lion1 = defender.creatures[4]
        lion1.legion = defender
        lion1.move("C4")
        assert lion1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        dragon1 = defender.creatures[5]
        dragon1.legion = defender
        dragon1.move("D4")
        assert dragon1.find_target_hexlabels() == set()
        assert dragon1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("B2")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        centaur2.move("D3")
        assert centaur2.find_target_hexlabels() == set(["D4", "E3"])
        assert centaur2.engaged_enemies == set([dragon1, gargoyle1])
        assert centaur2.number_of_dice(dragon1) == 3
        assert centaur2.strike_number(dragon1) == 4
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        gargoyle2 = attacker.creatures[3]
        gargoyle2.move("A3")
        assert gargoyle2.find_target_hexlabels() == set(["B4"])
        assert gargoyle2.engaged_enemies == set([centaur1])
        assert gargoyle2.number_of_dice(centaur1) == 4
        assert gargoyle2.strike_number(centaur1) == 6
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        minotaur2 = attacker.creatures[4]
        minotaur2.legion = attacker
        minotaur2.move("F1")
        assert minotaur2.find_target_hexlabels() == set(["E3"])
        assert minotaur2.engaged_enemies == set([])
        assert minotaur2.number_of_dice(gargoyle1) == 2
        assert minotaur2.strike_number(gargoyle1) == 3
        unicorn2 = attacker.creatures[5]
        unicorn2.legion = attacker
        unicorn2.move("B3")
        assert unicorn2.find_target_hexlabels() == set(["B4", "C4"])
        assert unicorn2.engaged_enemies == set([centaur1, lion1])
        assert unicorn2.number_of_dice(centaur1) == 6
        assert unicorn2.strike_number(centaur1) == 4
        assert unicorn2.number_of_dice(lion1) == 6
        assert unicorn2.strike_number(lion1) == 3

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set([centaur2])
        assert dragon1.engaged_enemies == set([centaur2])
        assert dragon1.number_of_dice(centaur2) == 12
        assert dragon1.strike_number(centaur2) == 5
        assert lion1.engaged_enemies == set([unicorn2])
        assert lion1.number_of_dice(unicorn2) == 6
        assert lion1.strike_number(unicorn2) == 5
        assert ogre1.engaged_enemies == set()
        assert titan1.engaged_enemies == set()

    def test_strikes_desert(self):
        self.rd01.creatures.append(Creature.Creature("Lion"))
        self.rd01.creatures.append(Creature.Creature("Hydra"))
        self.bu01.creatures.append(Creature.Creature("Lion"))
        self.bu01.creatures.append(Creature.Creature("Griffon"))
        self.rd01.move(118, False, None, 5)
        self.bu01.move(118, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        centaur1 = defender.creatures[2]
        centaur1.move("D5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        ogre1 = defender.creatures[1]
        ogre1.move("D6")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        gargoyle1.move("F4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        lion1 = defender.creatures[4]
        lion1.legion = defender
        lion1.move("E4")
        assert lion1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        hydra1 = defender.creatures[5]
        hydra1.legion = defender
        hydra1.move("D4")
        assert hydra1.find_target_hexlabels() == set()
        assert hydra1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("C2")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        centaur2.move("D3")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        gargoyle2.move("C3")
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        lion2 = attacker.creatures[4]
        lion2.legion = attacker
        lion2.move("B3")
        assert lion2.find_target_hexlabels() == set()
        assert lion2.engaged_enemies == set([])
        griffon2 = attacker.creatures[5]
        griffon2.legion = attacker
        griffon2.move("B4")
        assert griffon2.find_target_hexlabels() == set()
        assert griffon2.engaged_enemies == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert hydra1.engaged_enemies == set()
        assert hydra1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        assert ogre1.engaged_enemies == set()
        assert titan1.engaged_enemies == set()

        game.battle_phase = Phase.STRIKE
        assert hydra1.find_target_hexlabels() == set(["B3", "B4", "C2"])
        assert hydra1.number_of_dice(lion2) == 5
        assert hydra1.strike_number(lion2) == 4
        assert hydra1.number_of_dice(griffon2) == 5
        assert hydra1.strike_number(griffon2) == 5
        assert hydra1.number_of_dice(ogre2) == 5
        assert hydra1.strike_number(ogre2) == 3

        game.battle_active_legion = attacker
        game.battle_phase = Phase.COUNTERSTRIKE
        game.battle_phase = Phase.MOVE
        griffon2.move("C5")
        centaur2.move("F3")
        lion2.move("C4")
        gargoyle2.move("E3")
        ogre2.move("C3")
        titan2.move("B2")
        game.battle_phase = Phase.STRIKE
        assert griffon2.engaged_enemies == set([centaur1, ogre1])
        assert griffon2.number_of_dice(centaur1) == 5
        assert griffon2.strike_number(centaur1) == 4
        assert griffon2.number_of_dice(ogre1) == 5
        assert griffon2.strike_number(ogre1) == 2
        assert centaur2.engaged_enemies == set([gargoyle1, lion1])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(lion1) == 2
        assert centaur2.strike_number(lion1) == 3
        assert lion2.engaged_enemies == set([centaur1, hydra1])
        assert lion2.number_of_dice(centaur1) == 5
        assert lion2.strike_number(centaur1) == 5
        assert lion2.number_of_dice(hydra1) == 5
        assert lion2.strike_number(hydra1) == 4
        assert gargoyle2.engaged_enemies == set([lion1, hydra1])
        assert gargoyle2.number_of_dice(lion1) == 3
        assert gargoyle2.strike_number(lion1) == 4
        assert gargoyle2.number_of_dice(hydra1) == 3
        assert gargoyle2.strike_number(hydra1) == 4
        assert ogre2.engaged_enemies == set()
        assert titan2.engaged_enemies == set()

    def test_strikes_desert2(self):
        self.rd01.creatures.append(Creature.Creature("Lion"))
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Lion"))
        self.bu01.creatures.append(Creature.Creature("Griffon"))
        self.rd01.move(118, False, None, 5)
        self.bu01.move(118, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        centaur1 = defender.creatures[2]
        centaur1.move("D5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        ogre1 = defender.creatures[1]
        ogre1.move("D6")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        gargoyle1.move("F4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        lion1 = defender.creatures[4]
        lion1.legion = defender
        lion1.move("E4")
        assert lion1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        ranger1 = defender.creatures[5]
        ranger1.legion = defender
        ranger1.move("D4")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("C2")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        centaur2.move("D3")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        gargoyle2.move("C3")
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        lion2 = attacker.creatures[4]
        lion2.legion = attacker
        lion2.move("B3")
        assert lion2.find_target_hexlabels() == set()
        assert lion2.engaged_enemies == set([])
        griffon2 = attacker.creatures[5]
        griffon2.legion = attacker
        griffon2.move("A1")
        assert griffon2.find_target_hexlabels() == set()
        assert griffon2.engaged_enemies == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert ranger1.engaged_enemies == set()
        assert ranger1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        assert ogre1.engaged_enemies == set()
        assert titan1.engaged_enemies == set()

        game.battle_phase = Phase.STRIKE
        assert ranger1.find_target_hexlabels() == set(["B3", "C2"])
        assert ranger1.number_of_dice(lion2) == 2
        assert ranger1.strike_number(lion2) == 3
        assert ranger1.number_of_dice(ogre2) == 2
        assert ranger1.strike_number(ogre2) == 2

        game.battle_active_legion = attacker
        game.battle_phase = Phase.COUNTERSTRIKE
        game.battle_phase = Phase.MOVE
        griffon2.move("C5")
        centaur2.move("F3")
        lion2.move("C4")
        gargoyle2.move("E3")
        ogre2.move("C3")
        titan2.move("B2")
        game.battle_phase = Phase.STRIKE
        assert griffon2.engaged_enemies == set([centaur1, ogre1])
        assert griffon2.number_of_dice(centaur1) == 5
        assert griffon2.strike_number(centaur1) == 4
        assert griffon2.number_of_dice(ogre1) == 5
        assert griffon2.strike_number(ogre1) == 2
        assert centaur2.engaged_enemies == set([gargoyle1, lion1])
        assert centaur2.number_of_dice(gargoyle1) == 3
        assert centaur2.strike_number(gargoyle1) == 3
        assert centaur2.number_of_dice(lion1) == 2
        assert centaur2.strike_number(lion1) == 3
        assert lion2.engaged_enemies == set([centaur1, ranger1])
        assert lion2.number_of_dice(centaur1) == 5
        assert lion2.strike_number(centaur1) == 5
        assert lion2.number_of_dice(ranger1) == 5
        assert lion2.strike_number(ranger1) == 5
        assert gargoyle2.engaged_enemies == set([lion1, ranger1])
        assert gargoyle2.number_of_dice(lion1) == 3
        assert gargoyle2.strike_number(lion1) == 4
        assert gargoyle2.number_of_dice(ranger1) == 3
        assert gargoyle2.strike_number(ranger1) == 5
        assert ogre2.engaged_enemies == set()
        assert titan2.engaged_enemies == set()

    def test_strikes_desert3(self):
        self.rd01.creatures.append(Creature.Creature("Lion"))
        self.rd01.creatures.append(Creature.Creature("Ranger"))
        self.bu01.creatures.append(Creature.Creature("Lion"))
        self.bu01.creatures.append(Creature.Creature("Ranger"))
        self.rd01.move(118, False, None, 5)
        self.bu01.move(118, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        centaur1 = defender.creatures[2]
        centaur1.move("D5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        ogre1 = defender.creatures[1]
        ogre1.move("D6")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        gargoyle1.move("C4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        lion1 = defender.creatures[4]
        lion1.legion = defender
        lion1.move("E4")
        assert lion1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        ranger1 = defender.creatures[5]
        ranger1.legion = defender
        ranger1.move("D4")
        assert ranger1.find_target_hexlabels() == set()
        assert ranger1.engaged_enemies == set()

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.STRIKE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("C2")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        centaur2.move("D3")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        gargoyle2.move("C3")
        assert gargoyle2.find_target_hexlabels() == set(["C4"])
        assert gargoyle2.engaged_enemies == set([gargoyle1])
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        lion2 = attacker.creatures[4]
        lion2.legion = attacker
        lion2.move("B3")
        assert lion2.find_target_hexlabels() == set(["C4"])
        assert lion2.engaged_enemies == set([gargoyle1])
        ranger2 = attacker.creatures[5]
        ranger2.legion = attacker
        ranger2.move("A2")
        assert ranger2.find_target_hexlabels() == set()
        assert ranger2.engaged_enemies == set()

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set([gargoyle2, lion2])
        assert ranger1.engaged_enemies == set()
        assert ranger1.find_target_hexlabels() == set()
        assert lion1.engaged_enemies == set()
        assert ogre1.engaged_enemies == set()
        assert titan1.engaged_enemies == set()

        game.battle_phase = Phase.STRIKE
        assert ranger1.find_target_hexlabels() == set(["B3", "C2"])
        assert ranger1.number_of_dice(lion2) == 2
        assert ranger1.strike_number(lion2) == 3
        assert ranger1.number_of_dice(ogre2) == 2
        assert ranger1.strike_number(ogre2) == 2

        game.battle_active_legion = attacker
        game.battle_phase = Phase.COUNTERSTRIKE
        game.battle_phase = Phase.MOVE
        ranger2.move("C5")
        centaur2.move("F3")
        lion2.move("C4")
        gargoyle2.move("E3")
        ogre2.move("C3")
        titan2.move("B2")
        game.battle_phase = Phase.STRIKE
        assert ranger2.engaged_enemies == set([centaur1, ogre1, gargoyle1])
        assert ranger2.number_of_dice(centaur1) == 4
        assert ranger2.strike_number(centaur1) == 4
        assert ranger2.number_of_dice(ogre1) == 4
        assert ranger2.strike_number(ogre1) == 2
        assert ranger2.number_of_dice(gargoyle1) == 4
        assert ranger2.strike_number(gargoyle1) == 3
        assert centaur2.engaged_enemies == set([lion1])
        assert centaur2.number_of_dice(lion1) == 2
        assert centaur2.strike_number(lion1) == 3
        assert lion2.engaged_enemies == set([centaur1, ranger1])
        assert lion2.number_of_dice(centaur1) == 5
        assert lion2.strike_number(centaur1) == 5
        assert lion2.number_of_dice(ranger1) == 5
        assert lion2.strike_number(ranger1) == 5
        assert gargoyle2.engaged_enemies == set([lion1, ranger1])
        assert gargoyle2.number_of_dice(lion1) == 3
        assert gargoyle2.strike_number(lion1) == 4
        assert gargoyle2.number_of_dice(ranger1) == 3
        assert gargoyle2.strike_number(ranger1) == 5
        assert ogre2.engaged_enemies == set([gargoyle1])
        assert ogre2.number_of_dice(gargoyle1) == 6
        assert ogre2.strike_number(gargoyle1) == 5
        assert titan2.engaged_enemies == set()

    def test_strikes_tundra(self):
        self.rd01.creatures.append(Creature.Creature("Troll"))
        self.rd01.creatures.append(Creature.Creature("Giant"))
        self.bu01.creatures.append(Creature.Creature("Warbear"))
        self.bu01.creatures.append(Creature.Creature("Colossus"))
        self.rd01.move(6000, False, None, 5)
        self.bu01.move(6000, False, None, 5)
        game = self.game
        game._init_battle(self.bu01, self.rd01)
        defender = self.game.defender_legion
        centaur1 = defender.creatures[2]
        centaur1.move("D5")
        assert centaur1.find_target_hexlabels() == set()
        assert centaur1.engaged_enemies == set()
        ogre1 = defender.creatures[1]
        ogre1.move("F3")
        assert ogre1.find_target_hexlabels() == set()
        assert ogre1.engaged_enemies == set()
        gargoyle1 = defender.creatures[3]
        gargoyle1.move("E4")
        assert gargoyle1.find_target_hexlabels() == set()
        assert gargoyle1.engaged_enemies == set()
        titan1 = defender.creatures[0]
        titan1.move("E5")
        assert titan1.find_target_hexlabels() == set()
        assert titan1.engaged_enemies == set()
        troll1 = defender.creatures[4]
        troll1.legion = defender
        troll1.move("C5")
        assert troll1.find_target_hexlabels() == set()
        assert troll1.engaged_enemies == set()
        giant1 = defender.creatures[5]
        giant1.legion = defender
        giant1.move("D5")
        assert giant1.find_target_hexlabels() == set()
        assert giant1.engaged_enemies == set()

        game.done_with_maneuvers("p0")
        assert game.battle_phase == Phase.STRIKE
        assert gargoyle1.hits == 1
        assert centaur1.hits == 0
        assert titan1.hits == 0
        assert giant1.hits == 0
        assert troll1.hits == 0
        assert ogre1.hits == 0

        attacker = self.game.attacker_legion
        game.battle_active_legion = attacker
        game.battle_phase = Phase.MOVE
        ogre2 = attacker.creatures[1]
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        ogre2.move("A1")
        assert ogre2.find_target_hexlabels() == set()
        assert ogre2.engaged_enemies == set()
        centaur2 = attacker.creatures[2]
        centaur2.move("E2")
        assert centaur2.find_target_hexlabels() == set()
        assert centaur2.engaged_enemies == set()
        gargoyle2 = attacker.creatures[3]
        gargoyle2.move("C3")
        assert gargoyle2.find_target_hexlabels() == set()
        assert gargoyle2.engaged_enemies == set()
        titan2 = attacker.creatures[0]
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        titan2.move("B1")
        assert titan2.find_target_hexlabels() == set()
        assert titan2.engaged_enemies == set()
        warbear2 = attacker.creatures[4]
        warbear2.legion = attacker
        warbear2.move("D3")
        assert warbear2.find_target_hexlabels() == set()
        assert warbear2.engaged_enemies == set([])
        colossus2 = attacker.creatures[5]
        colossus2.legion = attacker
        colossus2.move("F2")
        assert colossus2.find_target_hexlabels() == set(["F3"])
        assert colossus2.engaged_enemies == set([ogre1])
        assert colossus2.number_of_dice(ogre1) == 10
        assert colossus2.strike_number(ogre1) == 2
        game.done_with_maneuvers("p1")
        assert gargoyle2.hits == 0
        assert centaur2.hits == 0
        assert ogre2.hits == 1
        assert titan2.hits == 0
        assert warbear2.hits == 0
        assert colossus2.hits == 0
        assert game.battle_phase == Phase.STRIKE

        game.battle_active_legion = defender
        game.battle_phase = Phase.COUNTERSTRIKE
        assert gargoyle1.engaged_enemies == set()
        assert giant1.engaged_enemies == set()
        assert giant1.find_target_hexlabels() == set()
        assert troll1.engaged_enemies == set()
        assert ogre1.engaged_enemies == set([colossus2])
        assert ogre1.number_of_dice(colossus2) == 6
        assert ogre1.strike_number(colossus2) == 6
        assert titan1.engaged_enemies == set()
