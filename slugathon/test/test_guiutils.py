__copyright__ = "Copyright (c) 2009 David Ripton"
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

def test_basedir():
    assert guiutils.basedir() == "/usr/lib/python2.6/site-packages/slugathon"
    assert guiutils.basedir("images") == \
      "/usr/lib/python2.6/site-packages/slugathon/images"
    assert guiutils.basedir("images/creature/titan") == \
      "/usr/lib/python2.6/site-packages/slugathon/images/creature/titan"
    assert guiutils.basedir("images", "creature", "titan") == \
      "/usr/lib/python2.6/site-packages/slugathon/images/creature/titan"
