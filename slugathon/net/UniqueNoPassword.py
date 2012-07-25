__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"


from twisted.cred.error import LoginDenied
from twisted.internet import defer

from slugathon.net.UniqueFilePasswordDB import UniqueFilePasswordDB


class UniqueNoPassword(UniqueFilePasswordDB):
    """A checker that does not check passwords but refuses to authenticate a
    user who is already logged in."""

    def requestAvatarId(self, credentials):
        if credentials.username in self.server.playernames:
            # already logged in
            return defer.fail(LoginDenied())
        else:
            return defer.succeed(credentials.username)
