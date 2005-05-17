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
