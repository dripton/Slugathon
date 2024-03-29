from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Tuple, Type

from twisted.cred import portal
from twisted.spread.pb import IPerspective, RemoteReference
from zope.interface import implementer

from slugathon.net import User

if TYPE_CHECKING:
    from slugathon.net import Server


__copyright__ = "Copyright (c) 2003-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(portal.IRealm)
class Realm(object):
    def __init__(self, server: Server.Server):
        self.server = server

    def requestAvatar(
        self,
        avatarId: bytes,
        mind: RemoteReference,
        *interfaces: Tuple[IPerspective, ...],
    ) -> Tuple[Type[IPerspective], User.User, Callable]:
        assert IPerspective in interfaces
        str_avatar_id = avatarId.decode()
        avatar = User.User(str_avatar_id, self.server, mind)
        avatar.attached(mind)
        return IPerspective, avatar, avatar.logout
