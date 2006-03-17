#!/usr/bin/env python

import sys
import time

from twisted.spread import pb
from twisted.cred import checkers, portal
from twisted.python import usage
from twisted.internet import reactor
import zope.interface

import Realm
import Game
import Action
from Observed import Observed
from Observer import IObserver


DEFAULT_PORT = 26569


class Server(Observed):
    """A Slugathon server, which can host multiple games in parallel."""

    zope.interface.implements(IObserver)

    def __init__(self):
        print "Called Server.__init__", self
        Observed.__init__(self)
        self.games = []
        self.name_to_user = {}

    def add_observer(self, user):
        print "called Server.add_observer", self, user
        Observed.add_observer(self, user)
        username = user.name
        self.name_to_user[username] = user
        action = Action.AddUsername(username)
        self.notify(action)

    def remove_observer(self, user):
        print "called Server.remove_observer", self, user
        Observed.remove_observer(self, user)
        username = user.name
        if username in self.name_to_user:
            del self.name_to_user[username]
            action = Action.DelUsername(username)
            self.notify(action)

    def get_usernames(self):
        names = self.name_to_user.keys()
        names.sort()
        return names

    def get_games(self):
        print "get_games called on", self
        return self.games[:]

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

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
            raise ValueError("Games must be named")
        if game_name in [game.name for game in self.games]:
            raise ValueError('The game name "%s" is already in use' 
              % game_name)
        if min_players > max_players:
            raise ValueError("min_players must be <= max_players")
        now = time.time()
        GAME_START_DELAY = 5 * 60
        game = Game.Game(game_name, username, now, now + GAME_START_DELAY, 
          min_players, max_players)
        print "built Game"
        self.games.append(game)
        game.add_observer(self)
        action = Action.FormGame(username, game.name, game.create_time,
          game.start_time, game.min_players, game.max_players)
        self.notify(action)

    def join_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            try:
                game.add_player(username)
            except AssertionError:
                pass
            else:
                action = Action.JoinGame(username, game.name)
                self.notify(action)

    def drop_from_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            try:
                game.remove_player(username)
            except AssertionError:
                pass
            else:
                if len(game.players) == 0:
                    if game in self.games:
                        self.games.remove(game)
                    action = Action.RemoveGame(game.name)
                    self.notify(action)
                else:
                    action = Action.DropFromGame(username, game.name)
                    self.notify(action)

    def start_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.start(username)

    def pick_color(self, username, game_name, color):
        game = self.name_to_game(game_name)
        if game:
            game.assign_color(username, color)

    def pick_first_marker(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.assign_first_marker(username, markername)

    def split_legion(self, username, game_name, parent_markername,
      child_markername, parent_creaturenames, child_creaturenames):
        game = self.name_to_game(game_name)
        if game:
            game.split_legion(username, parent_markername, child_markername,
              parent_creaturenames, child_creaturenames)

    def undo_split(self, username, game_name, parent_markername, 
      child_markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_split(username, parent_markername, child_markername)

    def done_with_splits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_splits(username)

    def take_mulligan(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.take_mulligan(username)

    def move_legion(self, username, game_name, markername, hexlabel, 
      entry_side, teleport, teleporting_lord):
        game = self.name_to_game(game_name)
        if game:
            game.move_legion(username, markername, hexlabel, entry_side,
              teleport, teleporting_lord)

    def undo_move_legion(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_move_legion(username, markername)

    def done_with_moves(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_moves(username)

    def resolve_engagement(self, username, game_name, hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.resolve_engagement(username, hexlabel)

    def recruit_creature(self, username, game_name, markername, creature_name):
        game = self.name_to_game(game_name)
        if game:
            game.recruit_creature(username, markername, creature_name)

    def undo_recruit(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_recruit(username, markername)

    def done_with_recruits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_recruits(username)


    def update(self, observed, action):
        print "Server.update", observed, action
        self.notify(action)



class Options(usage.Options):
    optParameters = [
      ["port", "p", DEFAULT_PORT, "Port number"],
    ]


def main(options):
    port = int(options["port"])

    server = Server()
    realm = Realm.Realm(server)
    checker = checkers.FilePasswordDB("passwd.txt")
    po = portal.Portal(realm, [checker])

    pbfact = pb.PBServerFactory(po)
    reactor.listenTCP(port, pbfact)
    reactor.run()


if __name__ == "__main__":
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, errortext:
        print "%s: %s" % (sys.argv[0], errortext)
        print "%s: Try --help for usage details." % (sys.argv[0])
        sys.exit(1)
    main(options)
