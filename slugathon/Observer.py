import zope.interface

class IObserver(zope.interface.Interface):

    def update(observed, action):
        """Inform this observer than action has happened to observed."""
