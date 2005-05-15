import os
import time
import py

import Anteroom
import Server
import Client


class TestAnteroom(object):
    def setup_class(cls):
        os.system("python Server.py &")
        time.sleep(1)

    def test_init(self):
        self.client = Client.Client("unittest", "unittest")
        def1 = self.client.connect()
        def1.addCallbacks(self.connected, self.failure)

    def connected(self):
        anteroom = self.client.anteroom
        assert isinstance(anteroom, Anteroom.Anteroom)
        while 1:
            gtk.main_iteration()

    def failure(self):
        py.test.fail()

    def teardown_class(cls):
        os.system('pkill -f "python.*Server.py"')
