#!/usr/bin/env python2.3

import sys
from twisted.spread import pb
from twisted.cred import authorizer
from twisted.python import usage
import twisted.internet.app
import User
import LazyAuthorizer
import userdata


DEFAULT_PORT = 26569

class Server(pb.Root):
    """A Slugathon server, which can host multiple games in parallel."""
    def __init__(self):
        pb.Root.__init__(self)
        self.games = []


class SlugathonService(pb.Service):
    def __init__(self, serviceName, serviceParent, authorizer):
        pb.Service.__init__(self, serviceName, serviceParent, authorizer)
    perspectiveClass = Server


class Options(usage.Options):
    optParameters = [
      ["port", "p", DEFAULT_PORT, "Port number"],
    ]


def add_users(service):
    """Add username / password pairs from userdata"""
    for (username, password) in userdata.data:
        user = service.createPerspective(username)
        user.makeIdentity(password)

def main(config):
    port = int(config["port"])

    app = twisted.internet.app.Application("Slugathon")
    auth = LazyAuthorizer.LazyAuthorizer(app)
    service = SlugathonService("SlugathonService", app, auth)
    service.perspectiveClass = User.User

    add_users(service)

    pbfact = pb.BrokerFactory(pb.AuthRoot(auth))
    app.listenTCP(port, pbfact)
    app.run(save=False)


if __name__ == '__main__':
    config = Options()
    try:
        config.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
    main(config)
