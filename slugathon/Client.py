#!/usr/bin/env python2.3

"""Outward-facing facade for client side."""

import sys
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

    def remote_setName(self, name):
        print "remote_setName(", name, ") called on", self
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
        self.user = user
        self.anteroom = Anteroom.Anteroom(user)
        # Allow chaining callbacks
        return defer.succeed(user)

    def failure(self, error):
        "Client.failure", self, error
        reactor.stop()

    def remote_notifyAddUsername(self, username):
        self.anteroom.addUsername(username)

    def remote_notifyDelUsername(self, username):
        self.anteroom.delUsername(username)
