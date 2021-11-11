__copyright__ = "Copyright (c) 2011 David Ripton"
__license__ = "GNU GPL v2"


from zope.interface import implementer

from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed


update_counter = 0


@implementer(IObserver)
class MyObserver():
    def update(self, observed, action, names):
        global update_counter
        update_counter += 1


class MyObserved(Observed):
    pass


def test_observed():
    observer = MyObserver()
    observer2 = MyObserver()
    observed = MyObserved()

    assert update_counter == 0
    observer.update(None, None, None)
    assert update_counter == 1

    assert len(observed.observers) == 0

    observed.add_observer(observer)
    assert len(observed.observers) == 1
    assert observed.observers[observer] == ""

    observed.remove_observer(observer)
    assert len(observed.observers) == 0

    observed.add_observer(observer, "Alice")
    assert len(observed.observers) == 1
    assert observed.observers[observer] == "Alice"

    observed.add_observer(observer2, "Bob")
    assert len(observed.observers) == 2
    assert observed.observers[observer2] == "Bob"

    observed.notify(None)
    print(update_counter)
    assert update_counter == 3

    observed.notify(None, ["Alice", "Bob"])
    print(update_counter)
    assert update_counter == 5

    observed.notify(None, ["Alice"])
    print(update_counter)
    assert update_counter == 6

    observed.notify(None, ["Sam"])
    print(update_counter)
    assert update_counter == 6
