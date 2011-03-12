__copyright__ = "Copyright (c) 2009-2011 David Ripton"
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

def test_point_in_polygon1():
    pip = guiutils.point_in_polygon
    v3 = [(0, 0), (6, 0), (0, 6)]
    assert pip((1, 1), v3)
    assert pip((2, 1), v3)
    assert pip((3, 1), v3)
    assert pip((4, 1), v3)
    assert not pip((6, 1), v3)
    assert pip((1, 2), v3)
    assert pip((2, 2), v3)
    assert pip((3, 2), v3)
    assert not pip((5, 2), v3)
    assert not pip((6, 2), v3)
    assert pip((1, 3), v3)
    assert pip((2, 3), v3)
    assert not pip((4, 3), v3)
    assert not pip((5, 3), v3)
    assert not pip((6, 3), v3)
    assert pip((1, 4), v3)
    assert not pip((3, 4), v3)
    assert not pip((4, 4), v3)
    assert not pip((5, 4), v3)
    assert not pip((6, 4), v3)
    assert not pip((2, 5), v3)
    assert not pip((3, 5), v3)
    assert not pip((4, 5), v3)
    assert not pip((5, 5), v3)
    assert not pip((6, 5), v3)

def test_point_in_polygon2():
    pip = guiutils.point_in_polygon
    v4 = [(0, 0), (5, 0), (5, 10), (0, 10)]
    assert not pip((5, 0), v4)
    assert not pip((5, 10), v4)
    assert not pip((0, 10), v4)
    assert pip((0.001, 0.001), v4)

def test_point_in_polygon3():
    pip = guiutils.point_in_polygon
    v6 = [(1, 3), (4, 3), (5, 0), (4, -3), (1, -3), (0, 0)]
    assert pip((4, 0), v6)
    assert pip((3, 1), v6)
