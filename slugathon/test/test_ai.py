__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import time

from slugathon.ai import CleverBot
from slugathon.game import Creature, Phase, Game


def test_best7():
    assert CleverBot.best7([]) == set()

    score_moves = [(1, "A1"), (2, "A2"), (3, "A3"), (4, "B1"), (5, "B2")]
    assert CleverBot.best7(score_moves) == set(["A1", "A2", "A3", "B1", "B2"])

    score_moves = [(1, "A1"), (2, "A2"), (3, "A3"), (4, "B1"), (5, "B2"),
      (6, "B3"), (7, "B4"), (8, "C1")]
    assert CleverBot.best7(score_moves) == set(["A2", "A3", "B1", "B2", "B3",
      "B4", "C1"])

    score_moves = [(1, "A1"), (2, "A2"), (2, "C2"), (3, "A3"), (4, "B1"),
      (5, "B2"), (6, "B3"), (7, "B4"), (8, "C1")]
    best_moves = CleverBot.best7(score_moves)
    assert (best_moves == set(["A2", "A3", "B1", "B2", "B3", "B4", "C1"]) or
      best_moves == set(["C2", "A3", "B1", "B2", "B3", "B4", "C1"]))

    score_moves = [(1, "A1"), (2, "A2"), (2, "C2"), (2, "A3"), (4, "B1"),
      (5, "B2"), (6, "B3"), (7, "B4"), (8, "C1")]
    seen = set()
    for trial in xrange(20):
        best_moves = CleverBot.best7(score_moves)
        assert (
          best_moves == set(["A2", "A3", "B1", "B2", "B3", "B4", "C1"]) or
          best_moves == set(["C2", "A3", "B1", "B2", "B3", "B4", "C1"]) or
          best_moves == set(["A2", "C2", "B1", "B2", "B3", "B4", "C1"]))
        for move in best_moves:
            seen.add(move)
    # Make sure we see all the tied moves at some point.
    assert seen == set(["A2", "A3", "C2", "B1", "B2", "B3", "B4", "C1"])


def test_gen_legion_moves():
    cleverbot = CleverBot.CleverBot("player", 1)

    movesets = []
    lm = sorted(cleverbot._gen_legion_moves(movesets))
    assert lm == [[]]

    movesets = [set(["A1", "A2", "A3", "B1"])]
    lm = sorted(cleverbot._gen_legion_moves(movesets))
    assert lm == sorted([
        ["A1"],
        ["A2"],
        ["A3"],
        ["B1"],
    ])

    movesets = [
        set(["A1", "A2", "A3", "B1"]),
        set(["A1", "A2", "A3", "B2"]),
    ]
    lm = sorted(cleverbot._gen_legion_moves(movesets))
    print lm
    assert lm == sorted([
        ["A1", "A2"],
        ["A1", "A3"],
        ["A1", "B2"],
        ["A2", "A1"],
        ["A2", "A3"],
        ["A2", "B2"],
        ["A3", "A1"],
        ["A3", "A2"],
        ["A3", "B2"],
        ["B1", "A1"],
        ["B1", "A2"],
        ["B1", "A3"],
        ["B1", "B2"],
    ])

    movesets = [
        set(["A1", "A2", "A3", "B1"]),
        set(["A1", "A2", "A3", "B2"]),
        set(["A1", "A2", "A3", "B3"]),
    ]
    lm = sorted(cleverbot._gen_legion_moves(movesets))
    print lm
    assert lm == sorted([
        ["A1", "A2", "A3"],
        ["A1", "A2", "B3"],
        ["A1", "A3", "A2"],
        ["A1", "A3", "B3"],
        ["A1", "B2", "A2"],
        ["A1", "B2", "A3"],
        ["A1", "B2", "B3"],
        ["A2", "A1", "A3"],
        ["A2", "A1", "B3"],
        ["A2", "A3", "A1"],
        ["A2", "A3", "B3"],
        ["A2", "B2", "A1"],
        ["A2", "B2", "A3"],
        ["A2", "B2", "B3"],
        ["A3", "A1", "A2"],
        ["A3", "A1", "B3"],
        ["A3", "A2", "A1"],
        ["A3", "A2", "B3"],
        ["A3", "B2", "A1"],
        ["A3", "B2", "A2"],
        ["A3", "B2", "B3"],
        ["B1", "A1", "A2"],
        ["B1", "A1", "A3"],
        ["B1", "A1", "B3"],
        ["B1", "A2", "A1"],
        ["B1", "A2", "A3"],
        ["B1", "A2", "B3"],
        ["B1", "A3", "A1"],
        ["B1", "A3", "A2"],
        ["B1", "A3", "B3"],
        ["B1", "B2", "A1"],
        ["B1", "B2", "A2"],
        ["B1", "B2", "A3"],
        ["B1", "B2", "B3"],
    ])

    movesets = [
        set(['F1', 'F2', 'F3', 'C1', 'E2', 'E1', 'D1']),
        set(['F1', 'F2', 'D1', 'E1', 'E2']),
        set(['F1', 'F2', 'E2', 'E1', 'D1']),
        set(['F1', 'F2', 'D1', 'E1', 'E2']),
        set(['F1', 'F2', 'D1', 'E1', 'E2']),
        set(['F1', 'F2', 'E2', 'E1', 'D1']),
        set(['F1', 'F2', 'D1', 'E1', 'E2']),
    ]
    lm = sorted(cleverbot._gen_legion_moves(movesets))
    assert lm == []


