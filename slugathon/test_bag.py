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
        b = bag({"a":1, "b":0, 1:2})
        assert "a" in b
        assert "b" not in b
        assert 1 in b
        assert len(b) == 2

        try:
            b = bag({"a":-1})
        except ValueError:
            pass
        else:
            self.fail("should have raised")

    def test_setitem(self):
        b = bag()
        b[1] = 1
        assert 1 in b
        assert b[1] == 1

    def test_equal(self):
        b1 = bag(dict(a=1, b=1, c=2))
        b2 = bag(dict(c=2, b=1, a=1))
        assert b1 == b2

    def test_union(self):
        b1 = bag(dict(a=1, b=1))
        b2 = bag(dict(a=2, c=1))
        b3 = b1.union(b2)
        assert b3 == bag(dict(a=3, b=1, c=1))

    def test_update(self):
        b1 = bag(dict(a=1, b=1))
        b1.update(["c"])
        assert b1 == bag(dict(a=1, b=1, c=1))

        b1.update({"c":0})
        assert b1 == bag(dict(a=1, b=1))

        b1.update(["c", "c", "c", "b", "c"])
        assert b1 == bag(dict(a=1, b=2, c=4))


if __name__ == "__main__":
    unittest.main()
