#!/usr/bin/env python

import sys
from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred import credentials

class DiceClient:
    def __init__(self, server="localhost", sides=6, numrolls=1):
        self.sides = sides
        self.numrolls = numrolls
        factory = pb.PBClientFactory()
        reactor.connectTCP(server, pb.portno, factory)
        def1 = factory.login(credentials.UsernamePassword("user1", "pass1"))
        def1.addCallbacks(self.connected, self.failure)
        reactor.run()

    def connected(self, perspective):
        print "client connected"
        perspective.callRemote('nextRoll', self.sides, 
          self.numrolls).addCallbacks(self.success, self.failure)

    def success(self, roll):
        print "Rolled", roll
        reactor.stop()

    def failure(self, error):
        print "Failure", error
        reactor.stop()
        return error


def usage(progname):
    print "%s [server name] [number of sides] [number of rolls]" % progname
    sys.exit(1)

if __name__ == "__main__":
    try:
        server = sys.argv[1]
        sides = int(sys.argv[2])
        numrolls = int(sys.argv[3])
        assert sides >= 1
    except LookupError:
        usage(sys.argv[0])
    except AssertionError:
        usage(sys.argv[0])

    DiceClient(server, sides, numrolls)
