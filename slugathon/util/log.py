__copyright__ = "Copyright (c) 2010 David Ripton"
__license__ = "GNU GPL v2"


"""Debug logging."""


import inspect
import time
import os


def log(*args):
    tup = inspect.stack()[1]
    path = tup[1]
    fn = os.path.split(path)[-1]
    line = tup[2]
    print time.time(), fn, line,
    for arg in args:
        print arg,
    print
