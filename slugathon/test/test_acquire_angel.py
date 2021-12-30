from slugathon.game import Creature
from slugathon.gui import AcquireAngels

__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"


def test_find_angel_combos() -> None:
    fac = AcquireAngels.find_angel_combos
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
