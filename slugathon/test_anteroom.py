#!/usr/bin/env python

import os
import time
import unittest
import Anteroom
import Server
import Client


class AnteroomTestCase(unittest.TestCase):
    def setUp(self):
        os.system("python Server.py &")
        time.sleep(1)

    def testInit(self):
        self.client = Client.Client("unittest", "unittest")
        def1 = self.client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def connected(self):
        anteroom = self.client.anteroom
        assert isinstance(anteroom, Anteroom.Anteroom)
        while 1:
            gtk.main_iteration()

    def failure(self):
        self.fail()

    def tearDown(self):
        os.system('pkill -f "python.*Server.py"')


if __name__ == "__main__":
    unittest.main()
