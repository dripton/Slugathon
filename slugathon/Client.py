#!/usr/bin/env python2.3

"""Outward-facing facade for client side."""

import sys
from twisted.spread import pb

class Client(pb.Referenceable):
    def __init__(self):
        self.name = None
        print self

    def remote_ping(self, arg):
        print "remote_ping(", arg, ") called on", self
        return True

    def remote_setname(self, name):
        print "remote_setname(", name, ")"
        self.name = name

    def __str__(self):
        return "Client " + str(self.name)
