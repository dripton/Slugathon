from twisted.cred import authorizer, identity
from twisted.internet import defer

"""Authorizer that adds not-yet-taken usernames to the allowed list."""

class LazyAuthorizer(authorizer.DefaultAuthorizer):

    def __init__(self, serviceCollection=None):
        authorizer.DefaultAuthorizer.__init__(self, serviceCollection)
        # TODO Load saved identities into self.identities

    def getIdentityRequest(self, name):
        req = defer.Deferred()
        if self.identities.has_key(name):
            print "LazyAuthorizer.getIdentityRequest name found"
            req.callback(self.identities[name])
        else:
            id = identity.Identity(name, self)
            id.setPassword(name)   # XXX Need password
            self.addIdentity(id)
            req.callback(id)
            print "LazyAuthorizer.getIdentityRequest new id", id
        return req
