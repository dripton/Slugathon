import time
import subprocess

import py
try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass

import gtk
from twisted.internet import reactor

import Anteroom
import Client


class TestAnteroom(object):
    def setup_class(cls):
        subprocess.Popen("python Server.py &", shell=True)
        time.sleep(1)

    def test_init(self):
        self.client = Client.Client("unittest", "unittest")
        def1 = self.client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def connected(self):
        anteroom = self.client.anteroom
        assert isinstance(anteroom, Anteroom.Anteroom)
        while True:
            gtk.main_iteration()

    def failure(self):
        reactor.stop()
        py.test.fail()

    def teardown_class(cls):
        subprocess.call(["pkill", "-f", "python.*Server.py"])
        time.sleep(1)
