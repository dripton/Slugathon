__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.cred import portal
from twisted.spread import pb
from zope.interface import implements

from slugathon.net import User


class Realm(object):
    implements(portal.IRealm)

    def __init__(self, server):
        self.server = server

    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User.User(avatarId, self.server, mind)
        avatar.attached(mind)
        return pb.IPerspective, avatar, avatar.logout
