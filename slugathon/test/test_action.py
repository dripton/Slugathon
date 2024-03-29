from slugathon.game import Action

__copyright__ = "Copyright (c) 2008-2012 David Ripton"
__license__ = "GNU GPL v2"


def test_fromstring() -> None:
    obj = Action.fromstring(
        "MoveLegion {'markerid': 'Rd01', \
'entry_side': 1, 'teleport': False, 'playername': 'player', \
'teleporting_lord': None, 'game_name': 'game', 'hexlabel': 1, \
'previous_hexlabel': 2}"
    )
    assert isinstance(obj, Action.MoveLegion)
    assert obj.markerid == "Rd01"
    assert obj.entry_side == 1
    assert obj.teleport is False
    assert obj.playername == "player"
    assert obj.teleporting_lord is None
    assert obj.game_name == "game"
    assert obj.hexlabel == 1
    assert obj.previous_hexlabel == 2


def test_eq() -> None:
    obj1 = Action.fromstring(
        "MoveLegion {'markerid': 'Rd01', \
'entry_side': 1, 'teleport': False, 'playername': 'player', \
'teleporting_lord': None, 'game_name': 'game', 'hexlabel': 1, \
'previous_hexlabel': 2}"
    )
    obj2 = Action.fromstring(
        "MoveLegion {'markerid': 'Rd01', \
'entry_side': 1, 'teleport': False, 'playername': 'player', \
'teleporting_lord': None, 'game_name': 'game', 'hexlabel': 1, \
'previous_hexlabel': 2}"
    )
    assert obj1 == obj2
    obj3 = Action.fromstring(
        "MoveLegion {'markerid': 'Rd01', \
'entry_side': 1, 'teleport': True, 'playername': 'player', \
'teleporting_lord': None, 'game_name': 'game', 'hexlabel': 1, \
'previous_hexlabel': 2}"
    )
    assert obj1 != obj3
