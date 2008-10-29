import py

import Creature

def test_non_existent_creature():
    try:
        Creature.Creature("Jackalope")
    except KeyError:
        pass
    else:
        py.test.fail("Should have raised")

def test_init():
    creature = Creature.Creature("Ogre")
    assert creature.name == "Ogre"
    assert creature.plural_name == "Ogres"
    assert creature.power == 6
    assert creature.skill == 2
    assert not creature.flies
    assert not creature.rangestrikes
    assert creature.character_type == "creature"
    assert not creature.summonable
    assert not creature.acquirable
    assert creature.max_count == 25
    assert creature.color_name == "ogre_red"

def test_score():
    creature = Creature.Creature("Ogre")
    assert creature.score() == 12
    creature = Creature.Creature("Colossus")
    assert creature.score() == 40

def test_native():
    ogre = Creature.Creature("Ogre")
    assert ogre.is_native("Bog")
    assert ogre.is_native("Slope")
    assert ogre.is_native("Plains")
    assert ogre.is_native("Tree")
    assert ogre.is_native("Tower")
    assert not ogre.is_native("Bramble")
    assert not ogre.is_native("Volcano")
    assert not ogre.is_native("Sane")
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
