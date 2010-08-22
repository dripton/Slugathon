__copyright__ = "Copyright (c) 2009-2010 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.util import guiutils


def test_rectangles_intersect():
    ri = guiutils.rectangles_intersect
    rect1 = (0, 0, 0, 0)
    rect2 = (0, 0, 1, 1)
    rect3 = (1, 1, 0, 0)
    rect4 = (1, 1, 1, 1)
    rect5 = (0.5, 0.5, 0, 0)
    assert ri(rect1, rect2)
    assert not ri(rect1, rect3)
    assert not ri(rect1, rect4)
    assert not ri(rect1, rect5)
    assert ri(rect2, rect3)
    assert ri(rect2, rect4)
    assert ri(rect2, rect5)
    assert ri(rect3, rect4)
    assert not ri(rect3, rect5)
    assert not ri(rect4, rect5)

def test_combine_rectangles():
    cr = guiutils.combine_rectangles
    rect1 = (0, 0, 0, 0)
    rect2 = (0, 0, 1, 1)
    rect3 = (1, 1, 0, 0)
    rect4 = (1, 1, 1, 1)
    rect5 = (0.5, 0.5, 0, 0)
    assert cr(rect1, rect1) == rect1
    assert cr(rect1, rect2) == rect2
    assert cr(rect1, rect3) == (0, 0, 1, 1)
    assert cr(rect1, rect4) == (0, 0, 2, 2)
    assert cr(rect1, rect5) == (0, 0, 0.5, 0.5)
    assert cr(rect2, rect2) == rect2
    assert cr(rect2, rect3) == (0, 0, 1, 1)
    assert cr(rect2, rect4) == (0, 0, 2, 2)
    assert cr(rect2, rect5) == (0, 0, 1, 1)
    assert cr(rect3, rect4) == rect4
    assert cr(rect3, rect5) == (0.5, 0.5, 0.5, 0.5)
    assert cr(rect4, rect5) == (0.5, 0.5, 1.5, 1.5)

def test_basedir():
    assert guiutils.basedir().endswith("/slugathon")
    assert guiutils.basedir("images").endswith("/slugathon/images")
    assert guiutils.basedir("images/creature/titan").endswith(
      "/slugathon/images/creature/titan")
    assert guiutils.basedir("images", "creature", "titan").endswith(
      "/slugathon/images/creature/titan")

def test_point_in_polygon():
    pip = guiutils.point_in_polygon
    v3 = [(0, 0), (10, 10), (-10, 10)]
    assert pip((0, 1), v3)
    assert pip((5, 7), v3)
    assert not pip((0, -1), v3)
    assert not pip((5, 1), v3)

    v4 = [(0, 0), (5, 0), (5, 10), (0, 10)]
    assert not pip((0, 0), v4)
    assert not pip((5, 0), v4)
    assert not pip((5, 10), v4)
    assert not pip((0, 10), v4)
    assert not pip((0, 1), v4)
    assert pip((0.001, 0.001), v4)
