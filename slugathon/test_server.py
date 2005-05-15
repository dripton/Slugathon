import os
import time
from twisted.spread import pb
from twisted.internet import reactor
import py

import Server
import Client

def setup_module(module):
    # Need to run the server in another process
    os.system("python Server.py &")
    # Give the OS a second to start it before we use it.
    time.sleep(1)

def test_startup():
    client = Client.Client(username="unittest", password="unittest")
    client.connect().addCallbacks(connected, failure)
    reactor.run()

def connected(perspective):
    print "connected", perspective
    perspective.callRemote("get_name", "foo").addCallbacks(success,
      failure)

def success(name):
    assert name == "unittest"
    reactor.stop()

def failure(error):
    print error
    reactor.stop()
    py.test.fail()

def teardown_module(module):
    os.system('pkill -f "python.*Server.py"')