def test_score_legion_move_brush():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p1", "Blue")
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    rd01 = player0.markerid_to_legion["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    bu01 = player1.markerid_to_legion["Bu01"]
    rd01.creatures.append(Creature.Creature("Ranger"))
    rd01.creatures.append(Creature.Creature("Gorgon"))
    bu01.creatures.append(Creature.Creature("Ranger"))
    bu01.creatures.append(Creature.Creature("Gorgon"))
    rd01.move(3, False, None, 5)
    bu01.move(3, False, None, 5)
    game._init_battle(bu01, rd01)
    defender = game.defender_legion
    attacker = game.attacker_legion
    titan1 = defender.sorted_creatures[0]
    gorgon1 = defender.sorted_creatures[1]
    ranger1 = defender.sorted_creatures[2]
    gargoyle1 = defender.sorted_creatures[3]
    centaur1 = defender.sorted_creatures[4]
    assert centaur1.name == "Centaur"
    ogre1 = defender.sorted_creatures[5]
    for creature in defender.creatures:
        creature.legion = defender
    for creature in attacker.creatures:
        creature.legion = attacker
    cleverbot_d = CleverBot.CleverBot("p0", 1)

    hexlabel = ogre1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ogre1)
    for move in moves:
        ogre1.move(move)
        score = cleverbot_d._score_legion_move(game, [ogre1])
        move_to_score[move] = score
    ogre1.move(hexlabel)
    # Should prefer back rank to second rank
    assert move_to_score["E5"] > move_to_score["C5"]
    assert move_to_score["E5"] > move_to_score["E4"]
    # Should prefer non-bramble to bramble
    assert move_to_score["E5"] > move_to_score["F4"]
    # Should prefer second rank plain to back rank bramble
    assert move_to_score["E4"] > move_to_score["F4"]

    hexlabel = gargoyle1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gargoyle1)
    print "ogre1 moves", moves
    for move in moves:
        gargoyle1.move(move)
        score = cleverbot_d._score_legion_move(game, [gargoyle1])
        move_to_score[move] = score
    gargoyle1.move(hexlabel)
    # Should prefer bramble to non-bramble
    assert move_to_score["F4"] > move_to_score["E5"]
    # Should prefer back rank to second rank
    assert move_to_score["E5"] > move_to_score["C5"]
    assert move_to_score["F4"] > move_to_score["D5"]
    # Should prefer second rank to third rank
    assert move_to_score["E4"] > move_to_score["D4"]
    assert move_to_score["D5"] > move_to_score["C4"]

    ranger1.move("C5")
    gorgon1.move("D5")
    ogre1.move("E4")
    titan1.move("D6")
    centaur1.move("E5")
    gargoyle1.move("F4")

    cleverbot_a = CleverBot.CleverBot("p1", 1)
    game.battle_active_legion = attacker
    game.battle_phase = Phase.STRIKE
    titan2 = attacker.sorted_creatures[0]
    gorgon2 = attacker.sorted_creatures[1]
    ranger2 = attacker.sorted_creatures[2]
    gargoyle2 = attacker.sorted_creatures[3]
    centaur2 = attacker.sorted_creatures[4]
    assert centaur2.name == "Centaur"
    ogre2 = attacker.sorted_creatures[5]

    hexlabel = titan2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(titan2)
    for move in moves:
        titan2.move(move)
        score = cleverbot_a._score_legion_move(game, [titan2])
        move_to_score[move] = score
    titan2.move(hexlabel)
    # Should prefer back rank to second rank
    assert move_to_score["A1"] > move_to_score["A2"]
    assert move_to_score["D1"] > move_to_score["D2"]
    # Should prefer non-bramble to bramble
    assert move_to_score["C1"] > move_to_score["D1"]
    # Should prefer second rank to third rank
    assert move_to_score["C2"] > move_to_score["D3"]
    # Should prefer third rank to fourth rank
    assert move_to_score["D3"] > move_to_score["B4"]

    hexlabel = ranger2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ranger2)
    for move in moves:
        ranger2.move(move)
        score = cleverbot_a._score_legion_move(game, [ranger2])
        move_to_score[move] = score
    ranger2.move(hexlabel)
    print move_to_score
    # Should prefer second rank to back rank
    assert move_to_score["A2"] > move_to_score["A1"]
    assert move_to_score["A2"] > move_to_score["B1"]
    assert move_to_score["A2"] > move_to_score["C1"]
    assert move_to_score["C2"] > move_to_score["A1"]
    assert move_to_score["C2"] > move_to_score["B1"]
    assert move_to_score["C2"] > move_to_score["C1"]
    assert move_to_score["E1"] > move_to_score["A1"]
    assert move_to_score["E1"] > move_to_score["B1"]
    assert move_to_score["E1"] > move_to_score["C1"]
    assert move_to_score["D2"] > move_to_score["D1"]
    # Should prefer non-bramble to bramble
    assert move_to_score["A1"] > move_to_score["D1"]
    assert move_to_score["B1"] > move_to_score["D1"]
    assert move_to_score["C1"] > move_to_score["D1"]
    assert move_to_score["C2"] > move_to_score["B2"]
    assert move_to_score["E1"] > move_to_score["B2"]
    assert move_to_score["C2"] > move_to_score["D2"]
    assert move_to_score["E1"] > move_to_score["D2"]
    # Should prefer third rank to second rank (modulo better rangestrike)
    assert move_to_score["C3"] > move_to_score["A2"]
    assert move_to_score["D3"] > move_to_score["A2"]
    assert move_to_score["E2"] > move_to_score["A2"]
    assert move_to_score["E2"] > move_to_score["E1"]
    assert move_to_score["F1"] > move_to_score["A2"]
    # Should prefer better rangestrike opportunity
    assert move_to_score["E2"] > move_to_score["F1"]
    # Should prefer rangestrike to melee
    assert move_to_score["D3"] > move_to_score["B4"]
    assert move_to_score["D3"] > move_to_score["D4"]
    assert move_to_score["F2"] > move_to_score["B4"]
    assert move_to_score["F2"] > move_to_score["D4"]

    hexlabel = gorgon2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gorgon2)
    for move in moves:
        gorgon2.move(move)
        score = cleverbot_a._score_legion_move(game, [gorgon2])
        move_to_score[move] = score
    gorgon2.move(hexlabel)
    # Should prefer second rank to back rank
    assert move_to_score["C2"] > move_to_score["A1"]
    assert move_to_score["E1"] > move_to_score["A1"]
    assert move_to_score["B2"] > move_to_score["D1"]
    assert move_to_score["D2"] > move_to_score["D1"]
    # Should prefer bramble to plain
    assert move_to_score["D1"] > move_to_score["C1"]
    assert move_to_score["D1"] > move_to_score["A1"]
    assert move_to_score["D1"] > move_to_score["B1"]
    assert move_to_score["B2"] > move_to_score["A2"]
    assert move_to_score["B2"] > move_to_score["C2"]
    assert move_to_score["D2"] > move_to_score["A2"]
    assert move_to_score["D2"] > move_to_score["C2"]
    assert move_to_score["D2"] > move_to_score["E1"]
    # Should prefer third rank to second rank
    assert move_to_score["B3"] > move_to_score["C2"]
    assert move_to_score["C3"] > move_to_score["C2"]
    assert move_to_score["D3"] > move_to_score["C2"]
    assert move_to_score["E2"] > move_to_score["C2"]
    assert move_to_score["A3"] > move_to_score["B2"]
    assert move_to_score["A3"] > move_to_score["D2"]
    # Should prefer rangestrike opportunity to none
    assert move_to_score["A3"] > move_to_score["F1"]
    assert move_to_score["B3"] > move_to_score["F1"]
    assert move_to_score["C3"] > move_to_score["F1"]
    assert move_to_score["D3"] > move_to_score["F1"]
    assert move_to_score["E2"] > move_to_score["F1"]
    # Should prefer better rangestrike opportunity
    assert move_to_score["C3"] > move_to_score["B3"]
    assert move_to_score["D3"] > move_to_score["B3"]
    assert move_to_score["E2"] > move_to_score["B3"]

    gorgon2.move("A3")
    ranger2.move("B3")

    hexlabel = centaur2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(centaur2)
    for move in moves:
        centaur2.move(move)
        score = cleverbot_a._score_legion_move(game, [centaur2])
        move_to_score[move] = score
    centaur2.move(hexlabel)
    # Should prefer being next to allies
    assert move_to_score["C3"] > move_to_score["D3"]

    # Avoid 1:2 melee against superior enemies
    assert move_to_score["C3"] > move_to_score["D4"]

    centaur2.move("C3")

    hexlabel = gargoyle2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gargoyle2)
    for move in moves:
        gargoyle2.move(move)
        score = cleverbot_a._score_legion_move(game, [gargoyle2])
        move_to_score[move] = score
    gargoyle2.move(hexlabel)

    gargoyle2.move("D3")

    hexlabel = ogre2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ogre2)
    for move in moves:
        ogre2.move(move)
        score = cleverbot_a._score_legion_move(game, [ogre2])
        move_to_score[move] = score
    ogre2.move(hexlabel)
    # Should prefer being up next to allies
    assert move_to_score["A2"] == max(move_to_score.itervalues())

    ogre2.move("A2")

    hexlabel = titan2.hexlabel
    titan2.moved = False
    move_to_score = {}
    moves = game.find_battle_moves(titan2)
    for move in moves:
        titan2.move(move)
        score = cleverbot_a._score_legion_move(game, [titan2])
        move_to_score[move] = score
    titan2.move(hexlabel)
    # Should prefer hiding in back behind the ogre
    print move_to_score
    assert move_to_score["A1"] == max(move_to_score.itervalues())

    titan2.move("A1")


