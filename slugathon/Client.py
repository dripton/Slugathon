#!/usr/bin/env python2.3

"""Outward-facing facade for client side."""

import sys
from twisted.spread import pb
import Server
from twisted.cred import credentials
from twisted.internet import reactor


class Client(pb.Referenceable):
    def __init__(self, username, password, host='localhost', 
          port=Server.DEFAULT_PORT):
        self.name = None
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.factory = pb.PBClientFactory()
        print self

    def perspective_ping(self, arg):
        print "perspective_ping(", arg, ") called on", self
        return True

    def perspective_setname(self, name):
        print "perspective_setname(", name, ")"
        self.name = name

    def __str__(self):
        return "Client " + str(self.name)

    def connect(self):
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        return self.factory.login(user_pass)
