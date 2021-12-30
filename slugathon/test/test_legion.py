import logging
import time

import pytest

from slugathon.data import creaturedata
from slugathon.game import Caretaker, Creature, Game, Legion, Player

__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


def test_num_lords() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.num_lords == 2
    assert not legion.can_flee

    legion = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Titan", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    assert legion.num_lords == 1
    assert not legion.can_flee

    legion = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Gargoyle", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    assert legion.num_lords == 0
    assert legion.can_flee


def test_creature_names() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.creature_names == [
        "Angel",
        "Centaur",
        "Centaur",
        "Gargoyle",
        "Gargoyle",
        "Ogre",
        "Ogre",
        "Titan",
    ]


def test_remove_creature_by_name() -> None:
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
    with pytest.raises(ValueError):
        legion.remove_creature_by_name("Gargoyle")
    legion.remove_creature_by_name("Ogre")
    legion.remove_creature_by_name("Ogre")
    legion.remove_creature_by_name("Centaur")
    legion.remove_creature_by_name("Centaur")
    legion.remove_creature_by_name("Titan")
    assert len(legion) == 1
    assert legion
    legion.remove_creature_by_name("Angel")
    assert len(legion) == 0
    assert legion


def test_add_creature_by_name() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert len(legion) == 8
    with pytest.raises(ValueError):
        legion.add_creature_by_name("Cyclops")
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 7
    with pytest.raises(ValueError):
        legion.add_creature_by_name("Cyclops")
    assert "Gargoyle" in legion.creature_names
    legion.remove_creature_by_name("Gargoyle")
    assert len(legion) == 6
    assert "Gargoyle" not in legion.creature_names
    legion.add_creature_by_name("Troll")
    assert len(legion) == 7
    assert "Troll" in legion.creature_names


