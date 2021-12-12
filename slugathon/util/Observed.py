from typing import Any, Dict, List, Optional

from zope.interface import Interface, implementer

from slugathon.game import Action
from slugathon.util import Observer


__copyright__ = "Copyright (c) 2004-2011 David Ripton"
__license__ = "GNU GPL v2"


class IObserved(Interface):
    def add_observer(observer, name=None):
        """Add an observer to this object."""

    def remove_observer(observer):
        """Remove an observer from this object."""

    def notify(action, names=None):
        """Tell observers about this action."""


@implementer(IObserved)
class Observed(object):
    """Inherit from this mixin and call its __init__ to allow the class
    to be observed."""

    def __init__(self) -> None:
        self.observers = {}  # type: Dict[Observer.IObserver, str]

    def add_observer(self, observer, name: str = "") -> None:
        if observer not in self.observers:
            self.observers[observer] = name

    def remove_observer(self, observer) -> None:
        if observer in self.observers:
            del self.observers[observer]

    def notify(
        self, action: Action.Action, names: Optional[List[str]] = None
    ) -> None:
        # Create the list so it can't change size while iterating
        for observer, name in list(self.observers.items()):
            if names is None or not name or name in names:
                observer.update(self, action, names)  # type: ignore
