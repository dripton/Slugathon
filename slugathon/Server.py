#!/usr/bin/env python2.3

import sys
from twisted.spread import pb
from twisted.cred import authorizer
from twisted.python import usage
import twisted.internet.app
import User


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

def main(config):
    port = int(config["port"])

    app = twisted.internet.app.Application("Slugathon")
    auth = authorizer.DefaultAuthorizer(app)
    service = SlugathonService("SlugathonService", app, auth)
    service.perspectiveClass = User.User

    # TODO Add new users when they first login.
    # TODO Persist users
    user = service.createPerspective(name="unittest")
    id = user.makeIdentity(password="unittest")

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
