__copyright__ = "Copyright (c) 2005-2011 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.game import Caretaker


def test_init():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Centaur") == 25
    assert caretaker.num_left("Titan") == 6
    assert caretaker.num_left("Wyvern") == 18


def test_take_one():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Wyvern") == 18
    caretaker.take_one("Wyvern")
    assert caretaker.num_left("Wyvern") == 17


def test_put_one_back():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Angel") == 18
    caretaker.take_one("Angel")
    assert caretaker.num_left("Angel") == 17
    caretaker.put_one_back("Angel")
    assert caretaker.num_left("Angel") == 18
    caretaker.put_one_back("Unknown")
    try:
        caretaker.num_left("Unknown")
    except Exception:
        pass
    else:
        assert False


def test_kill_one():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Angel") == 18
    caretaker.take_one("Angel")
    assert caretaker.num_left("Angel") == 17
    caretaker.kill_one("Angel")
    assert caretaker.num_left("Angel") == 18

    assert caretaker.num_left("Centaur") == 25
    caretaker.take_one("Centaur")
    assert caretaker.num_left("Centaur") == 24
    assert caretaker.graveyard["Centaur"] == 0
    caretaker.kill_one("Centaur")
    assert caretaker.num_left("Centaur") == 24
    assert caretaker.graveyard["Centaur"] == 1


def test_number_in_play():
    caretaker = Caretaker.Caretaker()
    assert caretaker.number_in_play("Centaur") == 0
    caretaker.take_one("Centaur")
    assert caretaker.number_in_play("Centaur") == 1
    caretaker.kill_one("Centaur")
    assert caretaker.number_in_play("Centaur") == 0
    caretaker.take_one("Centaur")
    caretaker.take_one("Centaur")
    caretaker.kill_one("Centaur")
    assert caretaker.number_in_play("Centaur") == 1


def test_take_too_many():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Serpent") == 10
    for unused in range(10):
        caretaker.take_one("Serpent")
    assert caretaker.num_left("Serpent") == 0
    try:
        caretaker.take_one("Serpent")
    except Exception:
        pass
    else:
        assert False, "should have raised"


def test_put_back_too_many():
    caretaker = Caretaker.Caretaker()
    assert caretaker.num_left("Serpent") == 10
    caretaker.put_one_back("Serpent")
    assert caretaker.num_left("Serpent") == 10
