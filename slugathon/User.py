from twisted.spread import pb
import time

class User(pb.Perspective):
    """Perspective for a player or observer."""

    def __init__(self, perspectiveName):
        pb.Perspective.__init__(self, perspectiveName)
        self.perspectiveName = perspectiveName

    def perspective_getname(self, arg):
        print "perspective_getname(", arg, ") called on", self
        return self.perspectiveName

    def __str__(self):
        return "User " + self.perspectiveName

    def attached(self, reference, identity):
        print "called User.attached", reference, identity
        self.client = reference
        self.client.callRemote("setname", self.perspectiveName)
        self.client.callRemote("ping", time.time())
        return pb.Perspective.attached(self, reference, identity)
