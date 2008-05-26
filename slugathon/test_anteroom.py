import py
import gtk
from twisted.internet import reactor
from twisted.internet import utils

import Anteroom
import Client


class TestAnteroom(object):
    def setup_class(cls):
        utils.getProcessValue("python", ["Server.py"])

    def test_init(self):
        self.client = Client.Client("unittest", "unittest")
        def1 = self.client.connect()
        def1.addCallback(self.connected)
        def1.addErrback(self.failure)

    def connected(self):
        anteroom = self.client.anteroom
        assert isinstance(anteroom, Anteroom.Anteroom)
        gtk.main()

    def failure(self):
        reactor.stop()
        py.test.fail()

    def teardown_class(cls):
        utils.getProcessValue("pkill", ["-f", "python.*Server.py"])
