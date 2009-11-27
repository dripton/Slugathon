#!/usr/bin/env python

from glob import glob
from distutils.core import setup
from distutils.command.install_data import install_data
import subprocess
import datetime


VERSION = "0.1a1"

class install_data_twisted(install_data):
    """Make sure data files are installed in package.

    Yuck.  Taken from an old version of Twisted's setup.py.
    """
    def finalize_options(self):
        self.set_undefined_options("install",
            ("install_lib", "install_dir")
        )
        install_data.finalize_options(self)

def head_commit():
    """Return the current commit of HEAD, or "" on failure."""
    cmd = ["git", "rev-list", "--max-count=1", "HEAD"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, unused = proc.communicate()
    if proc.returncode != 0:
        return ""
    if stdout:
        return stdout.strip()
    else:
        return ""

def timestamp():
    """Return the current UTC time in YYYYMMDDhhmmss form."""
    utcnow = datetime.datetime.utcnow()
    return utcnow.strftime("%Y%m%d%H%M%S")

def write_version_file():
    """Dump a file containing the version, timestamp, and commit to
    docs/version.txt"""
    version = "%s-%s-%s" % (VERSION, timestamp(), head_commit()[:7])
    # Need to use a relative path here because we may not have installed yet.
    fil = open("slugathon/docs/version.txt", "w")
    fil.write("%s\n" % version)
    fil.close()

write_version_file()

setup(
    name = "slugathon",
    version = "%s-%s-%s" % (VERSION, timestamp(), head_commit()[:7]),
    description = "board game",
    author = "David Ripton",
    author_email = "d+slugathon@ripton.net",
    url = "http://github.com/dripton/Slugathon/",
    download_url = "TODO",
    license = "GPLv2",
    packages = ["slugathon", "slugathon.data", "slugathon.game",
      "slugathon.gui", "slugathon.net", "slugathon.util"],
    data_files = [
        ("slugathon/images/battlehex", glob("slugathon/images/battlehex/*")),
        ("slugathon/images/creature", glob("slugathon/images/creature/*")),
        ("slugathon/images/dice", glob("slugathon/images/dice/*")),
        ("slugathon/images/legion", glob("slugathon/images/legion/*")),
        ("slugathon/images/masterhex", glob("slugathon/images/masterhex/*")),
        ("slugathon/ui", glob("slugathon/ui/*")),
        ("slugathon/config", glob("slugathon/config/*")),
        ("slugathon/docs", glob("slugathon/docs/*")),
    ],
    scripts = ["bin/slugathon-server", "bin/slugathon-client"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    cmdclass = {"install_data": install_data_twisted},
)
