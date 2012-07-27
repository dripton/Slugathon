#!/usr/bin/env python

__copyright__ = "Copyright (c) 2009-2012 David Ripton"
__license__ = "GNU GPL v2"


from glob import glob
from distutils.core import setup
from distutils.command.install_data import install_data
import subprocess
import datetime
import sys
import os


VERSION = "0.1"


class install_data_twisted(install_data):
    """Make sure data files are installed in package.

    Yuck.  Taken from an old version of Twisted's setup.py.
    """
    def finalize_options(self):
        self.set_undefined_options("install",
            ("install_lib", "install_dir"),
        )
        install_data.finalize_options(self)


def head_commit():
    """Return the current commit of HEAD, or "" on failure."""
    if sys.platform == "win32":
        GIT = "git.exe"
    else:
        GIT = "git"
    cmd = [GIT, "rev-list", "--max-count=1", "HEAD"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, unused = proc.communicate()
    except Exception:
        return ""
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
    with open("slugathon/docs/version.txt", "w") as fil:
        fil.write("%s\n" % version)


# cd to the location of the setup.py file so relative paths work.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

write_version_file()

setup(
    name="slugathon",
    version="%s-%s-%s" % (VERSION, timestamp(), head_commit()[:7]),
    description="Fantasy battle board game",
    author="David Ripton",
    author_email="d+slugathon@ripton.net",
    url="https://github.com/dripton/Slugathon/",
    download_url="https://github.com/dripton/Slugathon/zipball/master",
    license="GPLv2",
    packages=["slugathon", "slugathon.ai", "slugathon.data",
      "slugathon.game", "slugathon.gui", "slugathon.net", "slugathon.util"],
    data_files=[
        ("slugathon/images/battlehex", glob("slugathon/images/battlehex/*")),
        ("slugathon/images/creature", glob("slugathon/images/creature/*")),
        ("slugathon/images/dice", glob("slugathon/images/dice/*")),
        ("slugathon/images/legion", glob("slugathon/images/legion/*")),
        ("slugathon/images/masterhex", glob("slugathon/images/masterhex/*")),
        ("slugathon/config", glob("slugathon/config/*")),
        ("slugathon/docs", glob("slugathon/docs/*")),
    ],
    scripts=[
        "bin/slugathon",
        "bin/stresstest-slugathon",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Framework :: Twisted",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    cmdclass={"install_data": install_data_twisted},
)
