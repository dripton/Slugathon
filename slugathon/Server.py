#!/usr/bin/env python2.3

from twisted.spread import pb
from twisted.cred import authorizer
import twisted.internet.app


DEFAULT_PORT = 26569

class Server(pb.Root):
    """A Slugathon server, which can host multiple games in parallel."""

    def __init__(self, port=DEFAULT_PORT):
        self.games = []

    def remote_getGames(self):
        return self.games

def main():
    app = twisted.internet.app.Application("Slugathon")
    app.listenTCP(DEFAULT_PORT, pb.BrokerFactory(Server()))
    app.run()

if __name__ == '__main__':
    main()
