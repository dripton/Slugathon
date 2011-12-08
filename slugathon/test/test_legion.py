__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"


import time

from slugathon.game import Legion, Player, Creature, Game, Caretaker
from slugathon.data import creaturedata
from slugathon.util.log import log


def test_num_lords():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.num_lords == 2
    assert not legion.can_flee

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.num_lords == 1
    assert not legion.can_flee

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Gargoyle",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.num_lords == 0
    assert legion.can_flee


def test_creature_names():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.creature_names == ["Angel", "Centaur", "Centaur",
      "Gargoyle", "Gargoyle", "Ogre", "Ogre", "Titan"]


def test_remove_creature_by_name():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert len(legion) == 8
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 7
    assert "Gargoyle" in legion.creature_names
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 6
    assert "Gargoyle" not in legion.creature_names
    try:
        legion.remove_creature_by_name("Gargoyle")
    except ValueError:
        pass
    else:
        raise AssertionError("should have raised")


def test_add_creature_by_name():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert len(legion) == 8
    try:
        legion.add_creature_by_name("Cyclops")
    except ValueError:
        pass
    else:
        raise AssertionError("should have raised")
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 7
    try:
        legion.add_creature_by_name("Cyclops")
    except ValueError:
        pass
    else:
        raise AssertionError("should have raised")
    assert "Gargoyle" in legion.creature_names
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 6
    assert "Gargoyle" not in legion.creature_names
    legion.add_creature_by_name("Troll")
    assert len(legion) == 7
    assert "Troll" in legion.creature_names


