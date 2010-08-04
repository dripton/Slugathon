__copyright__ = "Copyright (c) 2006-2010 David Ripton"
__license__ = "GNU GPL v2"


"""Null User proxy, for testing."""


from twisted.internet import defer


class NullUser(object):
    def callRemote(*args):
        return defer.Deferred()
