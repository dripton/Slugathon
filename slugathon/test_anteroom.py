#!/usr/bin/env python2.3

import unittest
import Anteroom


class AnteroomTestCase(unittest.TestCase):
    def testInit(self):
        anteroom = Anteroom.Anteroom()
        print dir(anteroom)


if __name__ == '__main__':
    unittest.main()
