class bag(object):
    """A multiset, built on a dictionary."""
    def __init__(self, iterable=None):
        self._dic = {}
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        if hasattr(iterable, "items"):
            for key, val in iterable.items():
                if val > 0:
                    self._dic[key] = val
                elif val == 0:
                    if key in self._dic:
                        del self._dic[key]
                else:
                    raise ValueError, "bag value must be whole number"
        else:
            for item in iterable:
                self.add(item)

    def add(self, key):
        self._dic[key] = self._dic.get(key, 0) + 1

    def remove(self, key):
        if self._dic[key] <= 1:
            del self._dic[key]
        else:
            self._dic[key] -= 1

    def __getitem__(self, key):
        return self._dic.get(key, 0)

    def __setitem__(self, key, value):
        if value >= 1:
            self._dic[key] = value
        else:
            del self._dic[key]

    def __contains__(self, item):
        return item in self._dic

    def __repr__(self):
        return "bag(%s)" % str(self._dic)

    def __len__(self):
        return len(self._dic)

    def __eq__(self, other):
        if isinstance(other, bag):
            return self._dic == other._dic
        else:
            return False

    def union(self, other):
        assert isinstance(other, bag)
        newbag = bag(self._dic)
        for key, val in other._dic.items():
            newbag[key] += val
        return newbag

