#!/usr/bin/env python

import sys
from twisted.internet import reactor
from twisted.spread import pb

class DiceClient:
    def __init__(self, server="localhost", sides=6, numrolls=1):
        self.sides = sides
        self.numrolls = numrolls
        ds = pb.getObjectAt(server, pb.portno, 30)
        ds.addCallback(self.connected)
        ds.addErrback(self.failure)
        reactor.run()

    def connected(self, perspective):
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
