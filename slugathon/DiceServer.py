#!/usr/bin/env python

import random
import time
from twisted.spread import pb
import twisted.internet.app
import Dice


class DiceServer(pb.Root):
    def __init__(self):
        self.dice = Dice.Dice()
        print "Started DiceServer at", time.ctime() 

    def remote_nextRoll(self, sides=6, numrolls=1):
        return self.dice.roll(sides, numrolls)

def main():
    app = twisted.internet.app.Application("DiceServer")
    app.listenTCP(pb.portno, pb.BrokerFactory(DiceServer()))
    app.run()

if __name__ == "__main__":
    main()
