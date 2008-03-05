import py
from bag import bag

def test_add():
    b = bag()
    b.add(1)
    b.add(1)
    assert b[1] == 2
    assert 1 in b

def test_remove():
    b = bag()
    b.add(1)
    b.add(1)
    b.remove(1)
    assert b[1] == 1
    assert 1 in b
    b.remove(1)
    assert b[1] == 0
    assert 1 not in b
    try:
        b.remove("not in there")
    except KeyError:
        pass
    else:
        py.test.fail("should have raised")

def test_discard():
    b = bag()
    b.add(1)
    b.add(1)
    b.discard(1)
    assert b[1] == 1
    assert 1 in b
    b.discard(1)
    assert b[1] == 0
    assert 1 not in b
    b.discard("not in there")

def test_repr():
    b = bag()
    b.add(1)
    b.add(1)
    b.add(2)
    b.remove(2)
    assert str(b) == "bag({1: 2})"

def test_init():
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
        py.test.fail("should have raised")

def test_setitem():
    b = bag()
    b[1] = 1
    assert 1 in b
    assert b[1] == 1

def test_equal():
    b1 = bag(dict(a=1, b=1, c=2))
    b2 = bag(dict(c=2, b=1, a=1))
    assert b1 == b2

def test_not_equal():
    b1 = bag(dict(a=1, b=1, c=2))
    b2 = bag(dict(c=2, b=1, a=1))
    assert not (b1 != b2)
    b3 = bag(dict(c=3, b=1, a=1))
    assert b1 != b3

def test_union():
    b1 = bag(dict(a=1, b=1))
    b2 = bag(dict(a=2, c=1))
    b3 = b1.union(b2)
    assert b3 == bag(dict(a=3, b=1, c=1))

def test_update():
    b1 = bag(dict(a=1, b=1))
    b1.update(["c"])
    assert b1 == bag(dict(a=1, b=1, c=1))

    b1.update({"c":0})
    assert b1 == bag(dict(a=1, b=1, c=1))

    b1.update(["c", "c", "c", "b", "c"])
    assert b1 == bag(dict(a=1, b=2, c=5))

def test_clear():
    b = bag()
    b.add(1)
    assert b
    b.clear()
    assert not b
    assert len(b) == 0

def test_copy():
    b1 = bag()
    b1.add(1)
    b2 = b1.copy()
    assert len(b1) == len(b2)
    assert b1 == b2

def test_difference():
    b1 = bag({"a":1, "b":0, 1:2})
    b2 = bag({"a":1, "b":1, 1:1})
    assert b1.difference(b2) == bag({1:1})

def test_intersection():
    b1 = bag({"a":1, "b":0, 1:4})
    b2 = bag({"a":1, "b":1, 1:2})
    assert b1.intersection(b2) == b2.intersection(b1) == bag({"a":1, 1:2})

def test_issubset():
    b1 = bag({"a":1, "b":0, 1:4})
    b2 = bag({"a":1, "b":1, 1:2})
    b3 = bag({"a":9, "b":9, 1:9})
    assert b1.issubset(b1)
    assert b2.issubset(b2)
    assert b3.issubset(b3)
    assert not b1.issubset(b2)
    assert b1.issubset(b3)
    assert not b2.issubset(b1)
    assert b2.issubset(b3)
    assert not b3.issubset(b1)
    assert not b3.issubset(b2)

def test_issuperset():
    b1 = bag({"a":1, "b":0, 1:4})
    b2 = bag({"a":1, "b":1, 1:2})
    b3 = bag({"a":9, "b":9, 1:9})
    assert b1.issuperset(b1)
    assert b2.issuperset(b2)
    assert b3.issuperset(b3)
    assert not b1.issuperset(b2)
    assert not b1.issuperset(b3)
    assert not b2.issuperset(b1)
    assert not b2.issuperset(b3)
    assert b3.issuperset(b1)
    assert b3.issuperset(b2)

def test_iter():
    b1 = bag({"a":1, "b":0, 1:4})
    lst = []
    for el in b1:
        lst.append(el)
    assert "a" in lst
    assert 1 in lst
    assert "b" not in lst

def test_items():
    b1 = bag({"a":1, "b":0, 1:4})
    assert b1.items() == [("a", 1), (1, 4)]

def test_iteritems():
    b1 = bag({"a":1, "b":0, 1:4})
    assert list(b1.iteritems()) == [("a", 1), (1, 4)]

def test_keys():
    b1 = bag({"a":1, "b":0, 1:4})
    assert b1.keys() == ["a", 1]

def test_iterkeys():
    b1 = bag({"a":1, "b":0, 1:4})
    assert list(b1.iterkeys()) == ["a", 1]

def test_values():
    b1 = bag({"a":1, "b":0, 1:4})
    assert sorted(b1.values()) == [1, 4]

def test_itervalues():
    b1 = bag({"a":1, "b":0, 1:4})
    assert sorted(b1.itervalues()) == [1, 4]
