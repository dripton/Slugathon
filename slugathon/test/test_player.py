__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


import time

from slugathon.game import Player, Game, Phase


def test_can_exit_split_phase():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"
    player.create_starting_legion()
    assert len(player.markerid_to_legion) == 1
    assert not player.can_exit_split_phase

    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Centaur", "Gargoyle"],
    )
    assert player.can_exit_split_phase


def test_friendly_legions():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(100)
    player.assign_color("Red")
    player.pick_marker("Rd01")
    player.create_starting_legion()
    legion1 = player.markerid_to_legion["Rd01"]
    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Gargoyle", "Centaur", "Centaur"],
    )
    legion2 = player.markerid_to_legion["Rd02"]
    assert player.friendly_legions() == {legion1, legion2}
    assert player.friendly_legions(100) == {legion1, legion2}
    assert player.friendly_legions(200) == set()
    legion1.move(8, False, None, 1)
    assert player.friendly_legions() == {legion1, legion2}
    assert player.friendly_legions(100) == {legion2}
    assert player.friendly_legions(8) == {legion1}
    assert player.friendly_legions(200) == set()
    legion2.move(200, True, "Angel", 3)
    assert player.friendly_legions() == {legion1, legion2}
    assert player.friendly_legions(100) == set()
    assert player.friendly_legions(8) == {legion1}
    assert player.friendly_legions(200) == {legion2}


def test_can_exit_move_phase():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(100)
    player.assign_color("Red")
    player.pick_marker("Rd01")
    player.create_starting_legion()
    legion1 = player.markerid_to_legion["Rd01"]
    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Gargoyle", "Centaur", "Centaur"],
    )
    legion2 = player.markerid_to_legion["Rd02"]
    assert not player.can_exit_move_phase
    legion1.move(8, False, None, 1)
    assert not player.can_exit_move_phase
    legion2.move(200, True, "Angel", 3)
    game.phase = Phase.MOVE
    assert player.can_exit_move_phase


def test_num_creatures():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"
    player.create_starting_legion()
    assert player.num_creatures == 8


def test_teleported():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"
    player.create_starting_legion()
    assert player.num_creatures == 8
    assert not player.teleported
    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Gargoyle", "Centaur", "Centaur"],
    )
    legion1 = player.markerid_to_legion["Rd01"]
    legion2 = player.markerid_to_legion["Rd02"]
    legion1.move(8, False, None, 1)
    assert not player.teleported
    legion2.move(200, True, "Angel", 3)
    assert player.teleported
    legion2.undo_move()
    assert not player.teleported


def test_pick_marker():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Bu01")
    assert player.selected_markerid is None
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"


def test_take_marker():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    try:
        player.take_marker("Bu01")
    except Exception:
        pass
    else:
        assert False
    player.take_marker("Rd01")
    assert len(player.markerids_left) == 11


def test_create_starting_legion():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    try:
        player.create_starting_legion()
    except Exception:
        pass
    else:
        assert False
    player.selected_markerid = "Bu01"
    try:
        player.create_starting_legion()
    except Exception:
        pass
    else:
        assert False
    player.pick_marker("Rd01")
    player.create_starting_legion()
    player.pick_marker("Rd02")
    try:
        player.create_starting_legion()
    except Exception:
        pass
    else:
        assert False


def test_can_split():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"
    player.create_starting_legion()
    assert player.can_split
    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Centaur", "Gargoyle"],
    )
    assert not player.can_split
    game.turn = 2
    assert player.can_split
    player.split_legion(
        "Rd01", "Rd03", ["Titan", "Gargoyle"], ["Ogre", "Ogre"]
    )
    assert player.can_split
    player.split_legion(
        "Rd02", "Rd04", ["Angel", "Gargoyle"], ["Centaur", "Centaur"]
    )
    assert not player.can_split


def test_sorted_legions():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markerids_left) == 12
    player.pick_marker("Rd01")
    assert player.selected_markerid == "Rd01"
    player.create_starting_legion()
    assert player.can_split
    player.split_legion(
        "Rd01",
        "Rd02",
        ["Titan", "Ogre", "Ogre", "Gargoyle"],
        ["Angel", "Centaur", "Centaur", "Gargoyle"],
    )
    sorted_legions = player.sorted_legions
    assert len(sorted_legions) == 2
    assert sorted_legions[0].has_titan
    assert not sorted_legions[1].has_titan
