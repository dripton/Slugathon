import zope.interface

class IObserver(zope.interface.Interface):

    def update(observed, action):
        """Inform this observer than action has happened to observed.
        
        observed may be None, in which case the action should contain
        all necessary information.
        """
