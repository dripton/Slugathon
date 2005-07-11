import Legion
import Player
import Creature
import creaturedata

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
        raise "should have raised"

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

