#!/usr/bin/env python2.3

import sys
from sets import Set
import time
from twisted.spread import pb
from twisted.cred import checkers, portal
from twisted.python import usage
import twisted.internet.app
import Realm
import Game


DEFAULT_PORT = 26569

class Server:
    """A Slugathon server, which can host multiple games in parallel."""
    def __init__(self):
        print "Called Server.init", self
        self.games = []
        self.users = Set()
        self.name_to_user = {}

    def addUser(self, user):
        print "called Server.addUser", self, user
        self.users.add(user)
        username = user.name
        self.name_to_user[username] = user
        for u in self.users:
            u.notifyAddUsername(username)

    def delUser(self, user):
        print "called Server.delUser", self, user
        self.users.remove(user)
        username = user.name
        del self.name_to_user[username]
        for u in self.users:
            u.notifyDelUsername(username)

    def getUserNames(self):
        names = self.name_to_user.keys()
        names.sort()
        return names

    def getGames(self):
        return self.games[:]

    def send_chat_message(self, source, dest, text):
        """Send a chat message from user sender to users in dest.

           source is a username.  dest is a list of usernames.
           If dest is None, send to all users
        """
        print "called Server.send_chat_message", source, dest, text
        message = "%s: %s" % (source, text)
        if dest is None:
            dest = self.name_to_user.keys()
        for username in dest:
            user = self.name_to_user[username]
            user.receive_chat_message(message)

    def form_game(self, username, game_name, min_players, max_players):
        if not game_name:
            raise ValueError('Games must be named')
        if game_name in [g.name for g in self.games]:
            raise ValueError('The game name "%s" is already in use' 
              % game_name)
        if min_players > max_players:
            raise ValueError('min_players must be <= max_players')
        now = time.time()
        GAME_START_DELAY = 20
        game = Game.Game(game_name, username, now, now + GAME_START_DELAY,
            min_players, max_players)
        self.games.append(game)
        for u in self.users:
            u.notifyFormedGame(game)

    def drop_from_game(self, username, game):
        if not username in game.players:
            print 'drop_from_game from', username, 'not in game', game.name
        elif len(game.players) == 1:
            if game in self.games:
                self.games.remove(game)
            for u in self.users:
                u.notifyRemovedGame(game)
        else:
            game.remove_player(username)
            for u in self.users:
                u.notifyChangedGame(game)

    def join_game(self, username, game):
        if username in game.players:
            print 'join_game from', username, 'already in game', game.name
        elif len(game.players) >= game.max_players:
            print username, 'tried to join full game', game.name
        else:
            print 'adding', username, 'to', game.name
            game.add_player(username)
            for u in self.users:
                u.notifyChangedGame(game)


class Options(usage.Options):
    optParameters = [
      ["port", "p", DEFAULT_PORT, "Port number"],
    ]


def main(config):
    port = int(config["port"])

    server = Server()
    realm = Realm.Realm(server)
    checker = checkers.FilePasswordDB("passwd.txt")
    po = portal.Portal(realm, [checker])

    app = twisted.internet.app.Application("Slugathon")
    pbfact = pb.PBServerFactory(po)
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
