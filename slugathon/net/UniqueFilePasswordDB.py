__copyright__ = "Copyright (c) 2008-2012 David Ripton"
__license__ = "GNU GPL v2"


from twisted.cred.error import LoginDenied
from twisted.cred.checkers import FilePasswordDB
from twisted.internet import defer


class UniqueFilePasswordDB(FilePasswordDB):
    """A FilePasswordDB that refuses to authenticate a user who is already
    logged in."""

    def __init__(self, filename, delim=':', usernameField=0, passwordField=1,
      caseSensitive=True, hash=None, cache=False, server=None):
        FilePasswordDB.__init__(self, filename, delim, usernameField,
          passwordField, caseSensitive, hash, cache)
        self.server = server

    def requestAvatarId(self, c):
        if c.username in self.server.playernames:
            # already logged in
            return defer.fail(LoginDenied())
        else:
            return FilePasswordDB.requestAvatarId(self, c)
