from zope.interface import implements

from Observer import IObserver
import Action

# TODO Add actions for forming the game and joining the players, to simplify
# loading?

class History(object):
    """Event history tracker, for one game.

    Lacks direct undo or redo methods because we need those operations to
    go through the server.
    """

    implements(IObserver)

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
        self.undone.append(self.actions.pop())

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
        return action.undoable() and action.playername == playername

    def can_redo(self, playername):
        """Return True iff playername can redo an undone action."""
        if not self.undone:
            return False
        action = self.undone[-1]
        return action.playername == playername

    def find_last_split(self, playername, markername1, markername2):
        """Return the last SplitLegion action for playername involving
        markername1 or markername2, or None."""
        for action in reversed(self.actions):
            if (isinstance(action, Action.SplitLegion)
              and action.playername == playername
              and (action.parent_markername in [markername1, markername2]
              or action.child_markername in [markername1, markername2])):
                return action
        return None

    def save(self, fil):
        """Save history to a file, which should already be open for write."""
        for action in self.actions:
            fil.write(repr(action) + "\n")

    def load(self, fil):
        """Load history from a file, which should already be open for read."""
        self.actions = []
        self.undone = []
        for line in fil:
            line = line.strip()
            action = Action.fromstring(line)
            self.actions.append(action)
