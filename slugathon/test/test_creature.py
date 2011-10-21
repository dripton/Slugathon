__copyright__ = "Copyright (c) 2003-2009 David Ripton"
__license__ = "GNU GPL v2"


import time

from slugathon.game import Creature, Game, Player


def test_non_existent_creature():
    try:
        Creature.Creature("Jackalope")
    except KeyError:
        pass
    else:
        assert False, "Should have raised"


def test_init():
    creature = Creature.Creature("Ogre")
    assert creature.name == "Ogre"
    assert creature.plural_name == "Ogres"
    assert creature.power == 6
    assert creature.skill == 2
    assert not creature.flies
    assert not creature.rangestrikes
    assert not creature.magicmissile
    assert creature.character_type == "creature"
    assert not creature.summonable
    assert not creature.acquirable
    assert creature.max_count == 25
    assert creature.color_name == "ogre_red"


def test_score():
    creature = Creature.Creature("Ogre")
    assert creature.score == 12
    creature = Creature.Creature("Colossus")
    assert creature.score == 40


def test_native():
    ogre = Creature.Creature("Ogre")
    assert ogre.is_native("Bog")
    assert ogre.is_native("Slope")
    assert ogre.is_native("Plain")
    assert ogre.is_native("Tree")
    assert ogre.is_native("Tower")
    assert not ogre.is_native("Bramble")
    assert not ogre.is_native("Volcano")
    assert not ogre.is_native("Sand")
    assert not ogre.is_native("Dune")
    assert not ogre.is_native("Cliff")

    cyclops = Creature.Creature("Cyclops")
    assert cyclops.is_native("Bramble")
    assert not cyclops.is_native("Bog")

    warlock = Creature.Creature("Warlock")
    assert warlock.is_native("Wall")
    assert not warlock.is_native("Bog")

    titan = Creature.Creature("Titan")
    assert not titan.is_native("Wall")
    assert not titan.is_native("Tower")
    assert not titan.is_native("Bog")
    assert not titan.is_native("Bramble")

    lion = Creature.Creature("Lion")
    assert not lion.is_native("Bog")
    assert lion.is_native("Slope")
    assert lion.is_native("Plain")
    assert not lion.is_native("Tree")
    assert not lion.is_native("Tower")
    assert not lion.is_native("Bramble")
    assert lion.is_native("Sand")
    assert lion.is_native("Dune")
    assert lion.is_native("Cliff")
    assert not lion.is_native("Volcano")

    dragon = Creature.Creature("Dragon")
    assert not dragon.is_native("Bog")
    assert dragon.is_native("Slope")
    assert dragon.is_native("Plain")
    assert not dragon.is_native("Tree")
    assert not dragon.is_native("Tower")
    assert not dragon.is_native("Bramble")
    assert not dragon.is_native("Sand")
    assert not dragon.is_native("Dune")
    assert dragon.is_native("Cliff")
    assert dragon.is_native("Volcano")

    unicorn = Creature.Creature("Unicorn")
    assert unicorn.is_native("Slope")


def test_titan_power():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markernames) == 12
    player.pick_marker("Rd01")
    assert player.selected_markername == "Rd01"
    player.create_starting_legion()
    legion = player.legions["Rd01"]
    for creature in legion.creatures:
        if creature.name == "Titan":
            titan = creature
    assert player.score == 0
    assert titan.power == 6
    player.score = 99
    assert titan.power == 6
    player.score = 100
    assert titan.power == 7
    player.score = 10000
    assert titan.power == 106
