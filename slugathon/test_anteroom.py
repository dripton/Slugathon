import py
import gtk
from twisted.internet import reactor
from twisted.internet import utils

import Anteroom
import Client

client = None

def setup_module(module):
    utils.getProcessValue("python", ["Server.py"])

def test_init():
    global client
    client = Client.Client("unittest", "unittest")
    def1 = client.connect()
    def1.addCallback(connected)
    def1.addErrback(failure)

def connected():
    anteroom = client.anteroom
    assert isinstance(anteroom, Anteroom.Anteroom)
    gtk.main()

def failure():
    reactor.stop()
    py.test.fail()

def teardown_module(module):
    utils.getProcessValue("pkill", ["-f", "python.*Server.py"])
