import os

from slugathon.util import fileutils

__copyright__ = "Copyright (c) 2009-2011 David Ripton"
__license__ = "GNU GPL v2"


def test_basedir():
    assert fileutils.basedir().endswith("/slugathon")
    assert fileutils.basedir("images").endswith("/slugathon/images")
    assert fileutils.basedir("images/creature/titan").endswith(
        "/slugathon/images/creature/titan"
    )
    assert fileutils.basedir("images", "creature", "titan").endswith(
        "/slugathon/images/creature/titan"
    )


def test_basedir_MEIPASS2():
    exepath = "/src/Slugathon/dist/slugathon.exe"
    os.environ["_MEIPASS2"] = exepath
    assert fileutils.basedir("images").startswith(exepath)