def test_score_legion_move_plain():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p1", "Blue")
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    rd01 = player0.markerid_to_legion["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    bu01 = player1.markerid_to_legion["Bu01"]
    rd01.creatures.append(Creature.Creature("Ranger"))
    rd01.creatures.append(Creature.Creature("Gorgon"))
    bu01.creatures.append(Creature.Creature("Ranger"))
    bu01.creatures.append(Creature.Creature("Gorgon"))
    rd01.move(101, False, None, 5)
    bu01.move(101, False, None, 5)
    game._init_battle(bu01, rd01)
    defender = game.defender_legion
    attacker = game.attacker_legion
    titan1 = defender.creatures[0]
    ogre1 = defender.creatures[1]
    centaur1 = defender.creatures[2]
    gargoyle1 = defender.creatures[3]
    ranger1 = defender.creatures[4]
    gorgon1 = defender.creatures[5]
    for creature in defender.creatures:
        creature.legion = defender
    for creature in attacker.creatures:
        creature.legion = attacker
    cleverbot_d = CleverBot.CleverBot("p0", 1)

    hexlabel = ogre1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ogre1)
    for move in moves:
        ogre1.move(move)
        score = cleverbot_d._score_legion_move(game, [ogre1])
        move_to_score[move] = score
    ogre1.move(hexlabel)
    # Should prefer back rank to second rank
    assert move_to_score["E5"] > move_to_score["C5"]
    assert move_to_score["E5"] > move_to_score["E4"]

    hexlabel = gargoyle1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gargoyle1)
    print "ogre1 moves", moves
    for move in moves:
        gargoyle1.move(move)
        score = cleverbot_d._score_legion_move(game, [gargoyle1])
        move_to_score[move] = score
    gargoyle1.move(hexlabel)
    # Should prefer back rank to second rank
    assert move_to_score["E5"] > move_to_score["C5"]
    assert move_to_score["F4"] > move_to_score["D5"]
    # Should prefer second rank to third rank
    assert move_to_score["E4"] > move_to_score["D4"]
    assert move_to_score["D5"] > move_to_score["C4"]

    ranger1.move("C5")
    gorgon1.move("D5")
    ogre1.move("E4")
    titan1.move("D6")
    centaur1.move("E5")
    gargoyle1.move("F4")

    cleverbot_a = CleverBot.CleverBot("p1", 1)
    game.battle_active_legion = attacker
    game.battle_phase = Phase.STRIKE
    titan2 = attacker.sorted_creatures[0]
    gorgon2 = attacker.sorted_creatures[1]
    ranger2 = attacker.sorted_creatures[2]
    gargoyle2 = attacker.sorted_creatures[3]
    centaur2 = attacker.sorted_creatures[4]
    ogre2 = attacker.sorted_creatures[5]

    hexlabel = titan2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(titan2)
    for move in moves:
        titan2.move(move)
        score = cleverbot_a._score_legion_move(game, [titan2])
        move_to_score[move] = score
    titan2.move(hexlabel)
    # Should prefer back rank to second rank
    assert move_to_score["A1"] > move_to_score["A2"]
    assert move_to_score["D1"] > move_to_score["D2"]
    # Should prefer second rank to third rank
    assert move_to_score["C2"] > move_to_score["D3"]
    # Should prefer third rank to fourth rank
    assert move_to_score["D3"] > move_to_score["B4"]

    hexlabel = ranger2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ranger2)
    for move in moves:
        ranger2.move(move)
        score = cleverbot_a._score_legion_move(game, [ranger2])
        move_to_score[move] = score
    ranger2.move(hexlabel)
    # Should prefer second rank to back rank
    assert move_to_score["A2"] > move_to_score["A1"]
    assert move_to_score["D2"] > move_to_score["D1"]
    # Should prefer rangestrike to melee
    assert move_to_score["A3"] > move_to_score["B4"]
    assert move_to_score["B3"] > move_to_score["B4"]
    assert move_to_score["C3"] > move_to_score["B4"]
    assert move_to_score["D3"] > move_to_score["B4"]
    assert move_to_score["E2"] > move_to_score["B4"]
    # Should prefer 1-on-1 to 1-on-2
    assert move_to_score["B4"] > move_to_score["C4"]
    assert move_to_score["E3"] > move_to_score["C4"]
    assert move_to_score["E3"] > move_to_score["D4"]
    # Should prefer 1-on-1 with advantage to even 1-on-1.
    assert move_to_score["E3"] > move_to_score["B4"]

    hexlabel = gorgon2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gorgon2)
    for move in moves:
        gorgon2.move(move)
        score = cleverbot_a._score_legion_move(game, [gorgon2])
        move_to_score[move] = score
    gorgon2.move(hexlabel)
    # Should prefer second rank to back rank
    assert move_to_score["D2"] > move_to_score["D1"]
    # Should prefer third rank to second rank
    assert move_to_score["D3"] > move_to_score["C2"]
    # Should prefer rangestrike opportunity to none
    assert move_to_score["A3"] > move_to_score["F1"]
    assert move_to_score["B3"] > move_to_score["F1"]
    assert move_to_score["C3"] > move_to_score["F1"]
    assert move_to_score["D3"] > move_to_score["F1"]
    assert move_to_score["E2"] > move_to_score["F1"]

    gorgon2.move("A3")
    ranger2.move("B3")

    hexlabel = centaur2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(centaur2)
    for move in moves:
        centaur2.move(move)
        score = cleverbot_a._score_legion_move(game, [centaur2])
        move_to_score[move] = score
    centaur2.move(hexlabel)
    # Should prefer being next to allies
    assert move_to_score["C3"] > move_to_score["D3"]

    centaur2.move("C3")

    hexlabel = gargoyle2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(gargoyle2)
    for move in moves:
        gargoyle2.move(move)
        score = cleverbot_a._score_legion_move(game, [gargoyle2])
        move_to_score[move] = score
    gargoyle2.move("D3")

    hexlabel = ogre2.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(ogre2)
    for move in moves:
        ogre2.move(move)
        score = cleverbot_a._score_legion_move(game, [ogre2])
        move_to_score[move] = score
    ogre2.move(hexlabel)
    # Should prefer being up next to allies
    assert move_to_score["A2"] == max(move_to_score.itervalues())

    ogre2.move("A2")

    hexlabel = titan2.hexlabel
    titan2.moved = False
    move_to_score = {}
    moves = game.find_battle_moves(titan2)
    for move in moves:
        titan2.move(move)
        score = cleverbot_a._score_legion_move(game, [titan2])
        move_to_score[move] = score
    titan2.move(hexlabel)
    # Should prefer hiding in back behind the ogre
    print move_to_score
    assert move_to_score["A1"] == max(move_to_score.itervalues())

    titan2.move("A1")


