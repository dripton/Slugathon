__copyright__ = "Copyright (c) 2005-2008 David Ripton"
__license__ = "GNU GPL v2"

"""A multiset, built on a dictionary."""


class bag(object):
    """A multiset, built on a dictionary."""
    def __init__(self, iterable=None):
        self._dic = {}
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        """Update this object with items from iterable."""
        if hasattr(iterable, "items"):
            for key, val in iterable.iteritems():
                if val != int(val) or val < 0:
                    raise ValueError("illegal bag value")
                combo = self._dic.get(key, 0) + val
                if combo > 0:
                    self._dic[key] = combo
        else:
            for item in iterable:
                self.add(item)

    def add(self, key):
        """Add one of key."""
        self._dic[key] = self._dic.get(key, 0) + 1

    def remove(self, key):
        """Remove one of key."""
        if self._dic[key] <= 1:
            del self._dic[key]
        else:
            self._dic[key] -= 1

    def discard(self, key):
        """Remove one of key, if possible.  If not, do nothing."""
        if key not in self._dic:
            return
        self.remove(key)

    def __getitem__(self, key):
        """Return the count for key."""
        return self._dic.get(key, 0)

    def __setitem__(self, key, value):
        """Set the count for key to value."""
        if value >= 1:
            self._dic[key] = value
        else:
            del self._dic[key]

    def __contains__(self, item):
        """Return True iff item is in the bag."""
        return item in self._dic

    def __repr__(self):
        """Return a string representation of the bag."""
        return "bag(%s)" % str(self._dic)

    def __len__(self):
        """Return the number of keys."""
        return len(self._dic)

    def __eq__(self, other):
        """Return True iff other is equal to this bag."""
        if isinstance(other, bag):
            return self._dic == other._dic
        else:
            return False

    def __ne__(self, other):
        """Return True iff other is not equal to this bag."""
        return not self.__eq__(other)

    def union(self, other):
        """Return a new bag containing all items in this bag and the other."""
        if not isinstance(other, bag):
            raise TypeError("not a bag")
        newbag = bag(self._dic)
        for key, val in other._dic.iteritems():
            newbag[key] += val
        return newbag

    def clear(self):
        """Remove all elements from this bag."""
        self._dic.clear()

    def copy(self):
        """Return a shallow copy."""
        return bag(self._dic)

    def difference(self, other):
        """Return the difference between this bag and other as a new bag."""
        if not isinstance(other, bag):
            raise TypeError("not a bag")
        newbag = bag(self._dic)
        for key, val in self._dic.iteritems():
            val2 = other[key]
            if val2:
                newbag[key] = max(val - val2, 0)
        return newbag

    def intersection(self, other):
        """Return a new bag with the elements that are in both bags."""
        if not isinstance(other, bag):
            raise TypeError("not a bag")
        newbag = bag(self._dic)
        for key, val in self._dic.iteritems():
            val2 = other[key]
            newbag[key] = min(val, val2)
        return newbag

    def issubset(self, other):
        """Report whether the other bag contains everything in this one."""
        if not isinstance(other, bag):
            raise TypeError("not a bag")
        for key, val in self._dic.iteritems():
            val2 = other[key]
            if val2 < val:
                return False
        return True

    def issuperset(self, other):
        """Report whether this bag contains everything in the other one."""
        if not isinstance(other, bag):
            raise TypeError("not a bag")
        for key, val in other._dic.iteritems():
            val2 = self[key]
            if val2 < val:
                return False
        return True

    def __iter__(self):
        """Return an iterator, which returns one of each item in the set."""
        return iter(self._dic.iterkeys())

    def items(self):
        """Return a list of item, count pairs."""
        return self._dic.items()

    def iteritems(self):
        """Yield item, count pairs."""
        return self._dic.iteritems()

    def keys(self):
        """Return a list of one of each item in the set."""
        return self._dic.keys()

    def iterkeys(self):
        """Yield each item in the set."""
        return self._dic.iterkeys()

    def values(self):
        """Return a list of counts for each item in the set."""
        return self._dic.values()

    def itervalues(self):
        """Yield counts for each item in the set."""
        return self._dic.itervalues()
