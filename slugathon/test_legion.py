import time

import Legion
import Player
import Creature
import creaturedata
import Game
import Caretaker

def test_num_lords():
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("test", "Game1", 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.num_lords() == 2

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.num_lords() == 1

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Gargoyle",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.num_lords() == 0

def test_creature_names():
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("test", "Game1", 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.creature_names() == ["Angel", "Centaur", "Centaur",
      "Gargoyle", "Gargoyle", "Ogre", "Ogre", "Titan"]

def test_remove_creature_by_name():
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("test", "Game1", 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert len(legion) == 8
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 7
    assert "Gargoyle" in legion.creature_names()
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 6
    assert "Gargoyle" not in legion.creature_names()
    try:
        legion.remove_creature_by_name("Gargoyle")
    except ValueError:
        pass
    else:
        raise AssertionError, "should have raised"

def test_add_creature_by_name():
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("test", "Game1", 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert len(legion) == 8
    try:
        legion.add_creature_by_name("Cyclops")
    except ValueError:
        pass
    else:
        raise AssertionError, "should have raised"
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 7
    try:
        legion.add_creature_by_name("Cyclops")
    except ValueError:
        pass
    else:
        raise AssertionError, "should have raised"
    assert "Gargoyle" in legion.creature_names()
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 6
    assert "Gargoyle" not in legion.creature_names()
    legion.add_creature_by_name("Troll")
    assert len(legion) == 7
    assert "Troll" in legion.creature_names()

def test_is_legal_split():
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("test", "Game1", 0)

    parent = Legion.Legion(player, "Rd01", creatures, 1)
    child1 = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Ogre", "Ogre"]), 1)
    child2 = Legion.Legion(player, "Rd03", Creature.n2c(["Angel",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert parent.is_legal_split(child1, child2)

    assert not parent.is_legal_split(child1, child1)

def test_available_recruits():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", "g1", 0)
    board = game.board

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    caretaker = Caretaker.Caretaker()

    masterhex = board.hexes[140] # Marsh
    assert legion.available_recruits(masterhex, caretaker) == []
    masterhex = board.hexes[139] # Desert
    assert legion.available_recruits(masterhex, caretaker) == []
    masterhex = board.hexes[138] # Plains
    assert legion.available_recruits(masterhex, caretaker) == ["Centaur",
      "Lion"]
    masterhex = board.hexes[137] # Brush
    assert legion.available_recruits(masterhex, caretaker) == ["Gargoyle"]
    masterhex = board.hexes[600] # Tower
    assert legion.available_recruits(masterhex, caretaker) == ["Centaur",
      "Gargoyle", "Ogre", "Warlock"]

