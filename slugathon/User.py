from twisted.spread import pb
import time
from twisted.cred import portal

class User(pb.Avatar):
    """Perspective for a player or observer."""

    def __init__(self, name):
        self.name = name
        self.server = None
        self.client = None

    def perspective_getname(self, arg):
        print "perspective_getname(", arg, ") called on", self
        return self.name

    def __str__(self):
        return "User " + self.name

    def attached(self, mind):
        print "called User.attached", mind
        self.client = mind
        self.client.callRemote("setname", self.name)
        self.client.callRemote("ping", time.time())

    def logout(self):
        print "called logout"
