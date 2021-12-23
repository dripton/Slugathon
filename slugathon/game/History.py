import logging
from typing import Any, IO, List, Optional

from zope.interface import implementer

from slugathon.util.Observed import IObserved, IObserver
from slugathon.game import Action


__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


@implementer(IObserver)
class History(object):

    """Event history tracker, for one game.

    Lacks direct undo or redo methods because we need those operations to
    go through the server.
    """

    def __init__(self) -> None:
        self.actions = []  # type: List[Any]
        self.undone = []  # type: List[Any]

    def _undo(self, undo_action: Action.Action) -> None:
        """Undoes the last action performed, if it corresponds to undo_action.

        Otherwise, fails silently.
        """
        if not self.actions:
            return
        prev = self.actions[-1]
        if hash(undo_action) != hash(prev):
            return
        self.undone.append(self.actions.pop())

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        """Update history with a new action.

        observed is part of the interface, but we don't need it.
        """
        if isinstance(action, Action.UndoAction):
            self._undo(action)
        elif isinstance(action, Action.EphemeralAction):
            pass
        else:
            self.actions.append(action)
            # Anything but a redo should clear the whole undone list.
            # A redo only removes the last item, regardless of whether it
            # was accomplished using the redo interface, or by repeating
            # the last action that was undone.
            if self.undone:
                prev = self.undone.pop()
                if action != prev:
                    self.undone = []

    def can_undo(self, playername: str) -> bool:
        """Return True iff the last action is undoable by playername"""
        if not self.actions:
            return False
        action = self.actions[-1]
        logging.debug(action)
        return action.undoable() and action.playername == playername

    def can_redo(self, playername: str) -> bool:
        """Return True iff playername can redo an undone action."""
        if not self.undone:
            return False
        action = self.undone[-1]
        return action.playername == playername

    def find_last_split(
        self, playername: str, markerid1: str, markerid2: str
    ) -> Optional[Action.SplitLegion]:
        """Return the last SplitLegion action for playername involving
        markerid1 or markerid2, or None."""
        for action in reversed(self.actions):
            if (
                isinstance(action, Action.SplitLegion)
                and action.playername == playername
                and (
                    action.parent_markerid in [markerid1, markerid2]
                    or action.child_markerid in [markerid1, markerid2]
                )
            ):
                return action
        return None

    def save(self, fil: IO[str]) -> None:
        """Save history to a file, which should already be open for write."""
        for action in self.actions:
            fil.write(repr(action) + "\n")

    def load(self, fil: IO[str]) -> None:
        """Load history from a file, which should already be open for read."""
        self.actions = []
        self.undone = []
        for line in fil:
            line = line.strip()
            action = Action.fromstring(line)
            self.actions.append(action)
