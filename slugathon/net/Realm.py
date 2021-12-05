from twisted.cred import portal
from twisted.spread import pb
from zope.interface import implementer

from slugathon.net import User


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(portal.IRealm)
class Realm(object):
    def __init__(self, server):
        self.server = server

    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        str_avatar_id = avatarId.decode()
        avatar = User.User(str_avatar_id, self.server, mind)
        avatar.attached(mind)
        return pb.IPerspective, avatar, avatar.logout
