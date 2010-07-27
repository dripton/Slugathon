"""Null User proxy, for testing."""

from twisted.internet import defer

class NullUser(object):
    def callRemote(*args):
        return defer.Deferred()
