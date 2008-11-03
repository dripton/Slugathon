from odict import pdict, sdict

class TestPdict(object):
    def test_init_len(self):
        assert len(pdict()) == 0
        assert len(pdict({1: 2, 3: 4})) == 2
        assert len(pdict(a=1, b=2)) == 2
        assert len(pdict({1: 2, 3: 4}, a=1, b=2)) == 4

    def test_str_repr(self):
        assert str(pdict(a=1, b=2)) == "pdict{'a': 1, 'b': 2}"
        assert repr(pdict(a=1, b=2)) == "pdict{'a': 1, 'b': 2}"

    def test_setitem_order(self):
        pdic = pdict(z=1)
        pdic["y"] = 2
        pdic["x"] = 3
        assert pdic.keys() == ["z", "y", "x"]
        pdic["z"] = 1
        assert pdic.keys() == ["y", "x", "z"]

    def test_delitem(self):
        pdic = pdict(z=1)
        del pdic["z"]
        assert not pdic

    def test_clear(self):
        pdic = pdict(z=1)
        pdic.clear()
        assert not pdic

    def test_copy(self):
        pdic = pdict()
        pdic["c"] = 3
        pdic["b"] = 2
        pdic["a"] = 1
        pdic2 = pdic.copy()
        assert pdic2.items() == [("c", 3), ("b", 2), ("a", 1)]

    def test_update(self):
        pdic = pdict()
        pdic["c"] = 3
        pdic["b"] = 2
        pdic["a"] = 1
        pdic2 = pdict()
        pdic2.update(pdic)
        assert pdic2.items() == [("c", 3), ("b", 2), ("a", 1)]
        pdic3 = pdict()
        pdic3["a"] = 5
        pdic3["d"] = 4
        pdic2.update(pdic3)
        assert pdic2.items() == [("c", 3), ("b", 2), ("a", 5), ("d", 4)]

    def test_keys_values_items(self):
        pdic = pdict()
        pdic["c"] = 3
        pdic["b"] = 2
        pdic["a"] = 1
        assert pdic.keys() == list(pdic.iterkeys()) == ["c", "b", "a"]
        assert pdic.values() == list(pdic.itervalues()) == [3, 2, 1]
        assert pdic.items() == list(pdic.iteritems()) == [("c", 3), ("b", 2),
          ("a", 1)]

    def test_pop(self):
        pdic = pdict()
        pdic["c"] = 3
        pdic["b"] = 2
        pdic["a"] = 1
        assert pdic.pop("a") == 1
        try:
            pdic.pop("e")
        except KeyError:
            pass
        else:
            assert False
        assert pdic.pop("e", 6) == 6

    def test_popitem(self):
        pdic = pdict()
        pdic["c"] = 3
        pdic["b"] = 2
        pdic["a"] = 1
        assert pdic.popitem() == ("a", 1)
        assert pdic.popitem() == ("b", 2)
        assert pdic.popitem() == ("c", 3)
        try:
            pdic.popitem()
        except KeyError:
            pass
        else:
            assert False

    def test_fromkeys(self):
        pdic = pdict.fromkeys(range(3))
        assert str(pdic) == "pdict{0: None, 1: None, 2: None}"
        pdic = pdict.fromkeys(range(3), value=5)
        assert str(pdic) == "pdict{0: 5, 1: 5, 2: 5}"


class TestSdict(object):
    def test_init_len(self):
        assert len(sdict()) == 0
        assert len(sdict({1: 2, 3: 4})) == 2
        assert len(sdict(a=1, b=2)) == 2
        assert len(sdict({1: 2, 3: 4}, a=1, b=2)) == 4

    def test_str_repr(self):
        assert str(sdict(a=1, b=2)) == "sdict{'a': 1, 'b': 2}"
        assert repr(sdict(a=1, b=2)) == "sdict{'a': 1, 'b': 2}"

    def test_setitem_order(self):
        sdic = sdict(z=1)
        sdic["y"] = 2
        sdic["x"] = 3
        assert sdic.keys() == ["x", "y", "z"]
        sdic["z"] = 1
        assert sdic.keys() == ["x", "y", "z"]

    def test_delitem(self):
        sdic = sdict(z=1)
        del sdic["z"]
        assert not sdic

    def test_clear(self):
        sdic = sdict(z=1)
        sdic.clear()
        assert not sdic

    def test_copy(self):
        sdic = sdict()
        sdic["c"] = 3
        sdic["b"] = 2
        sdic["a"] = 1
        sdic2 = sdic.copy()
        assert sdic2.items() == [("a", 1), ("b", 2), ("c", 3)]

    def test_update(self):
        sdic = sdict()
        sdic["c"] = 3
        sdic["b"] = 2
        sdic["a"] = 1
        sdic2 = sdict()
        sdic2.update(sdic)
        assert sdic2.items() == [("a", 1), ("b", 2), ("c", 3)]
        sdic3 = sdict()
        sdic3["a"] = 5
        sdic3["d"] = 4
        sdic2.update(sdic3)
        assert sdic2.items() == [("a", 5), ("b", 2), ("c", 3), ("d", 4)]

    def test_keys_values_items(self):
        sdic = sdict()
        sdic["c"] = 3
        sdic["b"] = 2
        sdic["a"] = 1
        assert sdic.keys() == list(sdic.iterkeys()) == ["a", "b", "c"]
        assert sdic.values() == list(sdic.itervalues()) == [1, 2, 3]
        assert sdic.items() == list(sdic.iteritems()) == [("a", 1), ("b", 2),
          ("c", 3)]

    def test_pop(self):
        sdic = sdict()
        sdic["c"] = 3
        sdic["b"] = 2
        sdic["a"] = 1
        assert sdic.pop("a") == 1
        try:
            sdic.pop("e")
        except KeyError:
            pass
        else:
            assert False
        assert sdic.pop("e", 6) == 6

    def test_popitem(self):
        sdic = sdict()
        sdic["c"] = 3
        sdic["b"] = 2
        sdic["a"] = 1
        assert sdic.popitem() == ("c", 3)
        assert sdic.popitem() == ("b", 2)
        assert sdic.popitem() == ("a", 1)
        try:
            sdic.popitem()
        except KeyError:
            pass
        else:
            assert False

    def test_fromkeys(self):
        sdic = sdict.fromkeys(range(3))
        assert str(sdic) == "sdict{0: None, 1: None, 2: None}"
        sdic = sdict.fromkeys(range(3), value=5)
        assert str(sdic) == "sdict{0: 5, 1: 5, 2: 5}"
