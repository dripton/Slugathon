__copyright__ = "Copyright (c) 2005-2010 David Ripton"
__license__ = "GNU GPL v2"


import tempfile
import os
import cStringIO as StringIO

from slugathon.game import History, Action


tmp_path = None


def test_history_1():
    game_name = "game"
    playername = "player"
    parent_markername = "Rd01"
    child_markername = "Rd02"
    parent_creature_names = 4 * [None]
    child_creature_names = 4 * [None]

    history = History.History()
    assert history.actions == []
    assert history.undone == []
    assert not history.can_undo(playername)
    assert not history.can_redo(playername)

    action = Action.SplitLegion(game_name, playername, parent_markername,
      child_markername, parent_creature_names, child_creature_names)
    history.update(None, action)
    assert history.actions == [action]
    assert history.undone == []
    assert history.can_undo(playername)
    assert not history.can_undo("")
    assert not history.can_redo(playername)

    undo_action = Action.UndoSplit(game_name, playername, parent_markername,
      child_markername, parent_creature_names, child_creature_names)
    history.update(None, undo_action)
    assert history.actions == []
    assert history.undone == [action]
    assert not history.can_undo(playername)
    assert history.can_redo(playername)

    history.update(None, action)
    assert history.actions == [action]
    assert history.undone == []
    assert history.can_undo(playername)
    assert not history.can_undo("")
    assert not history.can_redo(playername)


def test_history_2():
    game_name = "game"
    playername = "player"
    parent_markername = "Rd01"
    child_markername = "Rd02"

    history = History.History()
    assert history.actions == []
    assert history.undone == []
    assert not history.can_undo(playername)
    assert not history.can_redo(playername)

    action1 = Action.MoveLegion(game_name, playername, parent_markername,
      1, 1, False, None)
    history.update(None, action1)
    assert history.actions == [action1]
    assert history.undone == []
    assert history.can_undo(playername)
    assert not history.can_undo("")
    assert not history.can_redo(playername)

    action2 = Action.MoveLegion(game_name, playername, child_markername,
      2, 3, False, None)
    history.update(None, action2)
    assert history.actions == [action1, action2]
    assert history.undone == []
    assert history.can_undo(playername)
    assert not history.can_undo("")
    assert not history.can_redo(playername)

    undo_action2 = Action.UndoMoveLegion(game_name, playername,
      child_markername, 2, 3, False, None)
    history.update(None, undo_action2)
    assert history.actions == [action1]
    assert history.undone == [action2]
    assert history.can_undo(playername)
    assert history.can_redo(playername)

    undo_action1 = Action.UndoMoveLegion(game_name, playername,
      parent_markername, 1, 1, False, None)
    history.update(None, undo_action1)
    assert history.actions == []
    assert history.undone == [action2, action1]
    assert not history.can_undo(playername)
    assert history.can_redo(playername)

def test_save():
    game_name = "game"
    playername = "player"
    parent_markername = "Rd01"
    child_markername = "Rd02"

    history = History.History()
    assert history.actions == []
    assert history.undone == []
    assert not history.can_undo(playername)
    assert not history.can_redo(playername)

    action1 = Action.MoveLegion(game_name, playername, parent_markername,
      1, 1, False, None)
    history.update(None, action1)
    assert history.actions == [action1]
    assert history.undone == []
    assert history.can_undo(playername)
    assert not history.can_undo("")
    assert not history.can_redo(playername)

    action2 = Action.MoveLegion(game_name, playername, child_markername,
      2, 3, False, None)
    history.update(None, action2)
    assert history.actions == [action1, action2]

    global tmp_path
    with tempfile.NamedTemporaryFile(prefix="test_history",
      delete=False) as fil:
        tmp_path = fil.name
        history.save(fil)

    with open(tmp_path) as fil:
        lines = fil.readlines()
    assert len(lines) == 2

