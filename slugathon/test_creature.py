#!/usr/bin/env python2.3

import unittest
import Creature

class CreatureTestCase(unittest.TestCase):

    def testNonExistentCreature(self):
        try:
            creature = Creature.Creature('Jackalope')
        except KeyError:
            pass
        else:
            fail("Should have raised")

    def testInit(self):
        creature = Creature.Creature('Ogre')
        assert creature.name == 'Ogre'
        assert creature.pluralName == 'Ogres'
        assert creature.power == 6
        assert creature.skill == 2
        assert not creature.flies
        assert not creature.rangestrikes
        assert creature.characterType == 'creature'
        assert not creature.summonable
        assert not creature.acquirable
        assert creature.maxCount == 25
        assert creature.colorName == 'ogreRed'


if __name__ == '__main__':
    unittest.main()
