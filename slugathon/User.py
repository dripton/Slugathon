from twisted.spread import pb

class User(pb.Perspective):
    """Perspective for a player or observer."""

    def __init__(self, perspectiveName):
        self.perspectiveName = perspectiveName

    def perspective_getname(self, arg):
        print "perspective_getname(", arg, ") called on", self
        return self.perspectiveName

    def __str__(self):
        return "User " + self.perspectiveName
