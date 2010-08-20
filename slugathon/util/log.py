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
    now = time.time()
    fract = now - int(now)
    sfract = ("%.2f" % fract)[1:]
    local = time.localtime(now)
    print time.strftime("%H:%M:%S", local) + sfract, fn, line,
    for arg in args:
        print arg,
    print
