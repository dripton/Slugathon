import guiutils

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
