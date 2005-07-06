import Player

def test_can_exit_split_phase():
    player = Player.Player("test", "Game1", 0)
    player.assign_color("Red")
    assert len(player.markernames) == 12
    player.pick_marker("Rd01")
    assert player.selected_markername == "Rd01"
    player.create_starting_legion(player.selected_markername)
    assert len(player.legions) == 1
    assert not player.can_exit_split_phase()

    player.split_legion("Rd01", "Rd02", ["Titan", "Ogre", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Centaur", "Gargoyle"])
    assert player.can_exit_split_phase()