def test_score_legion_move_swamp():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p1", "Blue")
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Ogre", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Centaur", "Gargoyle"])
    rd01 = player0.markerid_to_legion["Rd01"]
    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Gargoyle", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Ogre"])
    bu01 = player1.markerid_to_legion["Bu01"]
    rd01.creatures.append(Creature.Creature("Troll"))
    rd01.creatures.append(Creature.Creature("Troll"))
    rd01.creatures.append(Creature.Creature("Troll"))
    bu01.creatures.remove(Creature.Creature("Centaur"))
    bu01.creatures.append(Creature.Creature("Warlock"))
    bu01.creatures.append(Creature.Creature("Warlock"))
    bu01.creatures.append(Creature.Creature("Cyclops"))
    bu01.creatures.append(Creature.Creature("Cyclops"))
    rd01.move(132, False, None, 1)
    bu01.move(132, False, None, 1)
    game._init_battle(bu01, rd01)
    defender = game.defender_legion
    attacker = game.attacker_legion
    d_titan = defender.creatures[0]
    d_ogre1 = defender.creatures[1]
    d_ogre2 = defender.creatures[2]
    d_gargoyle = defender.creatures[3]
    d_troll1 = defender.creatures[4]
    d_troll2 = defender.creatures[5]
    d_troll3 = defender.creatures[6]
    for creature in defender.creatures:
        creature.legion = defender
    for creature in attacker.creatures:
        creature.legion = attacker
    cleverbot_d = CleverBot.CleverBot("p0", 1)

    hexlabel = d_ogre1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(d_ogre1)
    for move in moves:
        d_ogre1.move(move)
        score = cleverbot_d._score_legion_move(game, [d_ogre1])
        move_to_score[move] = score
    d_ogre1.move(hexlabel)
    # Should prefer back rank to second rank
    for hexlabel1 in ["A1", "A1", "A3"]:
        for hexlabel2 in ["B1", "B2", "B3", "B4"]:
            assert move_to_score[hexlabel1] > move_to_score[hexlabel2]

    hexlabel = d_troll1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(d_troll1)
    for move in moves:
        d_troll1.move(move)
        score = cleverbot_d._score_legion_move(game, [d_troll1])
        move_to_score[move] = score
    d_troll1.move(hexlabel)
    # Should prefer back rank to second rank
    for hexlabel1 in ["A1", "A1", "A3"]:
        for hexlabel2 in ["B1", "B2", "B3", "B4"]:
            assert move_to_score[hexlabel1] > move_to_score[hexlabel2]

    hexlabel = d_gargoyle.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(d_gargoyle)
    for move in moves:
        d_gargoyle.move(move)
        score = cleverbot_d._score_legion_move(game, [d_gargoyle])
        move_to_score[move] = score
    d_gargoyle.move(hexlabel)
    # Should prefer back rank to second rank to third rank
    for hexlabel1 in ["A1", "A1", "A3"]:
        for hexlabel2 in ["B1", "B3", "B4"]:
            for hexlabel3 in ["C1", "C3"]:
                assert (move_to_score[hexlabel1] > move_to_score[hexlabel2] >
                  move_to_score[hexlabel3])

    hexlabel = d_titan.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(d_titan)
    for move in moves:
        d_titan.move(move)
        score = cleverbot_d._score_legion_move(game, [d_titan])
        move_to_score[move] = score
    d_titan.move(hexlabel)
    # Should prefer back rank to second rank to third rank to fourth rank
    for hexlabel1 in ["A1", "A1", "A3"]:
        for hexlabel2 in ["B1", "B3", "B4"]:
            for hexlabel3 in ["C1", "C3"]:
                for hexlabel4 in ["D2", "D4"]:
                    assert (move_to_score[hexlabel1] > move_to_score[hexlabel2]
                      > move_to_score[hexlabel3] > move_to_score[hexlabel4])

    d_troll1.move("B2")
    d_troll2.move("B4")
    d_ogre1.move("B1")
    d_gargoyle.move("B3")
    d_titan.move("A3")
    d_troll3.move("A2")
    d_ogre2.move("A1")

    cleverbot_a = CleverBot.CleverBot("p1", 1)
    game.battle_active_legion = attacker
    game.battle_phase = Phase.STRIKE
    a_titan = attacker.creatures[0]
    a_gargoyle1 = attacker.creatures[1]
    a_gargoyle2 = attacker.creatures[2]
    a_warlock1 = attacker.creatures[3]
    a_warlock2 = attacker.creatures[4]
    a_cyclops1 = attacker.creatures[5]
    a_cyclops2 = attacker.creatures[6]

    hexlabel = a_titan.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(a_titan)
    for move in moves:
        a_titan.move(move)
        score = cleverbot_a._score_legion_move(game, [a_titan])
        move_to_score[move] = score
    a_titan.move(hexlabel)
    # Should prefer back rank to second rank to third rank to fourth rank
    for hexlabel1 in ["F1", "F3", "F4"]:
        for hexlabel2 in ["E1", "E2", "E3", "E5"]:
            for hexlabel3 in ["D2", "D4", "D5", "D6"]:
                for hexlabel4 in ["C1", "C3"]:
                    assert (move_to_score[hexlabel1] > move_to_score[hexlabel2]
                      > move_to_score[hexlabel3] > move_to_score[hexlabel4])

    hexlabel = a_gargoyle1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(a_gargoyle1)
    for move in moves:
        a_gargoyle1.move(move)
        score = cleverbot_a._score_legion_move(game, [a_gargoyle1])
        move_to_score[move] = score
    a_gargoyle1.move(hexlabel)
    # Should prefer third rank to second rank to back rank
    for hexlabel1 in ["F1", "F3", "F4"]:
        for hexlabel2 in ["E1", "E2", "E3", "E5"]:
            for hexlabel3 in ["D2", "D4", "D5", "D6"]:
                assert (move_to_score[hexlabel3] > move_to_score[hexlabel2] >
                  move_to_score[hexlabel1])

    hexlabel = a_cyclops1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(a_cyclops1)
    for move in moves:
        a_cyclops1.move(move)
        score = cleverbot_a._score_legion_move(game, [a_cyclops1])
        move_to_score[move] = score
    a_cyclops1.move(hexlabel)
    # Should prefer third rank to second rank to back rank
    for hexlabel1 in ["F1", "F3", "F4"]:
        for hexlabel2 in ["E1", "E2", "E3", "E5"]:
            assert move_to_score[hexlabel2] > move_to_score[hexlabel1]

    hexlabel = a_warlock1.hexlabel
    move_to_score = {}
    moves = game.find_battle_moves(a_warlock1)
    for move in moves:
        a_warlock1.move(move)
        score = cleverbot_a._score_legion_move(game, [a_warlock1])
        move_to_score[move] = score
    a_warlock1.move(hexlabel)
    # Should prefer third rank to second rank to back rank
    for hexlabel1 in ["F1", "F3", "F4"]:
        for hexlabel2 in ["E1", "E2", "E3", "E5"]:
            assert move_to_score[hexlabel2] > move_to_score[hexlabel1]
    # Should prefer rangestrike to 1:2 melee
    assert move_to_score["D4"] > move_to_score["C3"]
    # Should prefer rangestrike to 1:1 melee
    assert move_to_score["D2"] > move_to_score["C1"]

    a_warlock1.move("C1")
    a_warlock2.move("C3")
    a_gargoyle1.move("D4")
    a_gargoyle2.move("D5")
    a_cyclops1.move("E5")
    a_cyclops2.move("E2")
    a_titan.move("F4")


