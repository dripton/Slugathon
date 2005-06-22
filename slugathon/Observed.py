import zope.interface

class IObserved(zope.interface.Interface):
    def add_observer(observer):
        """Add an observer to this object."""

    def remove_observer(observer):
        """Remove an observer from this object."""

    def notify(action):
        """Tell all observers about this action."""


class Observed(object):
    """Inherit from this mixin and call its __init__ to allow the class 
    to be observed.""" 

    zope.interface.implements(IObserved)

    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        print "called Observed.add_observer", self, observer
        if not observer in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        print "called Observed.remove_observer", self, observer
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, action):
        print "called Observed.notify", self, action
        for obs in self.observers:
            obs.update(self, action)
