from twisted.cred import portal
from twisted.spread import pb
from zope.interface import implements

import User

class Realm(object):
    implements(portal.IRealm)

    def __init__(self, server):
        print "called Realm.__init__", self, server
        self.server = server

    def requestAvatar(self, avatar_id, mind, *interfaces):
        print "Called Realm.requestAvatar", self, avatar_id, mind, interfaces
        assert pb.IPerspective in interfaces
        avatar = User.User(avatar_id, self.server, mind)
        avatar.attached(mind)
        return pb.IPerspective, avatar, avatar.logout

