#!/usr/bin/env python3

import datetime
import os
import subprocess
import sys
from distutils.command.install_data import install_data
from distutils.core import setup
from glob import glob

__copyright__ = "Copyright (c) 2009-2021 David Ripton"
__license__ = "GNU GPL v2"

VERSION = "0.1"


class install_data_twisted(install_data):

    """Make sure data files are installed in package.

    Yuck.  Taken from an old version of Twisted's setup.py.
    """

    def finalize_options(self):
        self.set_undefined_options(
            "install",
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
        commit = stdout.strip()
        if isinstance(commit, bytes):
            commit = commit.decode("utf-8")
        return commit
    else:
        return ""


def timestamp():
    """Return the current UTC time in YYYYMMDDhhmmss form."""
    utcnow = datetime.datetime.utcnow()
    return utcnow.strftime("%Y%m%d%H%M%S")


def write_version_file():
    """Dump a file containing the version, timestamp, and commit to
    docs/version.txt"""
    version = f"{VERSION}-{timestamp()}-{head_commit()[:7]}"
    # Need to use a relative path here because we may not have installed yet.
    with open("slugathon/docs/version.txt", "w") as fil:
        fil.write(f"{version}\n")


# cd to the location of the setup.py file so relative paths work.
os.chdir(os.path.dirname(os.path.realpath(__file__)))

write_version_file()

setup(
    name="slugathon",
    version=f"{VERSION}-{timestamp()}-{head_commit()[:7]}",
    description="Fantasy battle board game",
    author="David Ripton",
    author_email="d+slugathon@ripton.net",
    url="https://github.com/dripton/Slugathon/",
    download_url="https://github.com/dripton/Slugathon/zipball/master",
    license="GPLv2",
    packages=[
        "slugathon",
        "slugathon.ai",
        "slugathon.data",
        "slugathon.game",
        "slugathon.gui",
        "slugathon.net",
        "slugathon.util",
    ],
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
        "bin/set-all-slugathon-ai-passwords",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Framework :: Twisted",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    cmdclass={"install_data": install_data_twisted},
)
