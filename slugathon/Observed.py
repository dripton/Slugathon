import zope.interface

class IObserved(zope.interface.Interface):
    def add_observer(observer, name=None):
        """Add an observer to this object."""

    def remove_observer(observer):
        """Remove an observer from this object."""

    def notify(action, names=None):
        """Tell all observers about this action."""


class Observed(object):
    """Inherit from this mixin and call its __init__ to allow the class 
    to be observed.""" 

    zope.interface.implements(IObserved)

    def __init__(self):
        self.observers = {}

    def add_observer(self, observer, name=""):
        print "called Observed.add_observer", self, observer
        if not observer in self.observers:
            self.observers[observer] = name

    def remove_observer(self, observer):
        print "called Observed.remove_observer", self, observer
        if observer in self.observers:
            del self.observers[observer]

    def notify(self, action, names=None):
        print "called Observed.notify", self, action, names
        for observer, name in self.observers.iteritems():
            if names is None or name in names:
                print self, "notifying", observer, "about", action
                observer.update(self, action)
            else:
                print self, "not notifying", observer, name, "about", action