def test_score_move_scary_pursuer():
    now = time.time()
    game = Game.Game("g1", "p0", now, now, 2, 6)
    game.add_player("p1")
    player0 = game.players[0]
    player1 = game.players[1]
    cleverbot = CleverBot.CleverBot("p1", 5)
    player0.assign_starting_tower(200)
    player1.assign_starting_tower(100)
    game.sort_players()
    game.started = True
    game.assign_color("p1", "Blue")
    game.assign_color("p0", "Red")
    game.assign_first_marker("p0", "Rd01")
    game.assign_first_marker("p1", "Bu01")
    player0.pick_marker("Rd02")
    player0.split_legion("Rd01", "Rd02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    player0.done_with_splits()
    rd01 = player0.markerid_to_legion["Rd01"]

    player1.pick_marker("Bu02")
    player1.split_legion("Bu01", "Bu02",
      ["Titan", "Centaur", "Ogre", "Gargoyle"],
      ["Angel", "Centaur", "Ogre", "Gargoyle"])
    bu01 = player1.markerid_to_legion["Bu01"]
    bu02 = player1.markerid_to_legion["Bu02"]
    player0.done_with_splits()

    bu01.creatures.append(Creature.Creature("Ogre"))
    rd01.creatures.append(Creature.Creature("Colossus"))
    rd01.creatures.append(Creature.Creature("Colossus"))
    rd01.creatures.append(Creature.Creature("Colossus"))

    bu01.hexlabel = 41
    bu02.hexlabel = 400
    rd01.hexlabel = 100
    # We ignore fear on turn 1, so set the turn to 2 to test.
    game.turn = 2

    # staying in 41 gives us range 1
    # moving to 42 gives us range 2
    # moving to 1 gives us range 3
    # moving to 2 gives us range 4
    # moving to 3 gives us range 1
    # moving to 4 gives us range 2
    # moving to 5 gives us range 3

    hexlabel_to_score = {}
    for hexlabel in [41, 42, 1, 2, 3, 4, 5]:
        hexlabel_to_score[hexlabel] = cleverbot._score_move(bu01, hexlabel,
          hexlabel != 41)
    print hexlabel_to_score
    assert hexlabel_to_score[42] > hexlabel_to_score[41]
    assert hexlabel_to_score[42] > hexlabel_to_score[3]
    assert hexlabel_to_score[1] > hexlabel_to_score[42]
    assert hexlabel_to_score[1] > hexlabel_to_score[4]
    assert hexlabel_to_score[2] > hexlabel_to_score[1]
    assert hexlabel_to_score[2] > hexlabel_to_score[5]
    assert hexlabel_to_score[4] > hexlabel_to_score[41]
    assert hexlabel_to_score[4] > hexlabel_to_score[3]
    assert hexlabel_to_score[5] > hexlabel_to_score[42]
    assert hexlabel_to_score[5] > hexlabel_to_score[4]
