import zope.interface

from Observer import IObserver

class History(object):
    """Event history tracker."""

    def __init__(self):
        self.actions = []

    def update(self, observed, action):
        self.actions.append(action)
