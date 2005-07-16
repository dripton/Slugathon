import time

import Player
import Game

def test_can_exit_split_phase():
    player = Player.Player("test", "Game1", 0)
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
    player = game.players[0]
    player.assign_starting_tower(200)
    game.sort_players()
    game.started = True
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    player.pick_marker("Rd02")
    player.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Centaur", "Gargoyle"],
      ["Angel", "Ogre", "Ogre", "Gargoyle"])
    player.done_with_splits()
    legions = player.friendly_legions(200)
    assert len(legions) == 2
    assert legions == player.legions.values()
    legions = player.friendly_legions()
    assert len(legions) == 2
    assert legions == player.legions.values()
