from typing import Union

import pytest

from slugathon.util.bag import bag

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


def test_add() -> None:
    b = bag()  # type: bag[int]
    b.add(1)
    b.add(1)
    assert b[1] == 2
    assert 1 in b


def test_remove() -> None:
    b = bag()  # type: bag[int]
    b.add(1)
    b.add(1)
    b.remove(1)
    assert b[1] == 1
    assert 1 in b
    b.remove(1)
    assert b[1] == 0
    assert 1 not in b
    with pytest.raises(KeyError):
        b.remove(5)


def test_discard() -> None:
    b = bag()  # type: bag[int]
    b.add(1)
    b.add(1)
    b.discard(1)
    assert b[1] == 1
    assert 1 in b
    b.discard(1)
    assert b[1] == 0
    assert 1 not in b
    b.discard(5)


def test_repr() -> None:
    b = bag()  # type: bag[int]
    b.add(1)
    b.add(1)
    b.add(2)
    b.remove(2)
    assert str(b) == "bag({1: 2})"


def test_init() -> None:
    b = bag({"a": 1, "b": 0, 1: 2})  # type: bag[Union[int, str]]
    assert "a" in b
    assert "b" not in b
    assert 1 in b
    assert len(b) == 2
    with pytest.raises(ValueError):
        b = bag({"a": -1})


def test_setitem() -> None:
    b = bag()  # type: bag[int]
    b[1] = 1
    assert 1 in b
    assert b[1] == 1


def test_equal() -> None:
    b1 = bag(dict(a=1, b=1, c=2))  # type: bag[str]
    b2 = bag(dict(c=2, b=1, a=1))  # type: bag[str]
    assert b1 == b2
    assert b1 != "a string"


def test_not_equal() -> None:
    b1 = bag(dict(a=1, b=1, c=2))  # type: bag[str]
    b2 = bag(dict(c=2, b=1, a=1))  # type: bag[str]
    assert not (b1 != b2)
    b3 = bag(dict(c=3, b=1, a=1))  # type: bag[str]
    assert b1 != b3
    assert b1 != "a string"


def test_union() -> None:
    b1 = bag(dict(a=1, b=1))  # type: bag[str]
    b2 = bag(dict(a=2, c=1))  # type: bag[str]
    b3 = b1.union(b2)
    assert b3 == bag(dict(a=3, b=1, c=1))
    with pytest.raises(TypeError):
        b1.union("a string")  # type: ignore


def test_update() -> None:
    b1 = bag(dict(a=1, b=1))  # type: bag[str]
    b1.update(["c"])
    assert b1 == bag(dict(a=1, b=1, c=1))

    b1.update({"c": 0})
    assert b1 == bag(dict(a=1, b=1, c=1))

    b1.update(["c", "c", "c", "b", "c"])
    assert b1 == bag(dict(a=1, b=2, c=5))


def test_clear() -> None:
    b = bag()  # type: bag[int]
    b.add(1)
    assert b
    b.clear()
    assert not b
    assert len(b) == 0


def test_copy() -> None:
    b1 = bag()  # type: bag[int]
    b1.add(1)
    b2 = b1.copy()
    assert len(b1) == len(b2)
    assert b1 == b2


def test_difference() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 2})  # type: bag[Union[int, str]]
    b2 = bag({"a": 1, "b": 1, 1: 1})  # type: bag[Union[int, str]]
    assert b1.difference(b2) == bag({1: 1})
    with pytest.raises(TypeError):
        b1.difference("a string")  # type: ignore


def test_intersection() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    b2 = bag({"a": 1, "b": 1, 1: 2})  # type: bag[Union[int, str]]
    assert b1.intersection(b2) == b2.intersection(b1) == bag({"a": 1, 1: 2})
    with pytest.raises(TypeError):
        b1.intersection("a string")  # type: ignore


def test_issubset() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    b2 = bag({"a": 1, "b": 1, 1: 2})  # type: bag[Union[int, str]]
    b3 = bag({"a": 9, "b": 9, 1: 9})  # type: bag[Union[int, str]]
    assert b1.issubset(b1)
    assert b2.issubset(b2)
    assert b3.issubset(b3)
    assert not b1.issubset(b2)
    assert b1.issubset(b3)
    assert not b2.issubset(b1)
    assert b2.issubset(b3)
    assert not b3.issubset(b1)
    assert not b3.issubset(b2)
    with pytest.raises(TypeError):
        b1.issubset("a string")  # type: ignore


def test_issuperset() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    b2 = bag({"a": 1, "b": 1, 1: 2})  # type: bag[Union[int, str]]
    b3 = bag({"a": 9, "b": 9, 1: 9})  # type: bag[Union[int, str]]
    assert b1.issuperset(b1)
    assert b2.issuperset(b2)
    assert b3.issuperset(b3)
    assert not b1.issuperset(b2)
    assert not b1.issuperset(b3)
    assert not b2.issuperset(b1)
    assert not b2.issuperset(b3)
    assert b3.issuperset(b1)
    assert b3.issuperset(b2)
    with pytest.raises(TypeError):
        b1.issuperset("a string")  # type: ignore


def test_iter() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    lst = []
    for el in b1:
        lst.append(el)
    assert "a" in lst
    assert 1 in lst
    assert "b" not in lst


def test_items() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    assert list(b1.items()) == [("a", 1), (1, 4)]


def test_keys() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    assert list(b1.keys()) == ["a", 1]


def test_values() -> None:
    b1 = bag({"a": 1, "b": 0, 1: 4})  # type: bag[Union[int, str]]
    assert sorted(b1.values()) == [1, 4]
