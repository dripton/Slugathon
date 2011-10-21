__copyright__ = "Copyright (c) 2009-2011 David Ripton"
__license__ = "GNU GPL v2"


import os


def basedir(*args):
    """Return an absolute path based on the base slugathon package directory
    and the passed paths."""
    parts = [os.path.dirname(__file__), ".."]
    if args:
        parts.extend(args)
    return os.path.abspath(os.path.join(*parts))
