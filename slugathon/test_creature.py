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
