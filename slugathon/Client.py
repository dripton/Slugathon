"""Outward-facing facade for client side."""

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor, defer
import zope.interface

import Server
import Anteroom
from Observer import IObserver
from Observed import Observed


class Client(pb.Referenceable, Observed):

    zope.interface.implements(IObserver)

    def __init__(self, username, password, host='localhost', 
          port=Server.DEFAULT_PORT):
        Observed.__init__(self)
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
            self.attach(self.anteroom)
            # Allow chaining callbacks
            return defer.succeed(user)
        else:
            return defer.failure(user)

    def failure(self, error):
        print "Client.failure", self, error
        reactor.stop()

    # TODO Make this an Action, after adding a filter on Observed.notify
    def remote_receive_chat_message(self, text):
        self.anteroom.receive_chat_message(text)

    def remote_update(self, action):
        """Near-IObserver on the remote User, except observed is
           not passed remotely.

           Delegates to update to honor the interface.
        """
        observed = None
        print "Client.remote_update", self, observed, action
        self.update(observed, action)

    # TODO Game should observe Client directly.
    def update(self, observed, action):
        """Updates from User will come via remote_update, with
           observed set to None."""
        print "Client.update", self, observed, action
        self.notify(action)
