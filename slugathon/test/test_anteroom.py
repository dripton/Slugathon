__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


import gtk
from twisted.internet import reactor
from twisted.internet import utils

from slugathon.gui import Anteroom, Client


client = None


def setup_module(module):
    utils.getProcessValue("python", ["slugathon server"])


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


# TODO Use a process protocol to make this more portable.
def teardown_module(module):
    utils.getProcessValue("pkill", ["-f", "python.*slugathon server"])
