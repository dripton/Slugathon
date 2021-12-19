__copyright__ = "Copyright (c) 2006-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Null User proxy, for testing."""


from twisted.internet import defer

from slugathon.net import User


class NullUser(User.User):
    def __init__(self) -> None:
        pass

    def callRemote(*args) -> defer.Deferred:
        return defer.Deferred()