def test_load():
    history = History.History()
    assert history.actions == []
    assert history.undone == []
    with open(tmp_path) as fil:
        history.load(fil)
    assert len(history.actions) == 2
    for action in history.actions:
        assert isinstance(action, Action.MoveLegion)
    os.remove(tmp_path)

savefile_str = """\
AssignTower {'playername': 'dripton', 'tower_num': 400, 'game_name': 'a'}
AssignTower {'playername': 'tchula', 'tower_num': 500, 'game_name': 'a'}
AssignedAllTowers {'game_name': 'a'}
PickedColor {'playername': 'dripton', 'color': 'Red', 'game_name': 'a'}
PickedColor {'playername': 'tchula', 'color': 'Blue', 'game_name': 'a'}
CreateStartingLegion {'playername': 'tchula', 'markername': 'Bu11', \
'game_name': 'a'}
CreateStartingLegion {'playername': 'dripton', 'markername': 'Rd04', \
'game_name': 'a'}
SplitLegion {'playername': 'tchula', 'child_creature_names': \
('Angel', 'Gargoyle', 'Gargoyle', 'Ogre'), 'game_name': 'a', \
'child_markername': 'Bu06', 'parent_creature_names': \
('Centaur', 'Centaur', 'Ogre', 'Titan'), 'parent_markername': 'Bu11'}
RollMovement {'playername': 'tchula', 'game_name': 'a', 'movement_roll': 5, \
'mulligans_left': 1}
RollMovement {'playername': 'tchula', 'game_name': 'a', 'movement_roll': 6, \
'mulligans_left': 0}
MoveLegion {'markername': 'Bu11', 'entry_side': 1, 'teleport': True, \
'playername': 'tchula', 'teleporting_lord': 'Titan', 'game_name': 'a', \
'hexlabel': 300}
MoveLegion {'markername': 'Bu06', 'entry_side': 1, 'teleport': False, \
'playername': 'tchula', 'teleporting_lord': None, 'game_name': 'a', \
'hexlabel': 36}
StartMusterPhase {'playername': 'tchula', 'game_name': 'a'}
RecruitCreature {'playername': 'tchula', 'markername': 'Bu06', \
'creature_name': 'Ogre', 'game_name': 'a', 'recruiter_names': ['Ogre']}
RecruitCreature {'playername': 'tchula', 'markername': 'Bu11', \
'creature_name': 'Warlock', 'game_name': 'a', 'recruiter_names': ['Titan']}
StartSplitPhase {'playername': 'dripton', 'game_name': 'a', 'turn': 1}
SplitLegion {'playername': 'dripton', 'child_creature_names': \
('Angel', 'Gargoyle', 'Gargoyle', 'Ogre'), 'game_name': 'a', \
'child_markername': 'Rd02', 'parent_creature_names': \
('Centaur', 'Centaur', 'Ogre', 'Titan'), 'parent_markername': 'Rd04'}
RollMovement {'playername': 'dripton', 'game_name': 'a', 'movement_roll': 6, \
'mulligans_left': 1}
MoveLegion {'markername': 'Rd04', 'entry_side': 1, 'teleport': True, \
'playername': 'dripton', 'teleporting_lord': 'Titan', 'game_name': 'a', \
'hexlabel': 200}
MoveLegion {'markername': 'Rd02', 'entry_side': 5, 'teleport': False, \
'playername': 'dripton', 'teleporting_lord': None, 'game_name': 'a', \
'hexlabel': 117}
StartMusterPhase {'playername': 'dripton', 'game_name': 'a'}
RecruitCreature {'playername': 'dripton', 'markername': 'Rd02', \
'creature_name': 'Ogre', 'game_name': 'a', 'recruiter_names': ['Ogre']}
RecruitCreature {'playername': 'dripton', 'markername': 'Rd04', \
'creature_name': 'Warlock', 'game_name': 'a', 'recruiter_names': ['Titan']}
"""

def test_load2():
    history = History.History()
    assert history.actions == []
    assert history.undone == []
    fil = StringIO.StringIO(savefile_str)
    history.load(fil)
    assert len(history.actions) == 23
