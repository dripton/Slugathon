#!/usr/bin/env python2.3

import unittest
import Creature

class CreatureTestCase(unittest.TestCase):

    def test_non_existent_creature(self):
        try:
            creature = Creature.Creature('Jackalope')
        except KeyError:
            pass
        else:
            fail("Should have raised")

    def test_init(self):
        creature = Creature.Creature('Ogre')
        assert creature.name == 'Ogre'
        assert creature.plural_name == 'Ogres'
        assert creature.power == 6
        assert creature.skill == 2
        assert not creature.flies
        assert not creature.rangestrikes
        assert creature.characterType == 'creature'
        assert not creature.summonable
        assert not creature.acquirable
        assert creature.max_count == 25
        assert creature.color_name == 'ogreRed'


if __name__ == '__main__':
    unittest.main()
