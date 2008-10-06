from twisted.internet import reactor
from twisted.internet import utils
import py

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
    py.test.fail()

def teardown_class(cls):
    utils.getProcessValue("pkill", ["-f", "python.*Server.py"])
