from __future__ import annotations

from typing import Callable, Optional

from twisted.cred.checkers import FilePasswordDB
from twisted.cred.credentials import IUsernameHashedPassword
from twisted.cred.error import LoginDenied
from twisted.internet import defer

from slugathon.net import Server

__copyright__ = "Copyright (c) 2008-2021 David Ripton"
__license__ = "GNU GPL v2"


class UniqueFilePasswordDB(FilePasswordDB):

    """A FilePasswordDB that refuses to authenticate a user who is already
    logged in."""

    def __init__(
        self,
        filename: Optional[str],
        delim: bytes = b":",
        usernameField: int = 0,
        passwordField: int = 1,
        caseSensitive: bool = True,
        hash: Optional[Callable] = None,
        cache: bool = False,
        server: Optional[Server.Server] = None,
    ):
        FilePasswordDB.__init__(  # type: ignore
            self,
            filename,
            delim,
            usernameField,
            passwordField,
            caseSensitive,
            hash,
            cache,
        )
        self.server = server

    def requestAvatarId(
        self, credentials: IUsernameHashedPassword
    ) -> defer.Deferred:
        if self.server is None:
            return defer.fail(LoginDenied())
        elif credentials.username in self.server.playernames:  # type: ignore
            # already logged in
            return defer.fail(LoginDenied())
        else:
            return FilePasswordDB.requestAvatarId(self, credentials)  # type: ignore
