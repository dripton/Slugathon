"""Outward-facing facade for client side."""

from twisted.spread import pb
import Server
from twisted.cred import credentials
from twisted.internet import reactor, defer
import Anteroom


class Client(pb.Referenceable):
    def __init__(self, username, password, host='localhost', 
          port=Server.DEFAULT_PORT):
        self.username = username
        self.playername = username # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.factory = pb.PBClientFactory()
        self.user = None
        self.anteroom = None
        print "Called Client init:", self

    def remote_set_name(self, name):
        print "remote_set_name(", name, ") called on", self
        self.playername = name
        return name

    def remote_ping(self, arg):
        print "remote_ping(", arg, ") called on", self
        return True

    def __str__(self):
        return "Client " + str(self.username)

    def connect(self):
        print "Client.connect", self
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallbacks(self.connected, self.failure)
        return def1

    def connected(self, user):
        print "Client.connected", self, user
        if user:
            self.user = user
            self.anteroom = Anteroom.Anteroom(user, self.username)
            # Allow chaining callbacks
            return defer.succeed(user)
        else:
            return defer.failure(user)

    def failure(self, error):
        print "Client.failure", self, error
        reactor.stop()

    def remote_notify_add_username(self, username):
        if self.anteroom:
            self.anteroom.add_username(username)

    def remote_notify_del_username(self, username):
        if self.anteroom:
            self.anteroom.del_username(username)

    def remote_receive_chat_message(self, text):
        if self.anteroom:
            self.anteroom.receive_chat_message(text)

    def remote_notify_formed_game(self, game):
        if self.anteroom:
            self.anteroom.add_game(game)

    def remote_notify_removed_game(self, game):
        if self.anteroom:
            self.anteroom.remove_game(game)

    def remote_notify_changed_game(self, game):
        print "Client.notify_changed_game", game.name
        if self.anteroom:
            self.anteroom.change_game(game)
