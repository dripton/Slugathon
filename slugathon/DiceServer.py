#!/usr/bin/env python

import random
import time
from twisted.spread import pb
from twisted.cred import checkers, portal
import twisted.internet
import Dice


class DiceServer:
    def __init__(self):
        self.dice = Dice.Dice()
        print "Started DiceServer at", time.ctime() 

    def perspective_login(self, arg):
        print "called perspective_login", arg

    def perspective_nextRoll(self, sides=6, numrolls=1):
        return self.dice.roll(sides, numrolls)

class MyPerspective(pb.Avatar):
    def __init__(self, name):
        self.name = name
        self.server = None

    def perspective_nextRoll(self, *args):
        return self.server.perspective_nextRoll(*args)

class MyRealm:
    __implements__ = portal.IRealm

    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = MyPerspective(avatarId)
        avatar.server = self.server
        return pb.IPerspective, avatar, lambda: None

def main():
    realm = MyRealm()
    realm.server = DiceServer()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser("user1", "pass1")
    p = portal.Portal(realm, [checker])

    app = twisted.internet.app.Application("DiceServer")
    app.listenTCP(pb.portno, pb.PBServerFactory(p))
    app.run(save=False)

if __name__ == "__main__":
    main()
