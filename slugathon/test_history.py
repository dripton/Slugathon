import History
import Action

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
    parent_creature_names = 4 * [None]
    child_creature_names = 4 * [None]

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
