#!/usr/bin/env python2.3

import unittest
import os
import time
from twisted.spread import pb
from twisted.internet import reactor
import Server
import Client



class ServerTestCase(unittest.TestCase):
    def setUp(self):
        # Need to run the server in another process
        os.system("python2.3 Server.py &")
        # Give the OS a second to start it before we use it.
        time.sleep(1)

    def test_startup(self):
        self.client = Client.Client(username='unittest', password='unittest')
        self.client.connect().addCallbacks(self.connected, self.failure)
        reactor.run()

    def connected(self, perspective):
        print "connected", self, perspective
        perspective.callRemote('getName', 'foo').addCallbacks(self.success,
          self.failure)

    def success(self, name):
        assert name == "unittest"
        reactor.stop()

    def failure(self, error):
        print error
        reactor.stop()
        self.fail()

    def tearDown(self):
        os.system('pkill -f "python.*Server.py"')


if __name__ == '__main__':
    unittest.main()
