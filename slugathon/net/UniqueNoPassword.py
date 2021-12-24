from typing import Any

from twisted.cred.credentials import IUsernameHashedPassword
from twisted.cred.error import LoginDenied
from twisted.internet import defer

from slugathon.net.UniqueFilePasswordDB import UniqueFilePasswordDB

__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


class UniqueNoPassword(UniqueFilePasswordDB):
    """A checker that does not check passwords but refuses to authenticate a
    user who is already logged in."""

    def requestAvatarId(self, credentials: IUsernameHashedPassword) -> Any:
        if self.server is None:
            return defer.fail(LoginDenied())
        elif credentials.username in self.server.playernames:  # type: ignore
            # already logged in
            return defer.fail(LoginDenied())
        else:
            return defer.succeed(credentials.username)  # type: ignore