def test_is_legal_split():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)

    parent = Legion.Legion(player, "Rd01", creatures, 1)
    child1 = Legion.Legion(player, "Rd01", Creature.n2c(["Titan",
      "Gargoyle", "Ogre", "Ogre"]), 1)
    child2 = Legion.Legion(player, "Rd03", Creature.n2c(["Angel",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert parent.is_legal_split(child1, child2)
    assert not parent.is_legal_split(child1, child1)

    parent2 = Legion.Legion(player, "Rd01", Creature.n2c(["Titan",
      "Gargoyle", "Ogre", "Troll", "Centaur"]), 1)
    child3 = Legion.Legion(player, "Rd01", Creature.n2c(["Titan",
      "Gargoyle", "Ogre", "Troll"]), 1)
    child4 = Legion.Legion(player, "Rd03", Creature.n2c(["Centaur"]), 1)
    assert not parent2.is_legal_split(child3, child4)

    child5 = Legion.Legion(player, "Rd01", Creature.n2c(["Unknown",
      "Unknown", "Unknown", "Unknown"]), 1)
    child6 = Legion.Legion(player, "Rd03", Creature.n2c(["Unknown",
      "Unknown", "Unknown", "Unknown"]), 1)
    assert parent.is_legal_split(child5, child6)


def test_could_recruit():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    caretaker = Caretaker.Caretaker()

    assert not legion.could_recruit("Marsh", caretaker)
    assert not legion.could_recruit("Desert", caretaker)
    assert legion.could_recruit("Plains", caretaker)
    assert legion.could_recruit("Brush", caretaker)
    assert legion.could_recruit("Tower", caretaker)


def test_available_recruits():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan", "Lion",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    caretaker = Caretaker.Caretaker()

    assert legion.available_recruits("Marsh", caretaker) == []
    assert legion.available_recruits("Desert", caretaker) == ["Lion"]
    assert legion.available_recruits("Plains", caretaker) == ["Centaur",
      "Lion"]
    assert legion.available_recruits("Brush", caretaker) == ["Gargoyle"]
    assert legion.available_recruits("Tower", caretaker) == ["Ogre",
      "Centaur", "Gargoyle", "Warlock"]


def test_available_recruits_and_recruiters():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(player, "Rd01", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    caretaker = Caretaker.Caretaker()

    assert legion.available_recruits_and_recruiters("Marsh", caretaker) == []
    assert legion.available_recruits_and_recruiters("Desert", caretaker) == []
    assert legion.available_recruits_and_recruiters("Plains", caretaker) == [
      ("Centaur", "Centaur"), ("Lion", "Centaur", "Centaur")]
    assert legion.available_recruits_and_recruiters("Brush", caretaker) == [
      ("Gargoyle", "Gargoyle")]
    assert legion.available_recruits_and_recruiters("Tower", caretaker) == [
      ("Ogre",), ("Centaur",), ("Gargoyle",), ("Warlock", "Titan")]

    caretaker.counts["Centaur"] = 0
    assert legion.available_recruits_and_recruiters("Plains", caretaker) == [
      ("Lion", "Centaur", "Centaur")]

    legion2 = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Gargoyle", "Gargoyle"]), 1)
    assert legion2.available_recruits_and_recruiters("Tower", caretaker) == [
      ("Ogre",), ("Gargoyle",), ("Warlock", "Titan"),
      ("Guardian", "Gargoyle", "Gargoyle", "Gargoyle")]
    assert legion2.available_recruits_and_recruiters("Brush", caretaker) == [
      ("Gargoyle", "Gargoyle"), ("Cyclops", "Gargoyle", "Gargoyle")]

    legion3 = Legion.Legion(player, "Rd03", Creature.n2c(["Colossus"]), 1)
    assert legion3.available_recruits_and_recruiters("Tundra", caretaker) == [
      ("Troll", "Colossus"), ("Warbear", "Colossus"), ("Giant", "Colossus"),
      ("Colossus", "Colossus")]
    assert legion3.available_recruits_and_recruiters("Mountains",
      caretaker) == [("Lion", "Colossus"), ("Minotaur", "Colossus"),
      ("Dragon", "Colossus"), ("Colossus", "Colossus")]
    assert legion3.available_recruits_and_recruiters("Marsh", caretaker) == []

    legion4 = Legion.Legion(player, "Rd04", Creature.n2c(["Behemoth",
      "Cyclops", "Cyclops", "Cyclops"]), 1)
    assert legion4.available_recruits_and_recruiters("Brush", caretaker) == [
      ("Gargoyle", "Cyclops"), ("Cyclops", "Cyclops"),
      ("Gorgon", "Cyclops", "Cyclops")]
    log(legion4.available_recruits_and_recruiters("Jungle", caretaker))
    assert legion4.available_recruits_and_recruiters("Jungle", caretaker) == [
      ("Gargoyle", "Cyclops"), ("Gargoyle", "Behemoth"),
      ("Cyclops", "Cyclops"), ("Cyclops", "Behemoth"), ("Behemoth", "Cyclops",
      "Cyclops", "Cyclops"), ("Behemoth", "Behemoth"),
    ]


def test_score():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.score == 120


def test_sorted_creatures():
    creatures = Creature.n2c(["Archangel", "Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Minotaur"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    li = legion.sorted_creatures
    assert len(li) == len(creatures) == len(legion)
    names = [creature.name for creature in li]
    assert names == ["Archangel", "Serpent", "Ranger", "Minotaur",
      "Gargoyle", "Centaur", "Ogre"]


def test_any_summonable():
    creatures = Creature.n2c(["Archangel", "Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Minotaur"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert legion.any_summonable
    creatures = Creature.n2c(["Angel", "Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Minotaur"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert legion.any_summonable
    creatures = Creature.n2c(["Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Minotaur"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert not legion.any_summonable


def test_unknown():
    creatures = Creature.n2c(["Archangel", "Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Minotaur"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert not legion.any_unknown
    assert not legion.all_unknown

    creatures = Creature.n2c(["Archangel", "Serpent", "Centaur", "Gargoyle",
      "Ogre", "Ranger", "Unknown"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert legion.any_unknown
    assert not legion.all_unknown

    creatures = Creature.n2c(8 * ["Unknown"])
    legion = Legion.Legion(None, "Rd01", creatures, 1)
    assert legion.any_unknown
    assert legion.all_unknown


def test_engaged():
    now = time.time()
    game = Game.Game("g1", "p1", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player1 = Player.Player("p1", game, 0)
    player1.color = "Red"
    game.players.append(player1)
    legion1 = Legion.Legion(player1, "Rd01", creatures, 1)
    player1.markerid_to_legion[legion1.markerid] = legion1

    player2 = Player.Player("p2", game, 1)
    player2.color = "Blue"
    game.players.append(player2)
    legion2 = Legion.Legion(player2, "Bu01", creatures, 2)
    player2.markerid_to_legion[legion2.markerid] = legion2
    assert not legion1.engaged
    assert not legion2.engaged

    legion2.move(1, False, None, 1)
    assert legion1.engaged
    assert legion2.engaged


def test_can_summon():
    now = time.time()
    game = Game.Game("g1", "p1", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player1 = Player.Player("p1", game, 0)
    player1.assign_color("Red")
    game.players.append(player1)
    legion1 = Legion.Legion(player1, "Rd01", creatures, 1)
    player1.markerid_to_legion[legion1.markerid] = legion1
    assert not legion1.can_summon

    player1.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    assert legion1.can_summon
    legion2 = player1.markerid_to_legion["Rd02"]
    legion2.move(2, False, None, 1)
    assert legion1.can_summon
    assert not legion2.can_summon


def test_find_picname():
    assert Legion.find_picname("Rd01") == "Cross"
    assert Legion.find_picname("Rd02") == "Eagle"
    assert Legion.find_picname("Gr12") == "Ourobouros"


def test_picname():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.picname == "Cross"

    legion = Legion.Legion(player, "Rd02", Creature.n2c(["Titan",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.picname == "Eagle"

    legion = Legion.Legion(player, "Gr12", Creature.n2c(["Gargoyle",
      "Gargoyle", "Centaur", "Centaur"]), 1)
    assert legion.picname == "Ourobouros"
