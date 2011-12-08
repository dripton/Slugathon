__copyright__ = "Copyright (c) 2004-2011 David Ripton"
__license__ = "GNU GPL v2"


from zope.interface import Interface


class IObserver(Interface):

    def update(observed, action, names):
        """Inform this observer that action has happened to observed.

        observed may be None, in which case action should contain
        all necessary information.
        """