def test_is_legal_split() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)

    parent = Legion.Legion(player, "Rd01", creatures, 1)
    child1 = Legion.Legion(
        player, "Rd01", Creature.n2c(["Titan", "Gargoyle", "Ogre", "Ogre"]), 1
    )
    child2 = Legion.Legion(
        player,
        "Rd03",
        Creature.n2c(["Angel", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    assert parent.is_legal_split(child1, child2)
    assert not parent.is_legal_split(child1, child1)

    parent2 = Legion.Legion(
        player,
        "Rd01",
        Creature.n2c(["Titan", "Gargoyle", "Ogre", "Troll", "Centaur"]),
        1,
    )
    child3 = Legion.Legion(
        player, "Rd01", Creature.n2c(["Titan", "Gargoyle", "Ogre", "Troll"]), 1
    )
    child4 = Legion.Legion(player, "Rd03", Creature.n2c(["Centaur"]), 1)
    assert not parent2.is_legal_split(child3, child4)

    child5 = Legion.Legion(
        player,
        "Rd01",
        Creature.n2c(["Unknown", "Unknown", "Unknown", "Unknown"]),
        1,
    )
    child6 = Legion.Legion(
        player,
        "Rd03",
        Creature.n2c(["Unknown", "Unknown", "Unknown", "Unknown"]),
        1,
    )
    assert parent.is_legal_split(child5, child6)


def test_could_recruit() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Titan", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    caretaker = Caretaker.Caretaker()

    assert not legion.could_recruit("Marsh", caretaker)
    assert not legion.could_recruit("Desert", caretaker)
    assert legion.could_recruit("Plains", caretaker)
    assert legion.could_recruit("Brush", caretaker)
    assert legion.could_recruit("Tower", caretaker)


def test_available_recruits() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Titan", "Lion", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    caretaker = Caretaker.Caretaker()

    assert legion.available_recruits("Marsh", caretaker) == []
    assert legion.available_recruits("Desert", caretaker) == ["Lion"]
    assert legion.available_recruits("Plains", caretaker) == [
        "Centaur",
        "Lion",
    ]
    assert legion.available_recruits("Brush", caretaker) == ["Gargoyle"]
    assert legion.available_recruits("Tower", caretaker) == [
        "Ogre",
        "Centaur",
        "Gargoyle",
        "Warlock",
    ]


def test_available_recruits_and_recruiters() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(
        player,
        "Rd01",
        Creature.n2c(["Titan", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    caretaker = Caretaker.Caretaker()

    assert legion.available_recruits_and_recruiters("Marsh", caretaker) == []
    assert legion.available_recruits_and_recruiters("Desert", caretaker) == []
    assert legion.available_recruits_and_recruiters("Plains", caretaker) == [
        ("Centaur", "Centaur"),
        ("Lion", "Centaur", "Centaur"),
    ]
    assert legion.available_recruits_and_recruiters("Brush", caretaker) == [
        ("Gargoyle", "Gargoyle")
    ]
    assert legion.available_recruits_and_recruiters("Tower", caretaker) == [
        ("Ogre",),
        ("Centaur",),
        ("Gargoyle",),
        ("Warlock", "Titan"),
    ]

    caretaker.counts["Centaur"] = 0
    assert legion.available_recruits_and_recruiters("Plains", caretaker) == [
        ("Lion", "Centaur", "Centaur")
    ]

    legion2 = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Titan", "Gargoyle", "Gargoyle", "Gargoyle"]),
        1,
    )
    assert legion2.available_recruits_and_recruiters("Tower", caretaker) == [
        ("Ogre",),
        ("Gargoyle",),
        ("Warlock", "Titan"),
        ("Guardian", "Gargoyle", "Gargoyle", "Gargoyle"),
    ]
    assert legion2.available_recruits_and_recruiters("Brush", caretaker) == [
        ("Gargoyle", "Gargoyle"),
        ("Cyclops", "Gargoyle", "Gargoyle"),
    ]

    legion3 = Legion.Legion(player, "Rd03", Creature.n2c(["Colossus"]), 1)
    assert legion3.available_recruits_and_recruiters("Tundra", caretaker) == [
        ("Troll", "Colossus"),
        ("Warbear", "Colossus"),
        ("Giant", "Colossus"),
        ("Colossus", "Colossus"),
    ]
    assert legion3.available_recruits_and_recruiters(
        "Mountains", caretaker
    ) == [
        ("Lion", "Colossus"),
        ("Minotaur", "Colossus"),
        ("Dragon", "Colossus"),
        ("Colossus", "Colossus"),
    ]
    assert legion3.available_recruits_and_recruiters("Marsh", caretaker) == []

    legion4 = Legion.Legion(
        player,
        "Rd04",
        Creature.n2c(["Behemoth", "Cyclops", "Cyclops", "Cyclops"]),
        1,
    )
    assert legion4.available_recruits_and_recruiters("Brush", caretaker) == [
        ("Gargoyle", "Cyclops"),
        ("Cyclops", "Cyclops"),
        ("Gorgon", "Cyclops", "Cyclops"),
    ]
    logging.info(
        legion4.available_recruits_and_recruiters("Jungle", caretaker)
    )
    assert legion4.available_recruits_and_recruiters("Jungle", caretaker) == [
        ("Gargoyle", "Cyclops"),
        ("Gargoyle", "Behemoth"),
        ("Cyclops", "Cyclops"),
        ("Cyclops", "Behemoth"),
        ("Behemoth", "Cyclops", "Cyclops", "Cyclops"),
        ("Behemoth", "Behemoth"),
    ]


def test_score() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.score == 120


def test_sorted_creatures() -> None:
    creatures = Creature.n2c(
        [
            "Archangel",
            "Serpent",
            "Centaur",
            "Gargoyle",
            "Ogre",
            "Ranger",
            "Minotaur",
        ]
    )
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    li = legion.sorted_creatures
    assert len(li) == len(creatures) == len(legion)
    names = [creature.name for creature in li]
    assert names == [
        "Archangel",
        "Serpent",
        "Ranger",
        "Minotaur",
        "Gargoyle",
        "Centaur",
        "Ogre",
    ]


def test_any_summonable() -> None:
    creatures = Creature.n2c(
        [
            "Archangel",
            "Serpent",
            "Centaur",
            "Gargoyle",
            "Ogre",
            "Ranger",
            "Minotaur",
        ]
    )
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.any_summonable
    creatures = Creature.n2c(
        [
            "Angel",
            "Serpent",
            "Centaur",
            "Gargoyle",
            "Ogre",
            "Ranger",
            "Minotaur",
        ]
    )
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.any_summonable
    creatures = Creature.n2c(
        ["Serpent", "Centaur", "Gargoyle", "Ogre", "Ranger", "Minotaur"]
    )
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert not legion.any_summonable


def test_unknown() -> None:
    creatures = Creature.n2c(
        [
            "Archangel",
            "Serpent",
            "Centaur",
            "Gargoyle",
            "Ogre",
            "Ranger",
            "Minotaur",
        ]
    )
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert not legion.any_unknown
    assert legion.all_known
    assert not legion.all_unknown

    creatures = Creature.n2c(
        [
            "Archangel",
            "Serpent",
            "Centaur",
            "Gargoyle",
            "Ogre",
            "Ranger",
            "Unknown",
        ]
    )
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.any_unknown
    assert not legion.all_known
    assert not legion.all_unknown

    creatures = Creature.n2c(8 * ["Unknown"])
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.any_unknown
    assert not legion.all_known
    assert legion.all_unknown


def test_engaged() -> None:
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


def test_can_summon() -> None:
    now = time.time()
    game = Game.Game("g1", "p1", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player1 = Player.Player("p1", game, 0)
    player1.assign_color("Red")
    game.players.append(player1)
    legion1 = Legion.Legion(player1, "Rd01", creatures, 1)
    player1.markerid_to_legion[legion1.markerid] = legion1
    assert not legion1.can_summon

    player1.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Centaur", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Ogre", "Gargoyle"],
    )
    assert legion1.can_summon
    legion2 = player1.markerid_to_legion["Rd02"]
    legion2.move(2, False, None, 1)
    assert legion1.can_summon
    assert not legion2.can_summon


def test_find_picname() -> None:
    assert Legion.find_picname("Rd01") == "Cross"
    assert Legion.find_picname("Rd02") == "Eagle"
    assert Legion.find_picname("Gr12") == "Ourobouros"


def test_picname() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.picname == "Cross"

    legion = Legion.Legion(
        player,
        "Rd02",
        Creature.n2c(["Titan", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    assert legion.picname == "Eagle"

    legion = Legion.Legion(
        player,
        "Gr12",
        Creature.n2c(["Gargoyle", "Gargoyle", "Centaur", "Centaur"]),
        1,
    )
    assert legion.picname == "Ourobouros"


def test_reveal_creatures() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)

    legion = Legion.Legion(
        player,
        "Rd01",
        Creature.n2c(["Unknown", "Unknown", "Unknown", "Unknown"]),
        1,
    )
    legion.reveal_creatures(["Ogre"])
    assert legion.creature_names == ["Ogre", "Unknown", "Unknown", "Unknown"]
    legion.reveal_creatures(["Ogre", "Ogre"])
    assert legion.creature_names == ["Ogre", "Ogre", "Unknown", "Unknown"]
    legion.reveal_creatures(["Ogre", "Ogre", "Troll"])
    assert legion.creature_names == ["Ogre", "Ogre", "Troll", "Unknown"]
    legion.reveal_creatures(["Troll"])
    assert legion.creature_names == ["Ogre", "Ogre", "Troll", "Unknown"]
    legion.reveal_creatures(["Troll", "Troll"])
    assert legion.creature_names == ["Ogre", "Ogre", "Troll", "Troll"]
    legion.add_creature_by_name("Ranger")
    legion.reveal_creatures(["Troll", "Troll", "Ranger"])
    assert legion.creature_names == [
        "Ogre",
        "Ogre",
        "Ranger",
        "Troll",
        "Troll",
    ]

    legion = Legion.Legion(
        player,
        "Rd01",
        Creature.n2c(["Unknown", "Unknown", "Unknown", "Unknown"]),
        1,
    )
    legion.reveal_creatures(["Centaur", "Centaur", "Lion"])
    assert legion.creature_names == ["Centaur", "Centaur", "Lion", "Unknown"]


def test_combat_value() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)

    # Plains
    legion.hexlabel = 1
    assert legion.terrain_combat_value == legion.combat_value
    # Woods
    legion.hexlabel = 2
    assert legion.terrain_combat_value == legion.combat_value
    # Brush
    legion.hexlabel = 3
    assert legion.terrain_combat_value > legion.combat_value
    # Hills
    legion.hexlabel = 4
    assert legion.terrain_combat_value > legion.combat_value
    # Jungle
    legion.hexlabel = 5
    assert legion.terrain_combat_value > legion.combat_value
    # Desert
    legion.hexlabel = 7
    assert legion.terrain_combat_value == legion.combat_value
    # Marsh
    legion.hexlabel = 8
    assert legion.terrain_combat_value > legion.combat_value
    # Swamp
    legion.hexlabel = 14
    assert legion.terrain_combat_value > legion.combat_value
    # Tower
    legion.hexlabel = 100
    assert legion.terrain_combat_value > legion.combat_value
    # Mountains
    legion.hexlabel = 1000
    assert legion.terrain_combat_value == legion.combat_value
    # Tundra
    legion.hexlabel = 2000
    assert legion.terrain_combat_value == legion.combat_value


def test_find_creature() -> None:
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    player = Player.Player("p0", game, 0)
    legion = Legion.Legion(player, "Rd01", creatures, 1)
    assert legion.find_creature("Titan", "DEFENDER") is None
    for creature in legion.creatures:
        creature.hexlabel = "DEFENDER"
    assert legion.find_creature("Titan", "DEFENDER") is not None
    assert legion.find_creature("Ogre", "DEFENDER") is not None
    assert legion.find_creature("Titan", "ATTACKER") is None
    assert legion.find_creature("Ogre", "ATTACKER") is None
