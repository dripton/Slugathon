#!/usr/bin/env python2.3

import os
import sys
import unittest

files = os.listdir(os.curdir)
names = []
for file in files:
    if file[:4] == "test" and file[-3:] == ".py":
        names.append(file[:-3])

suite = unittest.defaultTestLoader.loadTestsFromNames(names)
runner = unittest.TextTestRunner(verbosity = 2)
result = runner.run(suite)

sys.exit(not result.wasSuccessful())
