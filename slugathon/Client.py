#!/usr/bin/env python2.3

"""Outward-facing facade for client side."""

import sys
from twisted.spread import pb
import Server


class Client(pb.Referenceable):
    def __init__(self, username, password, host='localhost', 
          port=Server.DEFAULT_PORT):
        self.name = None
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        print self

    def remote_ping(self, arg):
        print "remote_ping(", arg, ") called on", self
        return True

    def remote_setname(self, name):
        print "remote_setname(", name, ")"
        self.name = name

    def __str__(self):
        return "Client " + str(self.name)

    def connect(self):
        return pb.connect(self.host, self.port, self.username, self.password,
          serviceName="SlugathonService", client=self, timeout=30)

