__copyright__ = "Copyright (c) 2003-2009 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from twisted.internet import reactor
from twisted.internet import utils

from slugathon.gui import Anteroom, Client

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
    assert False

def teardown_module(module):
    utils.getProcessValue("pkill", ["-f", "python.*Server.py"])
