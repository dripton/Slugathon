__copyright__ = "Copyright (c) 2011 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.ai import CleverBot
from slugathon.game import Creature


def test_gen_legion_moves():
    cleverbot = CleverBot.CleverBot("player")
    titan = Creature.Creature("Titan")
    ogre = Creature.Creature("Ogre")
    troll = Creature.Creature("Troll")

    best_creature_moves = {}
    lm = sorted(cleverbot._gen_legion_moves(best_creature_moves))
    assert lm == [{}]

    best_creature_moves = {titan: ["A1", "A2", "A3", "B1"]}
    lm = sorted(cleverbot._gen_legion_moves(best_creature_moves))
    assert lm == sorted([
        {titan: "A1"},
        {titan: "A2"},
        {titan: "A3"},
        {titan: "B1"},
    ])

    best_creature_moves = {
        titan: ["A1", "A2", "A3", "B1"],
        ogre: ["A1", "A2", "A3", "B2"],
    }
    lm = sorted(cleverbot._gen_legion_moves(best_creature_moves))
    print lm
    assert lm == sorted([
        {titan: "A1", ogre: "A2"},
        {titan: "A1", ogre: "A3"},
        {titan: "A1", ogre: "B2"},
        {titan: "A2", ogre: "A1"},
        {titan: "A2", ogre: "A3"},
        {titan: "A2", ogre: "B2"},
        {titan: "A3", ogre: "A1"},
        {titan: "A3", ogre: "A2"},
        {titan: "A3", ogre: "B2"},
        {titan: "B1", ogre: "A1"},
        {titan: "B1", ogre: "A2"},
        {titan: "B1", ogre: "A3"},
        {titan: "B1", ogre: "B2"},
    ])

    best_creature_moves = {
        titan: ["A1", "A2", "A3", "B1"],
        ogre: ["A1", "A2", "A3", "B2"],
        troll: ["A1", "A2", "A3", "B3"],
    }
    lm = sorted(cleverbot._gen_legion_moves(best_creature_moves))
    print lm
    assert lm == sorted([
        {titan: "A1", ogre: "A2", troll: "A3"},
        {titan: "A1", ogre: "A2", troll: "B3"},
        {titan: "A1", ogre: "A3", troll: "A2"},
        {titan: "A1", ogre: "A3", troll: "B3"},
        {titan: "A1", ogre: "B2", troll: "A2"},
        {titan: "A1", ogre: "B2", troll: "A3"},
        {titan: "A1", ogre: "B2", troll: "B3"},
        {titan: "A2", ogre: "A1", troll: "A3"},
        {titan: "A2", ogre: "A1", troll: "B3"},
        {titan: "A2", ogre: "A3", troll: "A1"},
        {titan: "A2", ogre: "A3", troll: "B3"},
        {titan: "A2", ogre: "B2", troll: "A1"},
        {titan: "A2", ogre: "B2", troll: "A3"},
        {titan: "A2", ogre: "B2", troll: "B3"},
        {titan: "A3", ogre: "A1", troll: "A2"},
        {titan: "A3", ogre: "A1", troll: "B3"},
        {titan: "A3", ogre: "A2", troll: "A1"},
        {titan: "A3", ogre: "A2", troll: "B3"},
        {titan: "A3", ogre: "B2", troll: "A1"},
        {titan: "A3", ogre: "B2", troll: "A2"},
        {titan: "A3", ogre: "B2", troll: "B3"},
        {titan: "B1", ogre: "A1", troll: "A2"},
        {titan: "B1", ogre: "A1", troll: "A3"},
        {titan: "B1", ogre: "A1", troll: "B3"},
        {titan: "B1", ogre: "A2", troll: "A1"},
        {titan: "B1", ogre: "A2", troll: "A3"},
        {titan: "B1", ogre: "A2", troll: "B3"},
        {titan: "B1", ogre: "A3", troll: "A1"},
        {titan: "B1", ogre: "A3", troll: "A2"},
        {titan: "B1", ogre: "A3", troll: "B3"},
        {titan: "B1", ogre: "B2", troll: "A1"},
        {titan: "B1", ogre: "B2", troll: "A2"},
        {titan: "B1", ogre: "B2", troll: "A3"},
        {titan: "B1", ogre: "B2", troll: "B3"},
    ])
