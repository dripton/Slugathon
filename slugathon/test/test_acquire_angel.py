__copyright__ = "Copyright (c) 2010 David Ripton"
__license__ = "GNU GPL v2"


import time

from slugathon.gui import AcquireAngel
from slugathon.game import Creature


def test_find_angel_combos():
    fac = AcquireAngel.find_angel_combos
    C = Creature.Creature

    assert fac(0, 1, 6, 12) == [(C("Angel"),)]

    assert fac(1, 1, 6, 12) == [
      (C("Archangel"), C("Angel")),
      (C("Angel"), C("Angel")),
      (C("Archangel"),),
      (C("Angel"),),
    ]

    assert fac(0, 2, 6, 12) == [
      (C("Angel"), C("Angel")),
      (C("Angel"),),
    ]

    assert fac(1, 2, 6, 12) == [
      (C("Archangel"), C("Angel"), C("Angel")),
      (C("Angel"), C("Angel"), C("Angel")),
      (C("Archangel"), C("Angel")),
      (C("Angel"), C("Angel")),
      (C("Archangel"),),
      (C("Angel"),),
    ]

    assert fac(0, 1, 6, 0) == []

    assert fac(1, 2, 0, 12) == [
      (C("Angel"), C("Angel"), C("Angel")),
      (C("Angel"), C("Angel")),
      (C("Angel"),),
    ]
