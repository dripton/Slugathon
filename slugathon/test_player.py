import time

import Player
import Game

def test_can_exit_split_phase():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markernames) == 12
    player.pick_marker("Rd01")
    assert player.selected_markername == "Rd01"
    player.create_starting_legion()
    assert len(player.legions) == 1
    assert not player.can_exit_split_phase()

    player.split_legion("Rd01", "Rd02", ["Titan", "Ogre", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Centaur", "Gargoyle"])
    assert player.can_exit_split_phase()


def test_friendly_legions():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(100)
    player.assign_color("Red")
    player.pick_marker("Rd01")
    player.create_starting_legion()
    legion1 = player.legions["Rd01"]
    player.split_legion("Rd01", "Rd02", ["Titan", "Ogre", "Ogre", "Gargoyle"],
      ["Angel", "Gargoyle", "Centaur", "Centaur"])
    legion2 = player.legions["Rd02"]
    assert player.friendly_legions() == set([legion1, legion2])
    assert player.friendly_legions(100) == set([legion1, legion2])
    assert player.friendly_legions(200) == set()
    legion1.move(8, False, 1, None)
    assert player.friendly_legions() == set([legion1, legion2])
    assert player.friendly_legions(100) == set([legion2])
    assert player.friendly_legions(8) == set([legion1])
    assert player.friendly_legions(200) == set()
    legion2.move(200, True, 3, "Angel")
    assert player.friendly_legions() == set([legion1, legion2])
    assert player.friendly_legions(100) == set()
    assert player.friendly_legions(8) == set([legion1])
    assert player.friendly_legions(200) == set([legion2])

def test_can_exit_move_phase():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(100)
    player.assign_color("Red")
    player.pick_marker("Rd01")
    player.create_starting_legion()
    legion1 = player.legions["Rd01"]
    player.split_legion("Rd01", "Rd02", ["Titan", "Ogre", "Ogre", "Gargoyle"],
      ["Angel", "Gargoyle", "Centaur", "Centaur"])
    legion2 = player.legions["Rd02"]
    assert not player.can_exit_move_phase(game)
    legion1.move(8, False, 1, None)
    assert player.can_exit_move_phase(game)
    legion2.move(200, True, 3, "Angel")
    assert player.can_exit_move_phase(game)

def test_num_creatures():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player = Player.Player("p0", game, 0)
    player.assign_starting_tower(600)
    player.assign_color("Red")
    assert len(player.markernames) == 12
    player.pick_marker("Rd01")
    assert player.selected_markername == "Rd01"
    player.create_starting_legion()
    assert player.num_creatures() == 8
