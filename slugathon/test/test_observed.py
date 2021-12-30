from typing import List, Optional

from zope.interface import implementer

from slugathon.game import Action
from slugathon.util.Observed import IObserved, IObserver, Observed

__copyright__ = "Copyright (c) 2011-2021 David Ripton"
__license__ = "GNU GPL v2"


update_counter = 0


@implementer(IObserver)
class MyObserver:
    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: Optional[List[str]] = None,
    ) -> None:
        global update_counter
        update_counter += 1


class MyObserved(Observed):
    pass


def test_observed() -> None:
    observer = MyObserver()
    observer2 = MyObserver()
    observed = MyObserved()

    action = Action.Action()

    assert update_counter == 0
    observer.update(None, action, None)
    assert update_counter == 1

    assert len(observed.observers) == 0

    observed.add_observer(observer)
    assert len(observed.observers) == 1
    assert observed.observers[observer] == ""  # type: ignore

    observed.remove_observer(observer)
    assert len(observed.observers) == 0

    observed.add_observer(observer, "Alice")
    assert len(observed.observers) == 1
    assert observed.observers[observer] == "Alice"  # type: ignore

    observed.add_observer(observer2, "Bob")
    assert len(observed.observers) == 2
    assert observed.observers[observer2] == "Bob"  # type: ignore

    action = Action.fromstring(
        "MoveLegion {'markerid': 'Rd01', \
'entry_side': 1, 'teleport': False, 'playername': 'player', \
'teleporting_lord': None, 'game_name': 'game', 'hexlabel': 1, \
'previous_hexlabel': 2}"
    )

    observed.notify(action)
    print(update_counter)
    assert update_counter == 3

    observed.notify(action, ["Alice", "Bob"])
    print(update_counter)
    assert update_counter == 5

    observed.notify(action, ["Alice"])
    print(update_counter)
    assert update_counter == 6

    observed.notify(action, ["Sam"])
    print(update_counter)
    assert update_counter == 6
