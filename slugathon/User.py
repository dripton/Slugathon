from twisted.spread import pb
import time
from twisted.cred import portal

class User(pb.Avatar):
    """Perspective for a player or observer."""

    def __init__(self, name, server, client):
        self.name = name
        self.server = server
        self.client = None
        # XXX Bidirectional references
        self.server.addUser(self)
        print "User.init", self, name, server

    def perspective_getName(self, arg):
        print "perspective_getName(", arg, ") called on", self
        return self.name

    def perspective_getUserNames(self):
        print "perspective_getUserNames called on", self
        return self.server.getUserNames()

    def perspective_getGames(self):
        print "perspective_getGames called on", self
        return self.server.getGames()


    def __str__(self):
        return "User " + self.name

    def attached(self, mind):
        print "called User.attached", mind
        self.client.callRemote("setname", self.name)
        self.client.callRemote("ping", time.time())

    def logout(self):
        print "called logout"
