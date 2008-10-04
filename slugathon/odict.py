"""Ordered dictionaries"""

class pdict(dict):
    """Preserves the order in which items were added."""
    def __init__(self, dict=None, **kwargs):
        self._list = []
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __repr__(self):
        return "pdict%s" % dict.__repr__(self)

    def __setitem__(self, key, item):
        # If we re-add the same item, move it to the end.
        if key in self:
            self._list.remove(key)
        dict.__setitem__(self, key, item)
        self._list.append(key)

    def __delitem__(self, key):
        self._list.remove(key)
        dict.__delitem__(self, key)

    def clear(self):
        dict.clear(self)
        self._list = []

    def copy(self):
        clone = pdict()
        for key, value in self.iteritems():
            clone[key] = value
        return clone

    def keys(self):
        return self._list[:]

    def iterkeys(self):
        for key in self._list:
            yield key

    def items(self):
        return [(key, self[key]) for key in self._list]

    def iteritems(self):
        for key in self._list:
            yield (key, self[key])

    def values(self):
        return [self[key] for key in self._list]

    def itervalues(self):
        for key in self._list:
            yield self[key]

    def update(self, dict=None, **kwargs):
        if dict is not None:
            for key, value in dict.iteritems():
                self[key] = value
        if kwargs:
            for key, value in kwargs:
                self[key] = value

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %d" % 
              len(args))
        try:
            self._list.remove(key)
        except ValueError:
            if args:
                return args[0]
            else:
                raise KeyError(str(key))
        return dict.pop(self, key, *args)

    def popitem(self):
        try:
            key = self._list.pop()
        except IndexError:
            raise KeyError("popitem() dictionary is empty")
        value = self[key]
        dict.__delitem__(self, key)
        return (key, value)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        pdic = cls()
        for key in iterable:
            pdic[key] = value
        return pdic


class sdict(dict):
    """Keeps items in the natural sorted order of the keys."""
    def __init__(self, dict=None, **kwargs):
        self._list = []
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __repr__(self):
        return "sdict%s" % dict.__repr__(self)

    def __setitem__(self, key, item):
        # If we re-add the same item, move it to the end.
        if key in self:
            self._list.remove(key)
        dict.__setitem__(self, key, item)
        self._list.append(key)
        self._list.sort()

    def __delitem__(self, key):
        self._list.remove(key)
        dict.__delitem__(self, key)

    def clear(self):
        dict.clear(self)
        self._list = []

    def copy(self):
        clone = sdict()
        for key, value in self.iteritems():
            clone[key] = value
        return clone

    def keys(self):
        return self._list[:]

    def iterkeys(self):
        for key in self._list:
            yield key

    def items(self):
        return [(key, self[key]) for key in self._list]

    def iteritems(self):
        for key in self._list:
            yield (key, self[key])

    def values(self):
        return [self[key] for key in self._list]

    def itervalues(self):
        for key in self._list:
            yield self[key]

    def update(self, dict=None, **kwargs):
        if dict is not None:
            for key, value in dict.iteritems():
                self[key] = value
        if kwargs:
            for key, value in kwargs:
                self[key] = value

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %d" % 
              len(args))
        try:
            self._list.remove(key)
        except ValueError:
            if args:
                return args[0]
            else:
                raise KeyError(str(key))
        return dict.pop(self, key, *args)

    def popitem(self):
        try:
            key = self._list.pop()
        except IndexError:
            raise KeyError("popitem() dictionary is empty")
        value = self[key]
        dict.__delitem__(self, key)
        return (key, value)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        sdic = cls()
        for key in iterable:
            sdic[key] = value
        return sdic

