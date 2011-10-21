__copyright__ = "Copyright (c) 2010 David Ripton"
__license__ = "GNU GPL v2"


"""Debug logging."""


import inspect
import time
import os
import sys


outstreams = [sys.stdout]


def log_to_path(path):
    """Create a logfile at path, and log only to it from now on."""
    fil = open(path, "w")
    global outstreams
    outstreams = [fil]


def tee_to_path(path):
    """Create a logfile at path, and also log to it from now on."""
    fil = open(path, "w")
    outstreams.append(fil)


def log(*args):
    tup = inspect.stack()[1]
    path = tup[1]
    fn = os.path.split(path)[-1]
    line = tup[2]
    now = time.time()
    fract = now - int(now)
    sfract = ("%.2f" % fract)[1:]
    local = time.localtime(now)
    for out in outstreams:
        print >> out, time.strftime("%H:%M:%S", local) + sfract, fn, line,
        for arg in args:
            print >> out, arg,
        print >> out
        out.flush()
