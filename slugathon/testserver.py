#!/usr/bin/env python2.3

import unittest
import os
import Server
from twisted.spread import pb
from twisted.internet import reactor



class ServerTestCase(unittest.TestCase):
    def setUp(self):
        # Need to run the server in another process
        os.system("./Server.py &")

    def testStartup(self):
        defer = pb.getObjectAt('localhost', Server.DEFAULT_PORT, 30)
        defer.addCallbacks(self.connected, self.failure)
        reactor.run()

    def connected(self, perspective):
        perspective.callRemote('getGames').addCallbacks(self.success,
          self.failure)

    def success(self, games):
        print games
        assert len(games) == 0
        reactor.stop()

    def failure(self, error):
        print error
        reactor.stop()
        self.fail()

    def tearDown(self):
        os.system('pkill -f "python.*Server.py"')

if __name__ == '__main__':
    unittest.main()
