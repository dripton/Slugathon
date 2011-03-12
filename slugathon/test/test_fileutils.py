__copyright__ = "Copyright (c) 2009-2011 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.util import fileutils


def test_basedir():
    assert fileutils.basedir().endswith("/slugathon")
    assert fileutils.basedir("images").endswith("/slugathon/images")
    assert fileutils.basedir("images/creature/titan").endswith(
      "/slugathon/images/creature/titan")
    assert fileutils.basedir("images", "creature", "titan").endswith(
      "/slugathon/images/creature/titan")
