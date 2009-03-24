__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.internet import reactor
from twisted.internet import utils

import Client


def setup_class(cls):
    utils.getProcessValue("python", ["Server.py"])

def test_startup():
    client = Client.Client(username="unittest", password="unittest")
    def1 = client.connect()
    def1.addCallback(connected)
    def1.addErrback(failure)
    reactor.run()

def connected(perspective):
    print "connected", perspective
    def1 = perspective.callRemote("get_name", "foo")
    def1.addCallback(success)
    def1.addErrback(failure)

def success(name):
    assert name == "unittest"
    reactor.stop()

def failure(error):
    print error
    reactor.stop()
    assert False

def teardown_class(cls):
    utils.getProcessValue("pkill", ["-f", "python.*Server.py"])
