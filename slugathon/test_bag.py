#!/usr/bin/env python

import unittest
from bag import bag

class TestCase(unittest.TestCase):
    def test_add(self):
        b = bag()
        b.add(1)
        b.add(1)
        assert b[1] == 2
        assert 1 in b

    def test_remove(self):
        b = bag()
        b.add(1)
        b.add(1)
        b.remove(1)
        assert b[1] == 1
        assert 1 in b
        b.remove(1)
        assert b[1] == 0
        assert 1 not in b

    def test_repr(self):
        b = bag()
        b.add(1)
        b.add(1)
        b.add(2)
        b.remove(2)
        assert str(b) == "bag({1: 2})"

    def test_init(self):
        b = bag({"a":1, "b":0, "c":-1, 1:2}, d=0, e=-1, f=1, g=5)
        assert "a" in b
        assert 1 in b
        assert "f" in b
        assert "g" in b
        assert len(b) == 4

    def test_setitem(self):
        b = bag()
        b[1] = 1
        assert 1 in b
        assert b[1] == 1

if __name__ == "__main__":
    unittest.main()
