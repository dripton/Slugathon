import zope.interface

from Observer import IObserver
import Action

class History(object):
    """Event history tracker, for one game.
    
    Lacks direct undo or redo methods because we need those operations to 
    go through the server.
    """

    zope.interface.implements(IObserver)

    def __init__(self):
        self.actions = []
        self.undone = []

    def _undo(self, undo_action):
        """Undoes the last action performed, if it corresponds to undo_action.

        Otherwise, fails silently.
        """
        if not self.actions:
            return
        prev = self.actions[-1]
        if hash(undo_action) != hash(prev):
            return
        del self.actions[-1]
        self.undone.append(prev)

    def update(self, observed, action):
        """Update history with a new action.
        
        observed is part of the interface, but we don't need it.
        """
        if (isinstance(action, Action.UndoSplit) or
          isinstance(action, Action.UndoMoveLegion) or
          isinstance(action, Action.UndoRecruit)):
            self._undo(action) 
        else:
            self.actions.append(action)
            # Anything but a redo should clear the whole undone list.
            # A redo only removes the last item, regardless of whether it
            # was accomplished using the redo interface, or by repeating 
            # the the last action that was undone.
            if self.undone:
                prev = self.undone.pop()
                if action != prev:
                    self.undone = []

    def can_undo(self, playername):
        """Return True iff the last action is undoable by playername"""
        if not self.actions:
            return False
        action = self.actions[-1]
        if not action.undoable():
            return False
        if action.playername != playername:
            return False
        return True

    def can_redo(self, playername):
        """Return True iff playername can redo an undone action."""
        if not self.undone:
            return False
        action = self.undone[-1]
        if action.playername != playername:
            return False
        return True
