__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.data.creaturedata import starting_creature_names
from slugathon.ai.predictsplits import (PredictSplits, CreatureInfo, Node,
                                        AllPredictSplits)


def test_predict_splits1():
    print("\ntest 1 begins")

    ps = PredictSplits("Rd", "Rd01", starting_creature_names)
    ps.print_leaves()

    turn = 1
    print("Turn", turn)
    ps.get_leaf("Rd01").split(4, "Rd02", turn)
    ps.get_leaf("Rd01").merge(ps.get_leaf("Rd02"), turn)
    ps.get_leaf("Rd01").split(4, "Rd02", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Rd01").add_creature("Troll")
    ps.get_leaf("Rd02").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Rd02").add_creature("Lion")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    ps.print_leaves()

    turn = 2
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Gargoyle"])
    ps.get_leaf("Rd01").add_creature("Gargoyle")
    ps.get_leaf("Rd02").reveal_creatures(["Lion"])
    ps.get_leaf("Rd02").add_creature("Lion")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    ps.print_leaves()

    turn = 3
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Titan"])
    ps.get_leaf("Rd01").add_creature("Warlock")
    ps.get_leaf("Rd02").add_creature("Gargoyle")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    ps.print_leaves()

    turn = 4
    print("Turn", turn)
    ps.get_leaf("Rd01").split(2, "Rd03", turn)
    ps.get_leaf("Rd02").split(2, "Rd04", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd01").add_creature("Cyclops")
    ps.get_leaf("Rd02").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd02").add_creature("Cyclops")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd03").all_certain
    assert not ps.get_leaf("Rd04").all_certain
    ps.print_leaves()

    turn = 5
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Warlock"])
    ps.get_leaf("Rd01").add_creature("Warlock")
    ps.get_leaf("Rd02").add_creature("Ogre")
    ps.get_leaf("Rd03").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Rd03").add_creature("Troll")
    ps.get_leaf("Rd04").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Rd04").add_creature("Lion")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    ps.print_leaves()

    turn = 6
    print("Turn", turn)
    ps.get_leaf("Rd02").split(2, "Rd05", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Titan", "Warlock", "Warlock",
                                          "Cyclops", "Troll", "Gargoyle",
                                          "Gargoyle"])
    ps.get_leaf("Rd01").remove_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd02").remove_creature("Angel")
    ps.get_leaf("Rd01").add_creature("Angel")
    ps.get_leaf("Rd02").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Rd02").add_creature("Minotaur")
    ps.get_leaf("Rd04").reveal_creatures(["Lion"])
    ps.get_leaf("Rd04").add_creature("Lion")
    ps.get_leaf("Rd02").reveal_creatures(["Cyclops", "Minotaur", "Lion",
                                          "Lion", "Ogre"])
    ps.get_leaf("Rd02").add_creature("Minotaur")
    ps.get_leaf("Rd02").remove_creatures(["Cyclops", "Minotaur", "Minotaur",
                                          "Lion", "Lion", "Ogre"])
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    ps.print_leaves()

    turn = 7
    print("Turn", turn)
    ps.get_leaf("Rd01").add_creature("Angel")
    ps.get_leaf("Rd03").reveal_creatures(["Troll"])
    ps.get_leaf("Rd03").add_creature("Troll")
    ps.get_leaf("Rd04").reveal_creatures(["Lion"])
    ps.get_leaf("Rd04").add_creature("Lion")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    ps.print_leaves()

    turn = 8
    print("Turn", turn)
    ps.get_leaf("Rd01").split(2, "Rd02", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd01").add_creature("Cyclops")
    ps.get_leaf("Rd05").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd05").add_creature("Cyclops")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    ps.print_leaves()

    turn = 9
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Troll"])
    ps.get_leaf("Rd01").add_creature("Troll")
    ps.get_leaf("Rd03").reveal_creatures(["Troll"])
    ps.get_leaf("Rd03").add_creature("Troll")
    ps.get_leaf("Rd04").reveal_creatures(["Lion", "Lion", "Lion"])
    ps.get_leaf("Rd04").add_creature("Griffon")
    ps.get_leaf("Rd05").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd05").add_creature("Cyclops")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    ps.print_leaves()

    turn = 10
    print("Turn", turn)
    ps.get_leaf("Rd01").split(2, "Rd06", turn)
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    ps.print_leaves()

    turn = 11
    print("Turn", turn)
    ps.get_leaf("Rd04").reveal_creatures(["Griffon", "Lion", "Lion", "Lion",
                                          "Centaur", "Centaur"])
    ps.get_leaf("Rd01").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd01").add_creature("Cyclops")
    ps.get_leaf("Rd03").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd03").add_creature("Ranger")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    ps.print_leaves()

    turn = 12
    print("Turn", turn)
    ps.get_leaf("Rd02").add_creature("Centaur")
    ps.get_leaf("Rd03").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd03").add_creature("Warbear")
    ps.get_leaf("Rd05").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd05").add_creature("Cyclops")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    ps.print_leaves()

    turn = 13
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Titan", "Warlock", "Warlock",
                                          "Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Rd05").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Rd05").add_creature("Behemoth")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    ps.print_leaves()

    turn = 14
    print("Turn", turn)
    ps.get_leaf("Rd04").reveal_creatures(["Griffon", "Lion", "Lion", "Lion",
                                          "Centaur", "Centaur"])
    ps.get_leaf("Rd02").remove_creature("Angel")
    ps.get_leaf("Rd04").add_creature("Angel")
    ps.get_leaf("Rd04").remove_creatures(["Angel", "Lion", "Lion", "Lion",
                                          "Centaur", "Centaur"])
    ps.get_leaf("Rd04").add_creature("Angel")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    assert ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    ps.print_leaves()

    print("test 1 ends")


def test_predict_splits2():
    print("\ntest 2 begins")

    ps = PredictSplits("Rd", "Rd11", starting_creature_names)
    ps.print_leaves()

    turn = 1
    print("Turn", turn)
    ps.get_leaf("Rd11").split(4, "Rd10", turn)
    ps.get_leaf("Rd10").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Rd10").add_creature("Troll")
    ps.get_leaf("Rd11").reveal_creatures(["Gargoyle"])
    ps.get_leaf("Rd11").add_creature("Gargoyle")
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 2
    print("Turn", turn)
    ps.get_leaf("Rd10").reveal_creatures(["Troll"])
    ps.get_leaf("Rd10").add_creature("Troll")
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 3
    print("Turn", turn)
    ps.get_leaf("Rd10").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd10").add_creature("Ranger")
    ps.get_leaf("Rd11").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd11").add_creature("Cyclops")
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 4
    print("Turn", turn)
    ps.get_leaf("Rd10").reveal_creatures(["Titan", "Ranger", "Troll",
                                          "Troll", "Gargoyle", "Ogre", "Ogre"])
    ps.print_leaves()
    ps.get_leaf("Rd10").remove_creature("Gargoyle")
    ps.get_leaf("Rd11").remove_creature("Angel")
    ps.get_leaf("Rd10").add_creature("Angel")
    assert ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 5
    print("Turn", turn)
    ps.get_leaf("Rd10").split(2, "Rd01", turn)
    ps.get_leaf("Rd10").reveal_creatures(["Troll"])
    ps.get_leaf("Rd10").add_creature("Troll")
    ps.get_leaf("Rd01").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Rd01").add_creature("Troll")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 6
    print("Turn", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Troll", "Ogre", "Ogre"])
    ps.get_leaf("Rd01").reveal_creatures(["Troll"])
    ps.get_leaf("Rd01").add_creature("Troll")
    ps.get_leaf("Rd10").reveal_creatures(["Troll", "Troll", "Troll"])
    ps.get_leaf("Rd10").add_creature("Wyvern")
    ps.get_leaf("Rd11").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd11").add_creature("Cyclops")
    assert ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 7
    print("Turn", turn)
    ps.get_leaf("Rd10").split(2, "Rd06", turn)
    ps.get_leaf("Rd11").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Rd11").add_creature("Lion")
    assert ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 8
    print("Turn", turn)
    ps.get_leaf("Rd11").split(2, "Rd07", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Troll", "Troll", "Ogre", "Ogre"])
    ps.get_leaf("Rd10").remove_creature("Angel")
    ps.get_leaf("Rd01").add_creature("Angel")
    ps.get_leaf("Rd01").remove_creatures(["Troll", "Troll", "Ogre", "Ogre"])
    ps.get_leaf("Rd01").add_creature("Angel")
    ps.get_leaf("Rd10").reveal_creatures(["Wyvern"])
    ps.get_leaf("Rd10").add_creature("Wyvern")
    ps.get_leaf("Rd11").reveal_creatures(["Lion"])
    ps.get_leaf("Rd11").add_creature("Lion")
    assert ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 9
    print("Turn", turn)
    ps.get_leaf("Rd07").add_creature("Centaur")
    ps.get_leaf("Rd11").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd11").add_creature("Cyclops")
    assert ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 10
    print("Turn", turn)
    ps.get_leaf("Rd11").split(2, "Rd08", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Angel", "Angel"])
    ps.get_leaf("Rd06").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd06").add_creature("Warbear")
    ps.get_leaf("Rd07").reveal_creatures(["Centaur"])
    ps.get_leaf("Rd07").add_creature("Centaur")
    ps.get_leaf("Rd08").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Rd08").add_creature("Lion")
    ps.get_leaf("Rd10").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd10").add_creature("Ranger")
    ps.get_leaf("Rd11").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Rd11").add_creature("Behemoth")
    ps.get_leaf("Rd01").reveal_creatures(["Angel", "Angel"])
    ps.get_leaf("Rd01").remove_creatures(["Angel", "Angel"])
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd08").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 11
    print("Turn", turn)
    ps.get_leaf("Rd06").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd06").add_creature("Ranger")
    ps.get_leaf("Rd07").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Rd07").add_creature("Lion")
    ps.get_leaf("Rd08").reveal_creatures(["Lion"])
    ps.get_leaf("Rd08").add_creature("Lion")
    ps.get_leaf("Rd10").reveal_creatures(["Titan"])
    ps.get_leaf("Rd10").add_creature("Warlock")
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd08").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 12
    print("Turn", turn)
    ps.get_leaf("Rd10").split(2, "Rd05", turn)
    ps.get_leaf("Rd05").reveal_creatures(["Troll"])
    ps.get_leaf("Rd05").add_creature("Troll")
    ps.get_leaf("Rd06").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd06").add_creature("Warbear")
    ps.get_leaf("Rd07").reveal_creatures(["Lion"])
    ps.get_leaf("Rd07").add_creature("Lion")
    ps.get_leaf("Rd11").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Rd11").add_creature("Ranger")
    assert not ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd08").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 13
    print("Turn", turn)
    ps.get_leaf("Rd11").split(2, "Rd04", turn)
    ps.get_leaf("Rd05").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd05").add_creature("Warbear")
    ps.get_leaf("Rd07").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Rd07").add_creature("Cyclops")
    ps.get_leaf("Rd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd11").add_creature("Ranger")
    ps.get_leaf("Rd08").reveal_creatures(["Lion", "Lion", "Centaur",
                                          "Centaur"])
    ps.get_leaf("Rd08").remove_creatures(["Lion", "Lion", "Centaur",
                                          "Centaur"])
    assert not ps.get_leaf("Rd04").all_certain
    assert not ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 14
    print("Turn", turn)
    ps.get_leaf("Rd06").reveal_creatures(["Warbear", "Warbear", "Ranger",
                                          "Troll", "Troll"])
    ps.get_leaf("Rd04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd04").add_creature("Cyclops")
    ps.get_leaf("Rd06").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd06").add_creature("Ranger")
    ps.get_leaf("Rd10").reveal_creatures(["Wyvern", "Wyvern"])
    ps.get_leaf("Rd10").add_creature("Hydra")
    ps.get_leaf("Rd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd11").add_creature("Ranger")
    assert not ps.get_leaf("Rd04").all_certain
    assert not ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 15
    print("Turn", turn)
    ps.get_leaf("Rd07").split(2, "Rd02", turn)
    ps.get_leaf("Rd11").split(2, "Rd01", turn)
    ps.get_leaf("Rd05").reveal_creatures(["Troll"])
    ps.get_leaf("Rd05").add_creature("Troll")
    ps.get_leaf("Rd06").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd06").add_creature("Ranger")
    ps.get_leaf("Rd11").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Rd11").add_creature("Gorgon")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd04").all_certain
    assert not ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 16
    print("Turn", turn)
    ps.get_leaf("Rd06").reveal_creatures(["Warbear", "Warbear", "Ranger",
                                          "Ranger", "Ranger", "Troll",
                                          "Troll"])
    ps.get_leaf("Rd01").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd01").add_creature("Ranger")
    ps.get_leaf("Rd04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd04").add_creature("Cyclops")
    ps.get_leaf("Rd05").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd05").add_creature("Ranger")
    ps.get_leaf("Rd07").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Rd07").add_creature("Ranger")
    ps.get_leaf("Rd10").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd10").add_creature("Ranger")
    ps.get_leaf("Rd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd11").add_creature("Ranger")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 17
    print("Turn", turn)
    ps.get_leaf("Rd06").split(2, "Rd08", turn)
    ps.get_leaf("Rd11").split(2, "Rd03", turn)
    ps.get_leaf("Rd08").reveal_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd08").remove_creatures(["Troll", "Troll"])
    ps.get_leaf("Rd05").reveal_creatures(["Warbear"])
    ps.get_leaf("Rd05").add_creature("Warbear")
    ps.get_leaf("Rd11").reveal_creatures(["Behemoth"])
    ps.get_leaf("Rd11").add_creature("Behemoth")
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 18
    print("Turn", turn)
    ps.get_leaf("Rd10").split(2, "Rd12", turn)
    ps.get_leaf("Rd01").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd01").add_creature("Ranger")
    ps.get_leaf("Rd11").reveal_creatures(["Gorgon"])
    ps.get_leaf("Rd11").add_creature("Gorgon")
    ps.get_leaf("Rd12").reveal_creatures(["Ranger", "Ranger"])
    ps.get_leaf("Rd12").remove_creatures(["Ranger", "Ranger"])
    assert not ps.get_leaf("Rd01").all_certain
    assert not ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert not ps.get_leaf("Rd07").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 19
    print("Turn", turn)
    ps.get_leaf("Rd11").split(2, "Rd08", turn)
    ps.get_leaf("Rd07").reveal_creatures(["Cyclops", "Ranger", "Lion",
                                          "Lion", "Centaur", "Centaur"])
    ps.get_leaf("Rd07").remove_creatures(["Lion", "Centaur", "Centaur"])
    ps.get_leaf("Rd01").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd01").add_creature("Ranger")
    ps.get_leaf("Rd03").reveal_creatures(["Cyclops"])
    ps.get_leaf("Rd03").add_creature("Cyclops")
    ps.get_leaf("Rd04").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Rd04").add_creature("Gorgon")
    ps.get_leaf("Rd07").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd07").add_creature("Ranger")
    ps.get_leaf("Rd08").reveal_creatures(["Ranger"])
    ps.get_leaf("Rd08").add_creature("Ranger")
    assert not ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd08").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    turn = 20
    print("Turn", turn)
    ps.get_leaf("Rd04").reveal_creatures(["Gorgon", "Cyclops", "Cyclops",
                                          "Cyclops", "Lion"])
    ps.get_leaf("Rd10").reveal_creatures(["Titan", "Hydra", "Wyvern",
                                          "Wyvern", "Warlock"])
    ps.get_leaf("Rd10").add_creature("Angel")
    ps.get_leaf("Rd05").reveal_creatures(["Warbear", "Warbear", "Ranger",
                                          "Ranger", "Troll", "Troll", "Troll"])
    ps.get_leaf("Rd10").remove_creature("Angel")
    ps.get_leaf("Rd05").remove_creature("Troll")
    ps.get_leaf("Rd05").add_creature("Angel")
    ps.get_leaf("Rd05").remove_creatures(["Angel", "Warbear", "Warbear",
                                          "Ranger", "Ranger", "Troll"])
    assert not ps.get_leaf("Rd01").all_certain
    assert ps.get_leaf("Rd02").all_certain
    assert not ps.get_leaf("Rd03").all_certain
    assert ps.get_leaf("Rd04").all_certain
    assert ps.get_leaf("Rd05").all_certain
    assert ps.get_leaf("Rd06").all_certain
    assert ps.get_leaf("Rd07").all_certain
    assert not ps.get_leaf("Rd08").all_certain
    assert ps.get_leaf("Rd10").all_certain
    assert not ps.get_leaf("Rd11").all_certain
    ps.print_leaves()

    print("test 2 ends")


def test_predict_splits3():
    print("\ntest 3 begins")

    ps = PredictSplits("Gr", "Gr07", starting_creature_names)
    ps.print_leaves()

    turn = 1
    print("Turn", turn)
    ps.get_leaf("Gr07").split(4, "Gr11", turn)
    ps.get_leaf("Gr07").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr07").add_creature("Cyclops")
    ps.get_leaf("Gr11").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr11").add_creature("Centaur")
    assert not ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr11").all_certain
    ps.print_leaves()

    turn = 2
    print("Turn", turn)
    ps.get_leaf("Gr07").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr07").add_creature("Cyclops")
    ps.get_leaf("Gr11").reveal_creatures(["Ogre"])
    ps.get_leaf("Gr11").add_creature("Ogre")
    assert not ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr11").all_certain
    ps.print_leaves()

    turn = 3
    print("Turn", turn)
    ps.get_leaf("Gr11").reveal_creatures(["Centaur", "Centaur", "Centaur"])
    ps.get_leaf("Gr11").add_creature("Warbear")
    assert not ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr11").all_certain
    ps.print_leaves()

    print("test 3 ends")


def test_predict_splits4():
    print("\ntest 4 begins")
    creatures = []
    creatures.append(CreatureInfo("Angel", True, True))
    creatures.append(CreatureInfo("Gargoyle", True, True))
    creatures.append(CreatureInfo("Centaur", True, True))
    creatures.append(CreatureInfo("Centaur", False, True))
    creatures.append(CreatureInfo("Centaur", True, False))
    node = Node("Gd10", 1, creatures, None)
    node.reveal_creatures(["Gargoyle", "Gargoyle"])
    print(node)
    assert node.all_certain
    print("test 4 ends")


def test_predict_splits5():
    print("\ntest 5 begins")
    ps = PredictSplits("Gd", "Gd04", starting_creature_names)
    ps.get_leaf("Gd04").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                          "Gargoyle", "Centaur", "Centaur",
                                          "Ogre", "Ogre"])
    ps.print_leaves()
    assert ps.get_leaf("Gd04").all_certain

    turn = 1
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(4, "Gd12", turn)
    ps.get_leaf("Gd12").reveal_creatures(["Titan"])
    ps.get_leaf("Gd04").reveal_creatures(["Centaur"])
    ps.get_leaf("Gd04").add_creature("Centaur")
    ps.get_leaf("Gd12").reveal_creatures(["Titan"])
    ps.get_leaf("Gd12").add_creature("Warlock")
    ps.print_leaves()
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 3

    turn = 2
    ps.get_leaf("Gd04").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gd04").add_creature("Troll")
    ps.get_leaf("Gd12").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gd12").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd04").all_certain
    assert ps.get_leaf("Gd12").all_certain

    turn = 3
    ps.get_leaf("Gd04").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gd04").add_creature("Lion")
    ps.print_leaves()
    assert ps.get_leaf("Gd04").all_certain
    assert ps.get_leaf("Gd12").all_certain

    turn = 4
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd07", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Troll"])
    ps.get_leaf("Gd04").add_creature("Troll")
    ps.print_leaves()
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").all_certain

    turn = 5
    print("\nTurn", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Lion"])
    ps.get_leaf("Gd04").add_creature("Lion")
    ps.get_leaf("Gd12").reveal_creatures(["Centaur"])
    ps.get_leaf("Gd12").add_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").all_certain

    turn = 6
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd08", turn)
    ps.get_leaf("Gd12").split(2, "Gd03", turn)
    ps.get_leaf("Gd08").reveal_creatures(["Ogre"])
    ps.get_leaf("Gd08").add_creature("Ogre")
    ps.get_leaf("Gd12").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gd12").add_creature("Lion")
    ps.get_leaf("Gd07").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gd07").add_creature("Lion")
    ps.get_leaf("Gd12").reveal_creatures(["Lion"])
    ps.get_leaf("Gd12").add_creature("Lion")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 3

    turn = 7
    print("\nTurn", turn)
    ps.get_leaf("Gd12").split(2, "Gd09", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gd03").add_creature("Cyclops")
    ps.get_leaf("Gd07").reveal_creatures(["Lion"])
    ps.get_leaf("Gd07").add_creature("Lion")
    ps.get_leaf("Gd08").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gd08").add_creature("Troll")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 5

    turn = 8
    print("\nTurn", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd04").add_creature("Ranger")
    ps.get_leaf("Gd07").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd07").add_creature("Ranger")
    ps.get_leaf("Gd08").reveal_creatures(["Troll"])
    ps.get_leaf("Gd08").add_creature("Troll")
    ps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd12").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 4

    turn = 10
    print("\nTurn", turn)
    ps.get_leaf("Gd07").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd07").add_creature("Ranger")
    ps.get_leaf("Gd12").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd12").add_creature("Ranger")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 2

    turn = 11
    print("\nTurn", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd03").add_creature("Cyclops")
    ps.get_leaf("Gd07").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd07").add_creature("Ranger")
    ps.get_leaf("Gd09").reveal_creatures(["Centaur"])
    ps.get_leaf("Gd09").add_creature("Centaur")
    ps.get_leaf("Gd08").remove_creature("Troll")
    ps.get_leaf("Gd08").remove_creature("Troll")
    ps.get_leaf("Gd08").remove_creature("Ogre")
    ps.get_leaf("Gd08").remove_creature("Ogre")
    ps.get_leaf("Gd08").remove_creature("Ogre")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08") is None
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 2

    turn = 12
    print("\nTurn", turn)
    ps.get_leaf("Gd07").split(2, "Gd06", turn)
    ps.get_leaf("Gd09").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gd09").add_creature("Lion")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 2

    turn = 13
    print("\nTurn", turn)
    ps.get_leaf("Gd12").split(2, "Gd10", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd03").add_creature("Cyclops")
    ps.get_leaf("Gd04").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd04").add_creature("Ranger")
    ps.get_leaf("Gd12").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gd12").add_creature("Gorgon")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 3

    turn = 14
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd02", turn)
    ps.get_leaf("Gd07").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd07").add_creature("Minotaur")
    ps.get_leaf("Gd09").reveal_creatures(["Centaur", "Centaur", "Centaur"])
    ps.get_leaf("Gd09").add_creature("Warbear")
    ps.get_leaf("Gd10").reveal_creatures(["Lion"])
    ps.get_leaf("Gd10").add_creature("Lion")
    ps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd12").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 5
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 3

    turn = 15
    print("\nTurn", turn)
    ps.get_leaf("Gd12").split(2, "Gd11", turn)
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 5
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 4

    turn = 16
    print("\nTurn", turn)
    ps.get_leaf("Gd07").reveal_creatures(["Ranger", "Ranger", "Ranger",
                                          "Minotaur", "Lion", "Lion"])
    ps.get_leaf("Gd04").remove_creature("Angel")
    ps.get_leaf("Gd07").add_creature("Angel")
    ps.get_leaf("Gd02").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd02").add_creature("Ranger")
    ps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd11").add_creature("Ranger")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 3

    turn = 17
    print("\nTurn", turn)
    ps.get_leaf("Gd07").split(2, "Gd08", turn)
    ps.get_leaf("Gd02").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd02").add_creature("Ranger")
    ps.get_leaf("Gd04").reveal_creatures(["Troll"])
    ps.get_leaf("Gd04").add_creature("Troll")
    ps.get_leaf("Gd09").reveal_creatures(["Lion"])
    ps.get_leaf("Gd09").add_creature("Lion")
    ps.get_leaf("Gd10").reveal_creatures(["Lion", "Lion", "Lion"])
    ps.get_leaf("Gd11").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd11").add_creature("Cyclops")
    ps.get_leaf("Gd07").reveal_creatures(["Angel", "Ranger", "Ranger",
                                          "Ranger", "Minotaur"])
    ps.get_leaf("Gd07").remove_creature("Minotaur")
    ps.get_leaf("Gd07").remove_creature("Angel")
    ps.get_leaf("Gd07").remove_creature("Ranger")
    ps.get_leaf("Gd07").remove_creature("Ranger")
    ps.get_leaf("Gd07").remove_creature("Ranger")
    ps.get_leaf("Gd04").reveal_creatures(["Ranger", "Ranger", "Troll",
                                          "Troll", "Troll"])
    ps.get_leaf("Gd04").remove_creature("Ranger")
    ps.get_leaf("Gd04").remove_creature("Ranger")
    ps.get_leaf("Gd04").remove_creature("Troll")
    ps.get_leaf("Gd04").remove_creature("Troll")
    ps.get_leaf("Gd04").remove_creature("Troll")
    ps.get_leaf("Gd02").reveal_creatures(["Lion"])
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04") is None
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd07") is None
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 18
    print("\nTurn", turn)
    ps.get_leaf("Gd02").add_creature("Lion")
    ps.get_leaf("Gd08").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd08").add_creature("Ranger")
    ps.get_leaf("Gd10").reveal_creatures(["Lion", "Lion"])
    ps.get_leaf("Gd10").add_creature("Ranger")
    ps.get_leaf("Gd06").remove_creature("Centaur")
    ps.get_leaf("Gd06").remove_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd06") is None
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 19
    print("\nTurn", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gd03").add_creature("Gorgon")
    ps.get_leaf("Gd10").reveal_creatures(["Lion"])
    ps.get_leaf("Gd10").add_creature("Lion")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 20
    print("\nTurn", turn)
    ps.get_leaf("Gd02").reveal_creatures(["Lion", "Lion", "Lion"])
    ps.get_leaf("Gd08").reveal_creatures(["Lion"])
    ps.get_leaf("Gd08").add_creature("Lion")
    ps.get_leaf("Gd09").reveal_creatures(["Lion"])
    ps.get_leaf("Gd09").add_creature("Lion")
    ps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd11").add_creature("Troll")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 22
    print("\nTurn", turn)
    ps.get_leaf("Gd09").split(2, "Gd07", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gd03").add_creature("Behemoth")
    ps.get_leaf("Gd08").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd08").add_creature("Troll")
    ps.get_leaf("Gd09").reveal_creatures(["Warbear"])
    ps.get_leaf("Gd09").add_creature("Warbear")
    ps.get_leaf("Gd10").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd10").add_creature("Troll")
    ps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd11").add_creature("Lion")
    ps.get_leaf("Gd12").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gd12").add_creature("Gorgon")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 23
    print("\nTurn", turn)
    ps.get_leaf("Gd03").split(2, "Gd05", turn)
    ps.get_leaf("Gd02").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd02").add_creature("Troll")
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gd03").add_creature("Gorgon")
    ps.get_leaf("Gd07").reveal_creatures(["Centaur"])
    ps.get_leaf("Gd07").add_creature("Centaur")
    ps.get_leaf("Gd08").reveal_creatures(["Lion"])
    ps.get_leaf("Gd08").add_creature("Lion")
    ps.get_leaf("Gd11").reveal_creatures(["Lion"])
    ps.get_leaf("Gd11").add_creature("Lion")
    ps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd12").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd05").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0

    turn = 24
    print("\nTurn", turn)
    ps.get_leaf("Gd02").split(2, "Gd04", turn)
    ps.get_leaf("Gd10").split(2, "Gd06", turn)
    ps.get_leaf("Gd02").reveal_creatures(["Ranger"])
    ps.get_leaf("Gd02").add_creature("Troll")
    ps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gd03").add_creature("Behemoth")
    ps.get_leaf("Gd05").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gd05").add_creature("Cyclops")
    ps.get_leaf("Gd08").reveal_creatures(["Lion"])
    ps.get_leaf("Gd08").add_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gd02").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd05").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd07").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd09").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0
    assert ps.get_leaf("Gd12").num_uncertain_creatures == 0
    print("\ntest 5 ends")


def test_predict_splits6():
    print("\ntest 6 begins")
    ps = PredictSplits("Gr", "Gr11", starting_creature_names)
    ps.print_leaves()

    turn = 1
    print("\nTurn", turn)
    ps.get_leaf("Gr11").split(4, "Gr02", turn)
    ps.get_leaf("Gr02").reveal_creatures(["Titan"])
    ps.get_leaf("Gr02").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr02").add_creature("Cyclops")
    ps.get_leaf("Gr11").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr11").add_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 1

    turn = 2
    print("\nTurn", turn)
    ps.get_leaf("Gr02").reveal_creatures(["Titan"])
    ps.get_leaf("Gr02").add_creature("Warlock")
    ps.get_leaf("Gr11").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr11").add_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 1

    turn = 3
    print("\nTurn", turn)
    ps.get_leaf("Gr02").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr02").add_creature("Cyclops")
    ps.get_leaf("Gr11").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gr11").add_creature("Lion")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 1

    turn = 4
    print("\nTurn", turn)
    ps.get_leaf("Gr02").split(2, "Gr10", turn)
    ps.get_leaf("Gr11").split(3, "Gr03", turn)
    ps.get_leaf("Gr11").merge(ps.get_leaf("Gr03"), turn)
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 5
    assert ps.get_leaf("Gr10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 1

    turn = 5
    print("\nTurn", turn)
    ps.get_leaf("Gr11").split(3, "Gr12", turn)
    ps.get_leaf("Gr02").reveal_creatures(["Warlock"])
    ps.get_leaf("Gr02").add_creature("Warlock")
    ps.get_leaf("Gr10").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr10").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 4
    assert ps.get_leaf("Gr12").num_uncertain_creatures == 3
    ps.get_leaf("Gr12").reveal_creatures(["Centaur", "Centaur", "Centaur"])
    ps.print_leaves()
    ps.get_leaf("Gr12").add_creature("Warbear")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr10").num_uncertain_creatures == 0
    assert ps.get_leaf("Gr11").num_uncertain_creatures == 1
    assert ps.get_leaf("Gr12").num_uncertain_creatures == 0

    ps.get_leaf("Gr10").reveal_creatures(["Cyclops", "Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr10").remove_creature("Cyclops")
    ps.get_leaf("Gr10").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr10").add_creature("Cyclops")
    ps.get_leaf("Gr10").remove_creature("Cyclops")
    ps.get_leaf("Gr10").remove_creature("Gargoyle")
    ps.get_leaf("Gr10").remove_creature("Gargoyle")
    ps.print_leaves()
    assert not ps.get_leaf("Gr02").all_certain
    assert not ps.get_leaf("Gr11").all_certain
    assert ps.get_leaf("Gr12").all_certain

    turn = 6
    print("\nTurn", turn)
    ps.get_leaf("Gr02").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr02").add_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gr02").all_certain
    assert ps.get_leaf("Gr11").all_certain
    assert ps.get_leaf("Gr12").all_certain
    print("\ntest 6 ends")


def test_predict_splits7():
    print("\ntest 7 begins")
    ps = PredictSplits("Gr", "Gr08", starting_creature_names)
    ps.print_leaves()

    turn = 1
    print("Turn", turn)
    ps.get_leaf("Gr08").split(4, "Gr04", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Titan"])
    ps.get_leaf("Gr04").reveal_creatures(["Titan"])
    ps.get_leaf("Gr04").add_creature("Warlock")
    ps.get_leaf("Gr08").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr08").add_creature("Centaur")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 2
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Gargoyle"])
    ps.get_leaf("Gr04").add_creature("Gargoyle")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 3
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 4
    print("Turn", turn)
    ps.get_leaf("Gr04").split(2, "Gr06", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Ogre"])
    ps.get_leaf("Gr04").add_creature("Ogre")
    ps.get_leaf("Gr08").reveal_creatures(["Centaur", "Centaur"])
    ps.get_leaf("Gr08").add_creature("Lion")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 5
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.get_leaf("Gr06").add_creature("Ogre")
    ps.get_leaf("Gr08").reveal_creatures(["Lion"])
    ps.get_leaf("Gr08").add_creature("Lion")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert not ps.get_leaf("Gr08").all_certain
    assert ps.get_leaf("Gr06").num_certain_creatures == 1

    turn = 6
    print("Turn", turn)
    ps.get_leaf("Gr04").split(2, "Gr07", turn)
    ps.get_leaf("Gr08").split(2, "Gr11", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Titan"])
    ps.get_leaf("Gr04").add_creature("Warlock")
    ps.get_leaf("Gr06").reveal_creatures(["Ogre"])
    ps.get_leaf("Gr06").add_creature("Ogre")
    ps.get_leaf("Gr11").remove_creatures(["Centaur", "Centaur"])
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert not ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 7
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.get_leaf("Gr06").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gr06").add_creature("Troll")
    ps.get_leaf("Gr07").reveal_creatures(["Ogre"])
    ps.get_leaf("Gr07").add_creature("Ogre")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert not ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 8
    print("Turn", turn)
    ps.get_leaf("Gr04").split(2, "Gr12", turn)
    ps.print_leaves()

    ps.get_leaf("Gr07").reveal_creatures(["Ogre", "Ogre", "Ogre"])
    ps.get_leaf("Gr07").add_creature("Minotaur")
    ps.get_leaf("Gr08").reveal_creatures(["Gargoyle"])
    ps.get_leaf("Gr08").add_creature("Gargoyle")
    ps.get_leaf("Gr06").remove_creatures(["Troll", "Gargoyle", "Gargoyle",
                                          "Ogre", "Ogre"])
    ps.get_leaf("Gr12").remove_creatures(["Cyclops", "Ogre"])
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain

    turn = 9
    print("Turn", turn)
    ps.get_leaf("Gr08").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gr08").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain

    turn = 11
    print("Turn", turn)
    ps.get_leaf("Gr08").split(2, "Gr01", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Titan"])
    ps.get_leaf("Gr04").add_creature("Warlock")
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr08").add_creature("Cyclops")
    ps.print_leaves()
    assert not ps.get_leaf("Gr01").all_certain
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 12
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.get_leaf("Gr08").reveal_creatures(["Lion"])
    ps.get_leaf("Gr08").add_creature("Lion")
    ps.print_leaves()
    ps.get_leaf("Gr01").remove_creatures(["Gargoyle", "Gargoyle"])
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain

    turn = 13
    print("Turn", turn)
    ps.get_leaf("Gr08").split(2, "Gr02", turn)
    ps.get_leaf("Gr07").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gr07").add_creature("Troll")
    ps.print_leaves()
    assert not ps.get_leaf("Gr02").all_certain
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 14
    print("Turn", turn)
    ps.get_leaf("Gr04").split(2, "Gr06", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.get_leaf("Gr06").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr06").add_creature("Cyclops")
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr08").add_creature("Cyclops")
    ps.print_leaves()
    assert not ps.get_leaf("Gr02").all_certain
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 15
    print("Turn", turn)
    ps.get_leaf("Gr06").remove_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gr02").reveal_creatures(["Centaur"])
    ps.get_leaf("Gr02").add_creature("Centaur")
    ps.print_leaves()
    assert not ps.get_leaf("Gr02").all_certain
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 16
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Cyclops")
    ps.get_leaf("Gr07").reveal_creatures(["Ogre", "Ogre", "Ogre"])
    ps.get_leaf("Gr07").add_creature("Minotaur")
    ps.get_leaf("Gr08").reveal_creatures(["Lion"])
    ps.get_leaf("Gr08").add_creature("Lion")
    ps.print_leaves()
    assert not ps.get_leaf("Gr02").all_certain
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain

    turn = 17
    print("Turn", turn)
    ps.get_leaf("Gr02").remove_creatures(["Lion", "Centaur", "Centaur"])
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain
    ps.get_leaf("Gr08").split(2, "Gr12", turn)
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gr08").add_creature("Gorgon")
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain
    assert not ps.get_leaf("Gr12").all_certain

    turn = 18
    print("Turn", turn)
    ps.get_leaf("Gr12").remove_creatures(["Lion", "Lion"])
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain
    ps.get_leaf("Gr04").split(2, "Gr12", turn)
    ps.get_leaf("Gr07").split(2, "Gr09", turn)
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gr08").add_creature("Gorgon")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain
    assert not ps.get_leaf("Gr09").all_certain
    assert not ps.get_leaf("Gr12").all_certain

    turn = 19
    print("Turn", turn)
    ps.get_leaf("Gr09").remove_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gr08").split(2, "Gr06", turn)
    ps.get_leaf("Gr07").reveal_creatures(["Minotaur", "Minotaur"])
    ps.get_leaf("Gr07").add_creature("Unicorn")
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops", "Cyclops"])
    ps.get_leaf("Gr08").add_creature("Gorgon")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert not ps.get_leaf("Gr06").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert not ps.get_leaf("Gr08").all_certain
    assert not ps.get_leaf("Gr12").all_certain

    turn = 20
    print("Turn", turn)
    ps.get_leaf("Gr06").remove_creatures(["Gorgon", "Lion"])
    ps.get_leaf("Gr08").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gr08").add_creature("Behemoth")
    ps.get_leaf("Gr12").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr12").add_creature("Cyclops")
    ps.print_leaves()
    assert not ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain
    assert not ps.get_leaf("Gr12").all_certain

    turn = 21
    print("Turn", turn)
    ps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gr04").add_creature("Gargoyle")
    ps.get_leaf("Gr12").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gr12").add_creature("Behemoth")
    ps.print_leaves()
    assert ps.get_leaf("Gr04").all_certain
    assert ps.get_leaf("Gr07").all_certain
    assert ps.get_leaf("Gr08").all_certain
    assert ps.get_leaf("Gr12").all_certain
    print("\ntest 7 ends")


def test_predict_splits8():
    print("\ntest 8 begins")
    ps = PredictSplits("Gd", "Gd03", starting_creature_names)

    turn = 1
    print("\nTurn", turn)
    ps.get_leaf("Gd03").split(4, "Gd04", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Ogre"])
    ps.get_leaf("Gd03").add_creature("Ogre")
    ps.get_leaf("Gd04").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gd04").add_creature("Cyclops")
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    ps.print_leaves()

    turn = 2
    print("\nTurn", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Centaur"])
    ps.get_leaf("Gd03").add_creature("Centaur")
    ps.get_leaf("Gd04").reveal_creatures(["Ogre"])
    ps.get_leaf("Gd04").add_creature("Ogre")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 1
    ps.print_leaves()

    turn = 3
    print("\nTurn", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd04").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 1

    turn = 4
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd11", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gd04").add_creature("Troll")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 2

    turn = 5
    print("\nTurn", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd04").add_creature("Cyclops")
    ps.get_leaf("Gd11").reveal_creatures(["Gargoyle", "Gargoyle"])
    ps.get_leaf("Gd11").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 6
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd10", turn)
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 7
    print("\nTurn", turn)
    ps.get_leaf("Gd04").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    ps.get_leaf("Gd04").add_creature("Behemoth")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 8
    print("\nTurn", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Ogre", "Ogre"])
    ps.get_leaf("Gd03").add_creature("Troll")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 9
    print("\nTurn", turn)
    ps.get_leaf("Gd03").split(2, "Gd01", turn)
    ps.print_leaves()
    ps.get_leaf("Gd04").reveal_creatures(["Troll"])
    ps.get_leaf("Gd04").add_creature("Troll")
    ps.get_leaf("Gd03").reveal_creatures(["Troll"])
    ps.get_leaf("Gd03").add_creature("Troll")
    ps.get_leaf("Gd11").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd11").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd01").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    ps.get_leaf("Gd01").remove_creature("Centaur")
    ps.get_leaf("Gd01").remove_creature("Centaur")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 10
    print("\nTurn", turn)
    ps.get_leaf("Gd04").split(2, "Gd08", turn)
    ps.get_leaf("Gd11").reveal_creatures(["Cyclops"])
    ps.get_leaf("Gd11").add_creature("Cyclops")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd10").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    ps.get_leaf("Gd10").remove_creature("Ogre")
    ps.get_leaf("Gd10").remove_creature("Ogre")
    ps.print_leaves()
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0

    turn = 11
    print("\nTurn", turn)
    ps.get_leaf("Gd03").reveal_creatures(["Troll"])
    ps.get_leaf("Gd03").add_creature("Troll")
    ps.print_leaves()
    print("\ntest 8 ends")
    assert ps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert ps.get_leaf("Gd04").num_uncertain_creatures == 4
    assert ps.get_leaf("Gd08").num_uncertain_creatures == 2
    assert ps.get_leaf("Gd11").num_uncertain_creatures == 0


def test_predict_splits9():
    print("\ntest 9 begins")
    aps = AllPredictSplits()
    aps.append(PredictSplits("Gd", "Gd08", starting_creature_names))
    aps.append(PredictSplits("Bu", "Bu02", starting_creature_names))
    aps.append(PredictSplits("Gr", "Gr12", starting_creature_names))
    aps.append(PredictSplits("Br", "Br06", starting_creature_names))
    aps.append(PredictSplits("Bk", "Bk06", starting_creature_names))
    aps.append(PredictSplits("Rd", "Rd06", starting_creature_names))

    aps.check()
    aps.print_leaves()
    turn = 1
    print("\nTurn", turn)
    aps.get_leaf("Gd08").split(4, "Gd03", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gd03").add_creature("Cyclops")
    aps.get_leaf("Gd08").reveal_creatures(["Ogre"])
    aps.get_leaf("Gd08").add_creature("Ogre")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 2
    aps.get_leaf("Bu02").split(4, "Bu05", turn)
    aps.get_leaf("Bu02").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu02").add_creature("Centaur")
    aps.get_leaf("Bu05").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Bu05").add_creature("Cyclops")
    assert aps.get_leaf("Bu02").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu05").num_uncertain_creatures == 2
    aps.get_leaf("Gr12").split(4, "Gr08", turn)
    aps.get_leaf("Gr08").reveal_creatures(["Titan"])
    aps.get_leaf("Gr08").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gr08").add_creature("Troll")
    aps.get_leaf("Gr12").reveal_creatures(["Centaur"])
    aps.get_leaf("Gr12").add_creature("Centaur")
    assert aps.get_leaf("Gr08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    aps.get_leaf("Br06").split(4, "Br01", turn)
    aps.get_leaf("Br01").reveal_creatures(["Titan"])
    aps.get_leaf("Br01").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Br01").add_creature("Cyclops")
    aps.get_leaf("Br06").reveal_creatures(["Centaur"])
    aps.get_leaf("Br06").add_creature("Centaur")
    assert aps.get_leaf("Br01").num_uncertain_creatures == 1
    assert aps.get_leaf("Br06").num_uncertain_creatures == 1
    aps.get_leaf("Bk06").split(4, "Bk10", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Ogre"])
    aps.get_leaf("Bk06").add_creature("Ogre")
    aps.get_leaf("Bk10").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Bk10").add_creature("Cyclops")
    assert aps.get_leaf("Bk06").num_uncertain_creatures == 2
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 2
    aps.get_leaf("Rd06").split(4, "Rd02", turn)
    aps.get_leaf("Rd02").reveal_creatures(["Ogre"])
    aps.get_leaf("Rd02").add_creature("Ogre")
    assert aps.get_leaf("Rd02").num_uncertain_creatures == 3
    assert aps.get_leaf("Rd06").num_uncertain_creatures == 4

    aps.check()
    aps.print_leaves()
    turn = 2
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gd03").add_creature("Cyclops")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 2
    aps.get_leaf("Bu02").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu02").add_creature("Centaur")
    aps.get_leaf("Bu05").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bu05").add_creature("Cyclops")
    assert aps.get_leaf("Bu02").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu05").num_uncertain_creatures == 2
    aps.get_leaf("Gr08").reveal_creatures(["Troll"])
    aps.get_leaf("Gr08").add_creature("Troll")
    aps.get_leaf("Gr12").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Gr12").add_creature("Gargoyle")
    assert aps.get_leaf("Gr08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    aps.get_leaf("Br06").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Br06").add_creature("Lion")
    assert aps.get_leaf("Br01").num_uncertain_creatures == 1
    assert aps.get_leaf("Br06").num_uncertain_creatures == 1
    aps.get_leaf("Bk06").reveal_creatures(["Centaur"])
    aps.get_leaf("Bk06").add_creature("Centaur")
    aps.get_leaf("Bk10").reveal_creatures(["Ogre"])
    aps.get_leaf("Bk10").add_creature("Ogre")
    assert aps.get_leaf("Bk06").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1

    aps.check()
    aps.print_leaves()
    turn = 3
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gd03").add_creature("Cyclops")
    aps.get_leaf("Gd08").reveal_creatures(["Ogre", "Ogre", "Ogre"])
    aps.get_leaf("Gd08").add_creature("Guardian")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    aps.get_leaf("Bu02").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Bu02").add_creature("Troll")
    assert aps.get_leaf("Bu02").num_uncertain_creatures == 1
    assert aps.get_leaf("Bu05").num_uncertain_creatures == 1
    aps.get_leaf("Gr08").reveal_creatures(["Ogre"])
    aps.get_leaf("Gr08").add_creature("Ogre")
    aps.get_leaf("Gr12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gr12").add_creature("Cyclops")
    assert aps.get_leaf("Gr08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    aps.get_leaf("Br06").split(3, "Br12", turn)
    aps.get_leaf("Br01").reveal_creatures(["Cyclops"])
    aps.get_leaf("Br01").add_creature("Cyclops")
    aps.get_leaf("Br06").reveal_creatures(["Lion"])
    aps.get_leaf("Br06").add_creature("Lion")
    assert aps.get_leaf("Br01").num_uncertain_creatures == 1
    assert aps.get_leaf("Br06").num_uncertain_creatures == 2
    assert aps.get_leaf("Br12").num_uncertain_creatures == 3
    aps.get_leaf("Bk06").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bk06").add_creature("Lion")
    aps.get_leaf("Bk10").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bk10").add_creature("Cyclops")
    assert aps.get_leaf("Bk06").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1
    aps.get_leaf("Rd06").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Rd06").add_creature("Gargoyle")
    assert aps.get_leaf("Rd02").num_uncertain_creatures == 3
    assert aps.get_leaf("Rd06").num_uncertain_creatures == 3

    aps.check()
    aps.print_leaves()
    turn = 4
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd12", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Centaur"])
    aps.get_leaf("Gd03").add_creature("Centaur")
    aps.get_leaf("Gd12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gd12").add_creature("Cyclops")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu02").split(2, "Bu08", turn)
    aps.get_leaf("Bu02").merge(aps.get_leaf("Bu08"), turn)
    aps.get_leaf("Bu05").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bu05").add_creature("Cyclops")
    aps.get_leaf("Gr08").split(2, "Gr06", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr06"), turn)
    aps.get_leaf("Gr12").split(2, "Gr09", turn)
    aps.get_leaf("Gr09").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gr09").add_creature("Cyclops")
    aps.get_leaf("Br01").reveal_creatures(["Ogre"])
    aps.get_leaf("Br01").add_creature("Ogre")
    aps.get_leaf("Br12").reveal_creatures(["Centaur", "Centaur", "Centaur"])
    aps.get_leaf("Br12").add_creature("Warbear")
    aps.get_leaf("Bk06").split(2, "Bk04", turn)
    aps.get_leaf("Bk10").split(2, "Bk11", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Centaur"])
    aps.get_leaf("Bk06").add_creature("Centaur")
    aps.get_leaf("Bk11").remove_creature("Gargoyle")
    aps.get_leaf("Bk11").remove_creature("Gargoyle")
    aps.get_leaf("Rd06").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Rd06").add_creature("Cyclops")

    aps.check()
    aps.print_leaves()
    turn = 5
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gd03").add_creature("Lion")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu02").split(2, "Bu01", turn)
    aps.get_leaf("Bu05").split(2, "Bu09", turn)
    aps.get_leaf("Bu09").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Br12").reveal_creatures(["Warbear", "Centaur", "Centaur",
                                           "Centaur"])
    aps.get_leaf("Br12").remove_creature("Centaur")
    aps.get_leaf("Bu09").remove_creature("Gargoyle")
    aps.get_leaf("Bu09").remove_creature("Gargoyle")
    aps.get_leaf("Br12").reveal_creatures(["Warbear", "Centaur", "Centaur"])
    aps.get_leaf("Br12").reveal_creatures(["Warbear"])
    aps.get_leaf("Br12").add_creature("Warbear")
    aps.get_leaf("Bu05").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu05").add_creature("Gorgon")
    aps.get_leaf("Gr08").split(2, "Gr01", turn)
    aps.get_leaf("Gr01").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Gr01").add_creature("Gargoyle")
    aps.get_leaf("Gr09").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr09").add_creature("Cyclops")
    aps.get_leaf("Br01").split(2, "Br11", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br11"), turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Warlock")

    aps.check()
    aps.print_leaves()
    turn = 6
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd06", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Gd06").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gd06").add_creature("Lion")
    aps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gd12").add_creature("Cyclops")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu02").reveal_creatures(["Troll"])
    aps.get_leaf("Bu02").add_creature("Troll")
    aps.get_leaf("Bu05").reveal_creatures(["Titan"])
    aps.get_leaf("Bu05").add_creature("Warlock")
    aps.get_leaf("Gr01").reveal_creatures(["Ogre"])
    aps.get_leaf("Gr01").add_creature("Ogre")
    aps.get_leaf("Gr09").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr09").add_creature("Cyclops")
    aps.get_leaf("Gr12").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gr12").add_creature("Lion")
    aps.get_leaf("Br01").split(2, "Br09", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br09"), turn)
    aps.get_leaf("Br06").reveal_creatures(["Lion"])
    aps.get_leaf("Br06").add_creature("Lion")
    aps.get_leaf("Br12").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk06").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Bk06").add_creature("Troll")
    aps.get_leaf("Bk10").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bk10").add_creature("Cyclops")
    aps.get_leaf("Rd06").reveal_creatures(["Cyclops"])
    aps.get_leaf("Rd06").add_creature("Cyclops")

    aps.check()
    aps.print_leaves()
    turn = 7
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Lion"])
    aps.get_leaf("Gd03").add_creature("Lion")
    aps.get_leaf("Gd08").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gd08").add_creature("Troll")
    aps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gd12").add_creature("Cyclops")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu05").split(2, "Bu12", turn)
    aps.get_leaf("Bu05").reveal_creatures(["Titan"])
    aps.get_leaf("Bu02").reveal_creatures(["Troll"])
    aps.get_leaf("Bu02").add_creature("Troll")
    aps.get_leaf("Bu05").reveal_creatures(["Warlock"])
    aps.get_leaf("Bu05").add_creature("Warlock")
    aps.get_leaf("Gr12").split(3, "Gr02", turn)
    aps.get_leaf("Gr12").merge(aps.get_leaf("Gr02"), turn)
    aps.get_leaf("Gr01").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gr01").add_creature("Cyclops")
    aps.get_leaf("Br01").split(2, "Br08", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br08"), turn)
    aps.get_leaf("Br06").reveal_creatures(["Ogre"])
    aps.get_leaf("Br06").add_creature("Ogre")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk06").split(2, "Bk12", turn)
    aps.get_leaf("Bk04").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bk04").add_creature("Lion")
    aps.get_leaf("Bk06").reveal_creatures(["Lion"])
    aps.get_leaf("Bk06").add_creature("Lion")

    aps.check()
    aps.print_leaves()
    turn = 8
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd04", turn)
    aps.get_leaf("Gd08").split(2, "Gd05", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Gd03").add_creature("Gorgon")
    aps.get_leaf("Gd05").reveal_creatures(["Centaur"])
    aps.get_leaf("Gd05").add_creature("Centaur")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd05").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu02").split(2, "Bu07", turn)
    aps.get_leaf("Bu07").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu07").add_creature("Centaur")
    aps.get_leaf("Gr12").split(3, "Gr03", turn)
    aps.get_leaf("Gr01").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr01").add_creature("Cyclops")
    aps.get_leaf("Br01").split(2, "Br09", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Lion"])
    aps.get_leaf("Bk06").add_creature("Lion")
    aps.get_leaf("Bk12").add_creature("Centaur")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Cyclops", "Cyclops",
                                           "Gargoyle", "Gargoyle",
                                           "Centaur", "Centaur"])
    aps.get_leaf("Gd08").reveal_creatures(["Angel", "Guardian", "Troll",
                                           "Ogre", "Ogre"])
    aps.get_leaf("Gd08").remove_creature("Ogre")
    aps.get_leaf("Rd06").remove_creature("Gargoyle")
    aps.get_leaf("Rd02").remove_creature("Angel")
    aps.get_leaf("Rd06").add_creature("Angel")
    aps.get_leaf("Rd06").remove_creature("Centaur")
    aps.get_leaf("Gd08").remove_creature("Angel")
    aps.get_leaf("Gd08").remove_creature("Troll")
    aps.get_leaf("Rd06").remove_creature("Angel")
    aps.get_leaf("Gd08").remove_creature("Ogre")
    aps.get_leaf("Gd08").remove_creature("Guardian")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Cyclops", "Cyclops",
                                           "Gargoyle", "Centaur"])
    aps.get_leaf("Rd06").add_creature("Angel")

    aps.check()
    aps.print_leaves()
    turn = 9
    print("\nTurn", turn)
    aps.get_leaf("Gd05").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gd05").add_creature("Lion")
    aps.get_leaf("Gd06").reveal_creatures(["Centaur"])
    aps.get_leaf("Gd06").add_creature("Centaur")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd05").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu01").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bu01").add_creature("Lion")
    aps.get_leaf("Bu02").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bu02").add_creature("Guardian")
    aps.get_leaf("Bu05").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bu05").add_creature("Cyclops")
    aps.get_leaf("Bu12").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bu12").add_creature("Cyclops")
    aps.get_leaf("Gr01").split(2, "Gr04", turn)
    aps.get_leaf("Bu01").remove_creature("Lion")
    aps.get_leaf("Bu01").remove_creature("Centaur")
    aps.get_leaf("Bu01").remove_creature("Centaur")
    aps.get_leaf("Gr03").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gr03").add_creature("Lion")
    aps.get_leaf("Gr04").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gr04").add_creature("Cyclops")
    aps.get_leaf("Gr08").reveal_creatures(["Ogre"])
    aps.get_leaf("Gr08").add_creature("Ogre")
    aps.get_leaf("Gr12").reveal_creatures(["Lion"])
    aps.get_leaf("Gr12").add_creature("Lion")
    aps.get_leaf("Br01").reveal_creatures(["Cyclops"])
    aps.get_leaf("Br01").add_creature("Cyclops")
    aps.get_leaf("Bk10").split(2, "Bk11", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Angel", "Troll", "Lion", "Lion",
                                           "Lion", "Ogre", "Ogre"])
    aps.get_leaf("Br06").reveal_creatures(["Angel", "Lion", "Lion", "Lion",
                                           "Ogre", "Ogre"])
    aps.get_leaf("Br06").remove_creature("Lion")
    aps.get_leaf("Br06").remove_creature("Lion")
    aps.get_leaf("Bk06").remove_creature("Angel")
    aps.get_leaf("Br06").remove_creature("Lion")
    aps.get_leaf("Bk06").remove_creature("Ogre")
    aps.get_leaf("Br06").reveal_creatures(["Ogre"])
    aps.get_leaf("Br06").add_creature("Ogre")
    aps.get_leaf("Br06").remove_creature("Angel")
    aps.get_leaf("Bk06").remove_creature("Lion")
    aps.get_leaf("Br06").remove_creature("Ogre")
    aps.get_leaf("Bk06").remove_creature("Lion")
    aps.get_leaf("Br06").remove_creature("Ogre")
    aps.get_leaf("Bk06").remove_creature("Lion")
    aps.get_leaf("Br06").remove_creature("Ogre")
    aps.get_leaf("Bk06").remove_creature("Ogre")
    aps.get_leaf("Bk06").reveal_creatures(["Troll"])
    aps.get_leaf("Bk06").add_creature("Angel")
    aps.get_leaf("Gd05").remove_creature("Lion")
    aps.get_leaf("Gd05").remove_creature("Centaur")
    aps.get_leaf("Gd05").remove_creature("Centaur")
    aps.get_leaf("Gd05").remove_creature("Ogre")
    aps.get_leaf("Bk11").remove_creature("Ogre")
    aps.get_leaf("Bk11").remove_creature("Ogre")
    aps.get_leaf("Rd06").reveal_creatures(["Titan"])
    aps.get_leaf("Rd06").add_creature("Warlock")
    aps.get_leaf("Rd02").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Rd02").add_creature("Gargoyle")

    aps.check()
    aps.print_leaves()
    turn = 10
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Gd03").add_creature("Gorgon")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu05").split(2, "Bu10", turn)
    aps.get_leaf("Rd02").remove_creature("Gargoyle")
    aps.get_leaf("Rd02").remove_creature("Gargoyle")
    aps.get_leaf("Rd02").remove_creature("Ogre")
    aps.get_leaf("Rd02").remove_creature("Ogre")
    aps.get_leaf("Rd02").remove_creature("Ogre")
    aps.get_leaf("Bu07").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bu07").add_creature("Lion")
    aps.get_leaf("Gr01").reveal_creatures(["Ogre"])
    aps.get_leaf("Gr01").add_creature("Ogre")
    aps.get_leaf("Gr03").reveal_creatures(["Lion"])
    aps.get_leaf("Gr03").add_creature("Lion")
    aps.get_leaf("Gr08").reveal_creatures(["Troll"])
    aps.get_leaf("Gr08").add_creature("Troll")
    aps.get_leaf("Br01").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Br01").add_creature("Troll")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Br09").remove_creature("Gargoyle")
    aps.get_leaf("Br09").remove_creature("Gargoyle")
    aps.get_leaf("Bk10").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Bk10").add_creature("Behemoth")
    aps.get_leaf("Bk12").reveal_creatures(["Centaur", "Centaur", "Centaur"])
    aps.get_leaf("Bk12").add_creature("Warbear")
    aps.get_leaf("Rd06").split(2, "Rd09", turn)
    aps.get_leaf("Rd09").reveal_creatures(["Centaur"])
    aps.get_leaf("Rd09").add_creature("Centaur")

    aps.check()
    aps.print_leaves()
    turn = 11
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu02").split(2, "Bu04", turn)
    aps.get_leaf("Bu02").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bu02").add_creature("Ranger")
    aps.get_leaf("Bu05").reveal_creatures(["Warlock"])
    aps.get_leaf("Bu05").add_creature("Warlock")
    aps.get_leaf("Bu07").reveal_creatures(["Lion"])
    aps.get_leaf("Bu07").add_creature("Lion")
    aps.get_leaf("Bu12").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Bu12").add_creature("Guardian")
    aps.get_leaf("Gr08").split(2, "Gr02", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr02"), turn)
    aps.get_leaf("Gr01").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gr01").add_creature("Troll")
    aps.get_leaf("Br01").split(2, "Br03", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br03"), turn)
    aps.get_leaf("Br12").split(2, "Br07", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br07"), turn)
    aps.get_leaf("Gd04").remove_creature("Lion")
    aps.get_leaf("Gd04").remove_creature("Lion")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu04").remove_creature("Troll")
    aps.get_leaf("Bu04").remove_creature("Ogre")
    aps.get_leaf("Bk10").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bk10").add_creature("Gorgon")
    aps.get_leaf("Rd06").reveal_creatures(["Cyclops"])
    aps.get_leaf("Rd06").add_creature("Cyclops")

    aps.check()
    aps.print_leaves()
    turn = 12
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd08", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd08"), turn)
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Bu05").reveal_creatures(["Gorgon"])
    aps.get_leaf("Bu05").add_creature("Gorgon")
    aps.get_leaf("Bu07").reveal_creatures(["Ogre"])
    aps.get_leaf("Bu07").add_creature("Ogre")
    aps.get_leaf("Bu12").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu12").add_creature("Gorgon")
    aps.get_leaf("Gr08").split(2, "Gr10", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr10"), turn)
    aps.get_leaf("Gr01").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr01").add_creature("Cyclops")
    aps.get_leaf("Br01").split(2, "Br02", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br02"), turn)
    aps.get_leaf("Br12").split(2, "Br06", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br06"), turn)
    aps.get_leaf("Gd12").remove_creature("Cyclops")
    aps.get_leaf("Gd12").remove_creature("Cyclops")
    aps.get_leaf("Gd12").remove_creature("Cyclops")
    aps.get_leaf("Gd12").remove_creature("Gargoyle")
    aps.get_leaf("Gd12").remove_creature("Gargoyle")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Behemoth", "Warlock",
                                           "Gorgon", "Cyclops",
                                           "Cyclops", "Cyclops"])
    aps.get_leaf("Bu02").reveal_creatures(["Angel", "Guardian", "Ranger",
                                           "Troll", "Troll"])
    aps.get_leaf("Bk10").remove_creature("Warlock")
    aps.get_leaf("Bu02").remove_creature("Angel")
    aps.get_leaf("Bk10").remove_creature("Behemoth")
    aps.get_leaf("Bu02").remove_creature("Ranger")
    aps.get_leaf("Bk10").remove_creature("Cyclops")
    aps.get_leaf("Bk06").remove_creature("Angel")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bu02").remove_creature("Troll")
    aps.get_leaf("Bu02").remove_creature("Troll")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bu02").remove_creature("Guardian")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Gorgon", "Cyclops",
                                           "Cyclops"])
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bk06").reveal_creatures(["Troll"])
    aps.get_leaf("Bk06").add_creature("Troll")
    aps.get_leaf("Rd06").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Rd06").add_creature("Behemoth")

    aps.check()
    aps.print_leaves()
    turn = 13
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd09", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd09"), turn)
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    aps.get_leaf("Bu05").split(2, "Bu02", turn)
    aps.get_leaf("Bu02").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu02").add_creature("Centaur")
    aps.get_leaf("Bu12").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Bu12").add_creature("Behemoth")
    aps.get_leaf("Gr01").split(2, "Gr07", turn)
    aps.get_leaf("Gr01").merge(aps.get_leaf("Gr07"), turn)
    aps.get_leaf("Gr08").split(2, "Gr05", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr05"), turn)
    aps.get_leaf("Rd09").remove_creature("Gargoyle")
    aps.get_leaf("Rd09").remove_creature("Centaur")
    aps.get_leaf("Rd09").remove_creature("Centaur")
    aps.get_leaf("Br01").split(2, "Br07", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br07"), turn)
    aps.get_leaf("Br12").split(2, "Br04", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br04"), turn)
    aps.get_leaf("Bk12").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bk12").add_creature("Lion")

    aps.check()
    aps.print_leaves()
    turn = 14
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd04", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").add_creature("Warlock")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    aps.get_leaf("Bu05").reveal_creatures(["Warlock"])
    aps.get_leaf("Bu05").add_creature("Warlock")
    aps.get_leaf("Bu07").add_creature("Ogre")
    aps.get_leaf("Bu10").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu10").add_creature("Gorgon")
    aps.get_leaf("Bu12").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu12").add_creature("Gorgon")
    aps.get_leaf("Gr01").split(2, "Gr05", turn)
    aps.get_leaf("Gr08").split(2, "Gr06", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr06"), turn)
    aps.get_leaf("Br01").split(2, "Br05", turn)
    aps.get_leaf("Br12").split(2, "Br04", turn)
    aps.get_leaf("Br01").reveal_creatures(["Cyclops", "Cyclops", "Cyclops"])
    aps.get_leaf("Br01").add_creature("Behemoth")
    aps.get_leaf("Bk06").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk06").add_creature("Ranger")

    aps.check()
    aps.print_leaves()
    turn = 15
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Gorgon"])
    aps.get_leaf("Gd03").add_creature("Gorgon")
    aps.get_leaf("Gd06").reveal_creatures(["Lion"])
    aps.get_leaf("Gd06").add_creature("Lion")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    aps.get_leaf("Bu07").split(2, "Bu09", turn)
    aps.get_leaf("Bu12").split(2, "Bu06", turn)
    aps.get_leaf("Bu12").merge(aps.get_leaf("Bu06"), turn)
    aps.get_leaf("Bu02").add_creature("Gargoyle")
    aps.get_leaf("Bu07").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Bu07").add_creature("Troll")
    aps.get_leaf("Bu09").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bu09").add_creature("Lion")
    aps.get_leaf("Bu10").add_creature("Gargoyle")
    aps.get_leaf("Gr08").split(2, "Gr06", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr06"), turn)
    aps.get_leaf("Gr03").reveal_creatures(["Lion"])
    aps.get_leaf("Gr03").add_creature("Lion")
    aps.get_leaf("Bk12").remove_creature("Warbear")
    aps.get_leaf("Bk12").remove_creature("Lion")
    aps.get_leaf("Bk12").remove_creature("Centaur")
    aps.get_leaf("Bk12").remove_creature("Centaur")
    aps.get_leaf("Bk12").remove_creature("Centaur")
    aps.get_leaf("Br01").add_creature("Angel")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk04").reveal_creatures(["Lion"])
    aps.get_leaf("Bk04").add_creature("Lion")
    aps.get_leaf("Bk06").reveal_creatures(["Troll"])
    aps.get_leaf("Bk06").add_creature("Troll")
    aps.get_leaf("Br05").remove_creature("Ogre")
    aps.get_leaf("Br05").remove_creature("Ogre")

    aps.check()
    aps.print_leaves()
    turn = 16
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd12", turn)
    aps.get_leaf("Gd06").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd06").add_creature("Minotaur")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 5
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 2
    aps.get_leaf("Bu12").split(2, "Bu01", turn)
    aps.get_leaf("Bu12").merge(aps.get_leaf("Bu01"), turn)
    aps.get_leaf("Bu05").reveal_creatures(["Gorgon"])
    aps.get_leaf("Bu05").add_creature("Gorgon")
    aps.get_leaf("Gr08").split(2, "Gr11", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr11"), turn)
    aps.get_leaf("Gr05").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gr05").add_creature("Troll")
    aps.get_leaf("Gr09").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Gr09").add_creature("Gorgon")
    aps.get_leaf("Br01").split(2, "Br03", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br03"), turn)
    aps.get_leaf("Bk04").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Bk04").add_creature("Ranger")
    aps.get_leaf("Bk06").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk06").add_creature("Ranger")
    aps.get_leaf("Bk10").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bk10").add_creature("Gorgon")
    aps.get_leaf("Rd06").split(2, "Rd11", turn)

    aps.check()
    aps.print_leaves()
    turn = 17
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Behemoth"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Gd12").reveal_creatures(["Gorgon"])
    aps.get_leaf("Gd12").add_creature("Gorgon")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 4
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Bu05").split(2, "Bu08", turn)
    aps.get_leaf("Bu12").split(2, "Bu01", turn)
    aps.get_leaf("Bu12").merge(aps.get_leaf("Bu01"), turn)
    aps.get_leaf("Bu09").reveal_creatures(["Lion"])
    aps.get_leaf("Bu09").add_creature("Lion")
    aps.get_leaf("Gr08").split(2, "Gr06", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr06"), turn)
    aps.get_leaf("Gr09").reveal_creatures(["Gorgon", "Cyclops", "Cyclops",
                                           "Cyclops", "Gargoyle", "Gargoyle"])
    aps.get_leaf("Bu07").reveal_creatures(["Troll", "Lion", "Lion", "Ogre",
                                           "Ogre", "Ogre"])
    aps.get_leaf("Bu07").remove_creature("Troll")
    aps.get_leaf("Gr09").remove_creature("Gorgon")
    aps.get_leaf("Gr09").remove_creature("Gargoyle")
    aps.get_leaf("Bu07").remove_creature("Ogre")
    aps.get_leaf("Gr12").remove_creature("Angel")
    aps.get_leaf("Gr09").add_creature("Angel")
    aps.get_leaf("Bu07").remove_creature("Lion")
    aps.get_leaf("Bu07").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Bu07").add_creature("Troll")
    aps.get_leaf("Bu07").remove_creature("Lion")
    aps.get_leaf("Gr09").remove_creature("Cyclops")
    aps.get_leaf("Gr09").remove_creature("Gargoyle")
    aps.get_leaf("Bu07").remove_creature("Ogre")
    aps.get_leaf("Bu07").remove_creature("Ogre")
    aps.get_leaf("Gr09").remove_creature("Cyclops")
    aps.get_leaf("Bu07").remove_creature("Troll")
    aps.get_leaf("Gr09").reveal_creatures(["Angel", "Cyclops"])
    aps.get_leaf("Gr09").add_creature("Angel")
    aps.get_leaf("Br01").split(2, "Br05", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br05"), turn)
    aps.get_leaf("Br04").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Br04").add_creature("Lion")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Angel", "Behemoth",
                                           "Cyclops", "Cyclops"])
    aps.get_leaf("Gr03").reveal_creatures(["Lion", "Lion", "Lion",
                                           "Centaur", "Centaur", "Centaur"])
    aps.get_leaf("Gr03").remove_creature("Centaur")
    aps.get_leaf("Gr03").remove_creature("Centaur")
    aps.get_leaf("Gr03").remove_creature("Lion")
    aps.get_leaf("Gr03").remove_creature("Lion")
    aps.get_leaf("Gr03").remove_creature("Lion")
    aps.get_leaf("Gr03").remove_creature("Centaur")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Angel", "Behemoth",
                                           "Cyclops", "Cyclops"])
    aps.get_leaf("Rd06").add_creature("Angel")
    aps.get_leaf("Rd11").reveal_creatures(["Warlock", "Cyclops"])
    aps.get_leaf("Bu09").reveal_creatures(["Lion", "Lion", "Centaur",
                                           "Centaur"])
    aps.get_leaf("Bu09").remove_creature("Lion")
    aps.get_leaf("Bu09").remove_creature("Centaur")
    aps.get_leaf("Rd11").remove_creature("Cyclops")
    aps.get_leaf("Bu09").reveal_creatures(["Lion"])
    aps.get_leaf("Bu09").add_creature("Lion")
    aps.get_leaf("Rd11").remove_creature("Warlock")
    aps.get_leaf("Bu09").reveal_creatures(["Lion", "Lion", "Centaur"])

    aps.check()
    aps.print_leaves()
    turn = 18
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd10", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd10"), turn)
    aps.get_leaf("Gd04").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Gd04").add_creature("Gorgon")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Bu12").split(2, "Bu04", turn)
    aps.get_leaf("Bu04").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu04").add_creature("Gorgon")
    aps.get_leaf("Gr08").split(2, "Gr06", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr06"), turn)
    aps.get_leaf("Gr01").reveal_creatures(["Troll"])
    aps.get_leaf("Gr01").add_creature("Troll")
    aps.get_leaf("Gr04").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr04").add_creature("Gargoyle")
    aps.get_leaf("Gr05").add_creature("Gargoyle")
    aps.get_leaf("Gr09").add_creature("Gargoyle")
    aps.get_leaf("Br01").split(2, "Br06", turn)
    aps.get_leaf("Br01").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Br01").add_creature("Gorgon")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Angel", "Gorgon",
                                           "Gorgon", "Cyclops", "Cyclops"])
    aps.get_leaf("Gr05").reveal_creatures(["Troll", "Gargoyle", "Ogre",
                                           "Ogre"])
    aps.get_leaf("Gr05").remove_creature("Gargoyle")
    aps.get_leaf("Gr05").remove_creature("Ogre")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Gr05").remove_creature("Troll")
    aps.get_leaf("Bk10").remove_creature("Gorgon")
    aps.get_leaf("Gr05").remove_creature("Ogre")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Gorgon", "Cyclops",
                                           "Cyclops"])
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bk06").reveal_creatures(["Ranger", "Ranger", "Troll",
                                           "Troll", "Troll"])
    aps.get_leaf("Gr12").reveal_creatures(["Cyclops", "Lion", "Lion"])
    aps.get_leaf("Gr12").remove_creature("Cyclops")
    aps.get_leaf("Gr12").remove_creature("Lion")
    aps.get_leaf("Bk06").remove_creature("Ranger")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk06").add_creature("Angel")
    aps.get_leaf("Gr12").remove_creature("Lion")
    aps.get_leaf("Bk06").remove_creature("Ranger")
    aps.get_leaf("Bk06").reveal_creatures(["Angel", "Troll", "Troll",
                                           "Troll"])
    aps.get_leaf("Bk04").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Bk04").add_creature("Ranger")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Angel", "Angel",
                                           "Behemoth", "Cyclops", "Cyclops"])
    aps.get_leaf("Gr04").reveal_creatures(["Cyclops", "Gargoyle", "Gargoyle",
                                           "Gargoyle"])
    aps.get_leaf("Gr04").remove_creature("Gargoyle")
    aps.get_leaf("Gr04").remove_creature("Gargoyle")
    aps.get_leaf("Gr04").remove_creature("Cyclops")
    aps.get_leaf("Gr04").remove_creature("Gargoyle")
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Angel", "Angel",
                                           "Behemoth", "Cyclops", "Cyclops"])
    aps.get_leaf("Rd06").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Rd06").add_creature("Gorgon")

    aps.check()
    aps.print_leaves()
    turn = 19
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd10", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd10"), turn)
    aps.get_leaf("Gd06").reveal_creatures(["Lion"])
    aps.get_leaf("Gd06").add_creature("Lion")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Bu02").reveal_creatures(["Gorgon"])
    aps.get_leaf("Bu02").add_creature("Gorgon")
    aps.get_leaf("Bu12").reveal_creatures(["Guardian"])
    aps.get_leaf("Bu12").add_creature("Guardian")
    aps.get_leaf("Gr08").split(2, "Gr07", turn)
    aps.get_leaf("Gr08").merge(aps.get_leaf("Gr07"), turn)
    aps.get_leaf("Gr01").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Gr01").add_creature("Gorgon")
    aps.get_leaf("Bk06").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bk06").add_creature("Wyvern")

    aps.check()
    aps.print_leaves()
    turn = 20
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd08", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Behemoth", "Behemoth"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd06").reveal_creatures(["Lion", "Lion", "Lion"])
    aps.get_leaf("Gd06").add_creature("Guardian")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Bu02").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bu02").add_creature("Lion")
    aps.get_leaf("Bu10").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu10").add_creature("Gorgon")
    aps.get_leaf("Gr01").split(2, "Gr03", turn)
    aps.get_leaf("Gr01").merge(aps.get_leaf("Gr03"), turn)
    aps.get_leaf("Gr08").split(2, "Gr02", turn)
    aps.get_leaf("Bu08").remove_creature("Gorgon")
    aps.get_leaf("Bu08").remove_creature("Gorgon")
    aps.get_leaf("Br01").reveal_creatures(["Behemoth"])
    aps.get_leaf("Br01").add_creature("Behemoth")
    aps.get_leaf("Br06").reveal_creatures(["Troll"])
    aps.get_leaf("Br06").add_creature("Troll")
    aps.get_leaf("Bk06").reveal_creatures(["Angel", "Wyvern", "Troll",
                                           "Troll", "Troll"])
    aps.get_leaf("Gd04").reveal_creatures(["Gorgon", "Cyclops", "Cyclops"])
    aps.get_leaf("Gd04").remove_creature("Gorgon")
    aps.get_leaf("Bk06").remove_creature("Angel")
    aps.get_leaf("Gd04").remove_creature("Cyclops")
    aps.get_leaf("Bk06").remove_creature("Wyvern")
    aps.get_leaf("Gd04").remove_creature("Cyclops")
    aps.get_leaf("Bk06").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bk06").add_creature("Angel")
    aps.get_leaf("Br04").remove_creature("Lion")
    aps.get_leaf("Br04").remove_creature("Centaur")
    aps.get_leaf("Br04").remove_creature("Centaur")

    aps.check()
    aps.print_leaves()
    turn = 21
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Bu04").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu04").add_creature("Gorgon")
    aps.get_leaf("Bu10").reveal_creatures(["Cyclops", "Cyclops"])
    aps.get_leaf("Bu10").add_creature("Gorgon")
    aps.get_leaf("Gr01").split(2, "Gr05", turn)
    aps.get_leaf("Gr01").reveal_creatures(["Gorgon", "Cyclops", "Cyclops",
                                           "Cyclops", "Troll"])
    aps.get_leaf("Bu05").reveal_creatures(["Titan", "Warlock", "Warlock",
                                           "Warlock", "Warlock"])
    aps.get_leaf("Gr01").remove_creature("Gorgon")
    aps.get_leaf("Bu05").remove_creature("Warlock")
    aps.get_leaf("Gr01").remove_creature("Cyclops")
    aps.get_leaf("Gr09").remove_creature("Angel")
    aps.get_leaf("Gr01").add_creature("Angel")
    aps.get_leaf("Bu05").remove_creature("Warlock")
    aps.get_leaf("Gr01").remove_creature("Angel")
    aps.get_leaf("Gr01").remove_creature("Troll")
    aps.get_leaf("Bu05").remove_creature("Warlock")
    aps.get_leaf("Gr01").remove_creature("Cyclops")
    aps.get_leaf("Gr01").remove_creature("Cyclops")
    aps.get_leaf("Bu05").reveal_creatures(["Titan", "Warlock"])
    aps.get_leaf("Bu05").add_creature("Angel")
    aps.get_leaf("Br01").split(2, "Br10", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br10"), turn)

    aps.check()
    aps.print_leaves()
    turn = 22
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd09", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd09"), turn)
    aps.get_leaf("Gd06").reveal_creatures(["Lion", "Lion", "Lion"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    aps.get_leaf("Gd12").reveal_creatures(["Gorgon"])
    aps.get_leaf("Gd12").add_creature("Gorgon")
    aps.get_leaf("Bu09").remove_creature("Lion")
    aps.get_leaf("Bu09").remove_creature("Lion")
    aps.get_leaf("Bu09").remove_creature("Centaur")
    aps.get_leaf("Br01").split(2, "Br07", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br07"), turn)
    aps.get_leaf("Bk04").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Bk04").add_creature("Ranger")
    aps.get_leaf("Bk06").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk06").add_creature("Warbear")
    aps.get_leaf("Rd06").split(2, "Rd07", turn)
    aps.get_leaf("Rd06").reveal_creatures(["Gorgon"])
    aps.get_leaf("Rd06").add_creature("Gorgon")

    aps.check()
    aps.print_leaves()
    turn = 23
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd05", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd05"), turn)
    aps.get_leaf("Gd06").split(2, "Gd04", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan", "Serpent", "Behemoth",
                                           "Behemoth", "Warlock",
                                           "Gorgon", "Gorgon"])
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 4
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    aps.get_leaf("Rd06").reveal_creatures(["Titan", "Angel", "Behemoth",
                                           "Gorgon", "Gorgon", "Cyclops"])
    aps.get_leaf("Rd06").remove_creature("Angel")
    aps.get_leaf("Rd06").remove_creature("Behemoth")
    aps.get_leaf("Gd03").remove_creature("Gorgon")
    aps.get_leaf("Rd06").remove_creature("Gorgon")
    aps.get_leaf("Rd06").remove_creature("Gorgon")
    aps.get_leaf("Rd06").remove_creature("Cyclops")
    aps.get_leaf("Gd03").remove_creature("Gorgon")
    aps.get_leaf("Gd03").remove_creature("Serpent")
    aps.get_leaf("Rd06").remove_creature("Titan")
    aps.get_leaf("Gd03").remove_creature("Warlock")
    aps.get_leaf("Rd07").remove_creature("Angel")
    aps.get_leaf("Rd07").remove_creature("Cyclops")
    aps.get_leaf("Gd03").reveal_creatures(["Titan", "Behemoth", "Behemoth"])
    aps.get_leaf("Gd03").add_creature("Angel")
    aps.get_leaf("Gd06").reveal_creatures(["Griffon"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.get_leaf("Gd12").reveal_creatures(["Gorgon"])
    aps.get_leaf("Gd12").add_creature("Gorgon")
    aps.get_leaf("Br01").split(2, "Br09", turn)
    aps.get_leaf("Br01").merge(aps.get_leaf("Br09"), turn)
    aps.get_leaf("Bk04").split(2, "Bk01", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Angel", "Warbear", "Troll",
                                           "Troll", "Troll"])
    aps.get_leaf("Gr09").reveal_creatures(["Angel", "Cyclops", "Gargoyle"])
    aps.get_leaf("Gr09").remove_creature("Gargoyle")
    aps.get_leaf("Bk06").remove_creature("Troll")
    aps.get_leaf("Gr09").remove_creature("Angel")
    aps.get_leaf("Gr09").remove_creature("Cyclops")
    aps.get_leaf("Bk06").remove_creature("Angel")
    aps.get_leaf("Bk06").reveal_creatures(["Warbear", "Troll", "Troll"])
    aps.get_leaf("Bk04").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Bk04").add_creature("Minotaur")
    aps.get_leaf("Bu12").reveal_creatures(["Behemoth"])
    aps.get_leaf("Bu12").add_creature("Behemoth")
    aps.get_leaf("Gr05").reveal_creatures(["Troll"])
    aps.get_leaf("Gr05").add_creature("Troll")
    aps.get_leaf("Br01").split(2, "Br07", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Troll"])
    aps.get_leaf("Bk06").add_creature("Troll")

    aps.check()
    aps.print_leaves()
    turn = 24
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Behemoth", "Behemoth"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd06").reveal_creatures(["Guardian"])
    aps.get_leaf("Gd06").add_creature("Guardian")
    aps.get_leaf("Gd12").reveal_creatures(["Gorgon", "Gorgon", "Gorgon"])
    aps.get_leaf("Gd12").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    assert aps.get_leaf("Gd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd06").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd08").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0

    aps.check()
    aps.print_leaves()
    turn = 25
    print("\nTurn", turn)
    aps.get_leaf("Bu12").split(2, "Bu07", turn)
    aps.get_leaf("Gr08").reveal_creatures(["Titan", "Troll", "Troll",
                                           "Troll", "Ogre"])
    aps.get_leaf("Br06").reveal_creatures(["Cyclops", "Troll", "Troll"])
    aps.get_leaf("Gr08").remove_creature("Ogre")
    aps.get_leaf("Br06").remove_creature("Cyclops")
    aps.get_leaf("Gr08").remove_creature("Troll")
    aps.get_leaf("Br06").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Br06").add_creature("Ranger")
    aps.get_leaf("Br06").remove_creature("Troll")
    aps.get_leaf("Gr08").remove_creature("Troll")
    aps.get_leaf("Br06").remove_creature("Ranger")
    aps.get_leaf("Br06").remove_creature("Troll")
    aps.get_leaf("Gr08").reveal_creatures(["Titan", "Troll"])
    aps.get_leaf("Gr08").add_creature("Angel")
    aps.get_leaf("Gr08").reveal_creatures(["Troll"])
    aps.get_leaf("Gr08").add_creature("Troll")
    aps.get_leaf("Bk04").reveal_creatures(["Ranger", "Ranger", "Ranger",
                                           "Minotaur", "Lion", "Lion"])
    aps.get_leaf("Bu05").reveal_creatures(["Titan", "Angel", "Warlock"])
    aps.get_leaf("Bk04").remove_creature("Ranger")
    aps.get_leaf("Bu05").remove_creature("Angel")
    aps.get_leaf("Bu05").remove_creature("Warlock")
    aps.get_leaf("Bk04").remove_creature("Minotaur")
    aps.get_leaf("Bk04").remove_creature("Lion")
    aps.get_leaf("Bk04").remove_creature("Ranger")
    aps.get_leaf("Bk04").remove_creature("Ranger")
    aps.get_leaf("Bu05").remove_creature("Titan")
    aps.get_leaf("Bk04").remove_creature("Lion")
    aps.get_leaf("Bu12").remove_creature("Guardian")
    aps.get_leaf("Bu12").remove_creature("Guardian")
    aps.get_leaf("Bu12").remove_creature("Behemoth")
    aps.get_leaf("Bu12").remove_creature("Behemoth")
    aps.get_leaf("Bu12").remove_creature("Gorgon")
    aps.get_leaf("Bu10").remove_creature("Gorgon")
    aps.get_leaf("Bu10").remove_creature("Gorgon")
    aps.get_leaf("Bu10").remove_creature("Cyclops")
    aps.get_leaf("Bu10").remove_creature("Cyclops")
    aps.get_leaf("Bu10").remove_creature("Gargoyle")
    aps.get_leaf("Bu10").remove_creature("Gorgon")
    aps.get_leaf("Bu02").remove_creature("Gorgon")
    aps.get_leaf("Bu02").remove_creature("Gorgon")
    aps.get_leaf("Bu02").remove_creature("Gargoyle")
    aps.get_leaf("Bu02").remove_creature("Centaur")
    aps.get_leaf("Bu02").remove_creature("Centaur")
    aps.get_leaf("Bu02").remove_creature("Lion")
    aps.get_leaf("Bu04").remove_creature("Gorgon")
    aps.get_leaf("Bu04").remove_creature("Cyclops")
    aps.get_leaf("Bu04").remove_creature("Cyclops")
    aps.get_leaf("Bu04").remove_creature("Gorgon")
    aps.get_leaf("Bu07").remove_creature("Gorgon")
    aps.get_leaf("Bu07").remove_creature("Cyclops")
    aps.get_leaf("Bk06").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bk06").add_creature("Wyvern")

    aps.check()
    aps.print_leaves()
    turn = 26
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd11", turn)
    aps.get_leaf("Gd06").reveal_creatures(["Minotaur"])
    aps.get_leaf("Gd06").add_creature("Minotaur")
    aps.get_leaf("Gd11").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Warlock", "Gorgon",
                                           "Cyclops", "Cyclops"])
    aps.get_leaf("Gr08").reveal_creatures(["Titan", "Angel", "Troll",
                                           "Troll"])
    aps.get_leaf("Bk10").remove_creature("Gorgon")
    aps.get_leaf("Gr08").remove_creature("Troll")
    aps.get_leaf("Gr08").remove_creature("Troll")
    aps.get_leaf("Bk10").remove_creature("Warlock")
    aps.get_leaf("Bk10").remove_creature("Cyclops")
    aps.get_leaf("Bk10").remove_creature("Cyclops")
    aps.get_leaf("Gr08").remove_creature("Titan")
    aps.get_leaf("Gr08").remove_creature("Angel")
    aps.get_leaf("Gr02").remove_creature("Ogre")
    aps.get_leaf("Gr02").remove_creature("Ogre")
    aps.get_leaf("Gr05").remove_creature("Troll")
    aps.get_leaf("Gr05").remove_creature("Ogre")
    aps.get_leaf("Gr05").remove_creature("Troll")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Br01").reveal_creatures(["Behemoth", "Behemoth"])
    aps.get_leaf("Br01").add_creature("Serpent")
    aps.get_leaf("Br12").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Br12").add_creature("Unicorn")

    aps.check()
    aps.print_leaves()
    turn = 28
    print("\nTurn", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd11").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Br12").split(2, "Br04", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk06").add_creature("Warbear")
    aps.get_leaf("Gd06").reveal_creatures(["Griffon", "Griffon"])
    aps.get_leaf("Gd06").add_creature("Hydra")

    aps.check()
    aps.print_leaves()
    turn = 30
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd10", turn)
    aps.get_leaf("Gd11").reveal_creatures(["Ranger", "Ranger", "Ranger"])
    aps.get_leaf("Gd11").add_creature("Guardian")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn", "Unicorn", "Unicorn"])
    aps.get_leaf("Br12").add_creature("Guardian")
    aps.get_leaf("Br07").remove_creature("Cyclops")
    aps.get_leaf("Br07").remove_creature("Cyclops")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Gd08").remove_creature("Centaur")
    aps.get_leaf("Gd08").remove_creature("Centaur")
    aps.get_leaf("Bk06").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk06").add_creature("Wyvern")

    aps.check()
    aps.print_leaves()
    turn = 31
    print("\nTurn", turn)
    aps.get_leaf("Gd06").reveal_creatures(["Minotaur", "Minotaur"])
    aps.get_leaf("Gd06").add_creature("Unicorn")
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Bk06").split(2, "Bk02", turn)
    aps.get_leaf("Gd04").remove_creature("Lion")
    aps.get_leaf("Gd04").remove_creature("Centaur")
    aps.get_leaf("Bk06").reveal_creatures(["Troll"])
    aps.get_leaf("Bk06").add_creature("Troll")

    aps.check()
    aps.print_leaves()
    turn = 32
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd01", turn)
    aps.get_leaf("Gd11").split(2, "Gd05", turn)
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Br04").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Br04").add_creature("Unicorn")
    aps.get_leaf("Bk02").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk02").add_creature("Ranger")
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd05").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd05").add_creature("Ranger")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Hydra")
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Br04").remove_creature("Unicorn")
    aps.get_leaf("Br04").remove_creature("Warbear")
    aps.get_leaf("Br04").remove_creature("Warbear")
    aps.get_leaf("Bk06").reveal_creatures(["Wyvern", "Wyvern"])
    aps.get_leaf("Bk06").add_creature("Hydra")
    aps.check()
    aps.print_leaves()
    turn = 34
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd11").split(2, "Gd02", turn)
    aps.get_leaf("Gd02").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd02").add_creature("Ranger")
    aps.get_leaf("Gd05").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd05").add_creature("Ranger")
    aps.get_leaf("Gd10").reveal_creatures(["Griffon", "Griffon"])
    aps.get_leaf("Gd10").add_creature("Hydra")
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Ranger")
    aps.get_leaf("Br12").split(2, "Br04", turn)
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Serpent")
    aps.get_leaf("Bk06").split(2, "Bk05", turn)
    aps.get_leaf("Gd02").remove_creature("Ranger")
    aps.get_leaf("Gd02").remove_creature("Ranger")
    aps.get_leaf("Gd02").remove_creature("Ranger")
    aps.get_leaf("Bk02").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk02").add_creature("Troll")
    aps.get_leaf("Bk05").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk05").add_creature("Ranger")
    aps.get_leaf("Gd11").reveal_creatures(["Guardian"])
    aps.get_leaf("Gd11").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 35
    print("\nTurn", turn)
    aps.get_leaf("Br01").split(2, "Br07", turn)
    aps.get_leaf("Gd10").remove_creature("Hydra")
    aps.get_leaf("Gd10").remove_creature("Griffon")
    aps.get_leaf("Gd10").remove_creature("Griffon")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bk02").reveal_creatures(["Ranger", "Troll", "Troll",
                                           "Troll"])
    aps.get_leaf("Gd07").reveal_creatures(["Behemoth", "Behemoth"])
    aps.get_leaf("Bk02").remove_creature("Ranger")
    aps.get_leaf("Gd07").remove_creature("Behemoth")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk02").add_creature("Angel")
    aps.get_leaf("Gd07").remove_creature("Behemoth")
    aps.get_leaf("Bk02").remove_creature("Troll")
    aps.get_leaf("Bk02").reveal_creatures(["Angel", "Troll", "Troll"])
    aps.get_leaf("Bk05").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk05").add_creature("Troll")
    aps.check()
    aps.print_leaves()
    turn = 36
    print("\nTurn", turn)
    aps.get_leaf("Gd11").split(2, "Gd08", turn)
    aps.get_leaf("Gd11").merge(aps.get_leaf("Gd08"), turn)
    aps.get_leaf("Gd05").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd05").add_creature("Ranger")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk05").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk05").add_creature("Ranger")
    aps.check()
    aps.print_leaves()
    turn = 37
    print("\nTurn", turn)
    aps.get_leaf("Gd11").split(2, "Gd08", turn)
    aps.get_leaf("Gd05").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd05").add_creature("Ranger")
    aps.get_leaf("Br04").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br04").add_creature("Unicorn")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Unicorn")
    aps.get_leaf("Bk02").reveal_creatures(["Troll"])
    aps.get_leaf("Bk02").add_creature("Troll")
    aps.get_leaf("Bk06").reveal_creatures(["Hydra"])
    aps.get_leaf("Bk06").add_creature("Hydra")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Hydra")
    aps.get_leaf("Gd08").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd08").add_creature("Ranger")
    aps.check()
    aps.print_leaves()
    turn = 38
    print("\nTurn", turn)
    aps.get_leaf("Br12").split(2, "Br09", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br09"), turn)
    aps.get_leaf("Bk05").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk05").add_creature("Ranger")
    aps.check()
    aps.print_leaves()
    turn = 39
    print("\nTurn", turn)
    aps.get_leaf("Br12").split(2, "Br06", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br06"), turn)
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Serpent")
    aps.get_leaf("Bk02").reveal_creatures(["Angel", "Troll", "Troll",
                                           "Troll"])
    aps.get_leaf("Br07").reveal_creatures(["Behemoth", "Behemoth"])
    aps.get_leaf("Br07").remove_creature("Behemoth")
    aps.get_leaf("Bk02").remove_creature("Angel")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk02").add_creature("Angel")
    aps.get_leaf("Bk02").remove_creature("Troll")
    aps.get_leaf("Br07").remove_creature("Behemoth")
    aps.get_leaf("Bk02").reveal_creatures(["Angel", "Troll", "Troll"])
    aps.get_leaf("Bk02").add_creature("Archangel")
    aps.get_leaf("Bk05").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk05").add_creature("Ranger")
    aps.get_leaf("Bk06").reveal_creatures(["Wyvern", "Wyvern"])
    aps.get_leaf("Bk06").add_creature("Hydra")
    aps.get_leaf("Gd05").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd05").add_creature("Ranger")
    aps.check()
    aps.print_leaves()
    turn = 40
    print("\nTurn", turn)
    aps.get_leaf("Br12").split(2, "Br05", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br05"), turn)
    aps.get_leaf("Bk05").split(2, "Bk03", turn)
    aps.get_leaf("Br04").remove_creature("Guardian")
    aps.get_leaf("Br04").remove_creature("Unicorn")
    aps.get_leaf("Br04").remove_creature("Unicorn")
    aps.get_leaf("Bk03").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk03").add_creature("Ranger")
    aps.get_leaf("Bk05").reveal_creatures(["Ranger"])
    aps.get_leaf("Bk05").add_creature("Ranger")
    aps.check()
    aps.print_leaves()
    turn = 41
    print("\nTurn", turn)
    aps.get_leaf("Gd05").split(2, "Gd09", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd05").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd05").add_creature("Troll")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Hydra")
    aps.get_leaf("Gd11").reveal_creatures(["Ranger"])
    aps.get_leaf("Gd11").add_creature("Troll")
    aps.get_leaf("Br12").split(2, "Br03", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br03"), turn)
    aps.get_leaf("Bk05").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk05").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 42
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd02", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd02"), turn)
    aps.get_leaf("Gd11").reveal_creatures(["Troll"])
    aps.get_leaf("Gd11").add_creature("Troll")
    aps.get_leaf("Br12").split(2, "Br08", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br08"), turn)
    aps.get_leaf("Bk05").split(2, "Bk12", turn)
    aps.get_leaf("Bk02").reveal_creatures(["Troll"])
    aps.get_leaf("Bk02").add_creature("Troll")
    aps.get_leaf("Bk03").reveal_creatures(["Ranger", "Ranger", "Ranger"])
    aps.get_leaf("Bk03").add_creature("Guardian")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.check()
    aps.print_leaves()
    turn = 43
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd07", turn)
    aps.get_leaf("Gd11").split(2, "Gd10", turn)
    aps.get_leaf("Gd11").merge(aps.get_leaf("Gd10"), turn)
    aps.get_leaf("Br12").split(2, "Br07", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br07"), turn)
    aps.get_leaf("Bk06").split(2, "Bk08", turn)
    aps.check()
    aps.print_leaves()
    turn = 44
    print("\nTurn", turn)
    aps.get_leaf("Gd11").split(2, "Gd04", turn)
    aps.get_leaf("Gd11").merge(aps.get_leaf("Gd04"), turn)
    aps.get_leaf("Br12").split(2, "Br11", turn)
    aps.get_leaf("Br12").merge(aps.get_leaf("Br11"), turn)
    aps.get_leaf("Bk01").remove_creature("Centaur")
    aps.get_leaf("Bk01").remove_creature("Centaur")
    aps.check()
    aps.print_leaves()
    turn = 45
    print("\nTurn", turn)
    aps.get_leaf("Gd11").split(2, "Gd02", turn)
    aps.get_leaf("Gd11").merge(aps.get_leaf("Gd02"), turn)
    aps.get_leaf("Gd01").reveal_creatures(["Minotaur", "Minotaur"])
    aps.get_leaf("Gd01").add_creature("Unicorn")
    aps.get_leaf("Br12").split(2, "Br11", turn)
    aps.get_leaf("Br11").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br11").add_creature("Minotaur")
    aps.get_leaf("Bk05").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk05").add_creature("Warbear")
    aps.get_leaf("Bk06").reveal_creatures(["Hydra"])
    aps.get_leaf("Bk06").add_creature("Hydra")
    aps.check()
    aps.print_leaves()
    turn = 46
    print("\nTurn", turn)
    aps.get_leaf("Gd11").split(2, "Gd02", turn)
    aps.get_leaf("Br01").reveal_creatures(["Titan"])
    aps.get_leaf("Br01").add_creature("Warlock")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Warbear")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Hydra")
    aps.check()
    aps.print_leaves()
    turn = 47
    print("\nTurn", turn)
    aps.get_leaf("Br01").split(2, "Br06", turn)
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Serpent")
    aps.get_leaf("Gd07").remove_creature("Guardian")
    aps.get_leaf("Gd07").remove_creature("Guardian")
    aps.get_leaf("Gd11").remove_creature("Guardian")
    aps.get_leaf("Gd11").remove_creature("Guardian")
    aps.get_leaf("Gd11").remove_creature("Ranger")
    aps.get_leaf("Gd11").remove_creature("Troll")
    aps.get_leaf("Gd11").remove_creature("Troll")
    aps.get_leaf("Bk06").add_creature("Angel")
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Serpent")
    aps.get_leaf("Gd06").reveal_creatures(["Unicorn"])
    aps.get_leaf("Gd06").add_creature("Warbear")
    aps.get_leaf("Bk02").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bk02").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 49
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    aps.get_leaf("Gd06").split(2, "Gd07", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd07"), turn)
    aps.get_leaf("Gd01").reveal_creatures(["Unicorn"])
    aps.get_leaf("Gd01").add_creature("Warbear")
    aps.get_leaf("Gd09").reveal_creatures(["Lion", "Lion"])
    aps.get_leaf("Gd09").add_creature("Minotaur")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Minotaur")
    aps.get_leaf("Bk05").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Bk05").add_creature("Giant")
    aps.check()
    aps.print_leaves()
    turn = 50
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd10", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd10"), turn)
    aps.get_leaf("Gd06").split(2, "Gd11", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd11"), turn)
    aps.get_leaf("Gd01").reveal_creatures(["Minotaur"])
    aps.get_leaf("Gd01").add_creature("Minotaur")
    aps.get_leaf("Br12").split(2, "Br07", turn)
    aps.get_leaf("Bk03").reveal_creatures(["Guardian"])
    aps.get_leaf("Bk03").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 51
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    aps.get_leaf("Gd06").split(2, "Gd11", turn)
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Behemoth")
    aps.get_leaf("Bk05").split(2, "Bk07", turn)
    aps.get_leaf("Gd09").remove_creature("Minotaur")
    aps.get_leaf("Gd09").remove_creature("Lion")
    aps.get_leaf("Gd09").remove_creature("Lion")
    aps.get_leaf("Gd11").remove_creature("Unicorn")
    aps.get_leaf("Gd11").remove_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 52
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd04", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd04"), turn)
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.get_leaf("Br01").split(2, "Br03", turn)
    aps.get_leaf("Br11").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br11").add_creature("Warbear")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Br11").remove_creature("Unicorn")
    aps.get_leaf("Br11").remove_creature("Unicorn")
    aps.get_leaf("Br11").remove_creature("Warbear")
    aps.get_leaf("Br11").remove_creature("Minotaur")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bk08").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Bk08").add_creature("Giant")
    aps.check()
    aps.print_leaves()
    turn = 53
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd09", turn)
    aps.get_leaf("Gd05").reveal_creatures(["Ranger", "Ranger", "Ranger"])
    aps.get_leaf("Gd05").add_creature("Guardian")
    aps.get_leaf("Gd08").reveal_creatures(["Ranger", "Ranger", "Ranger"])
    aps.get_leaf("Gd08").add_creature("Guardian")
    aps.get_leaf("Gd01").remove_creature("Unicorn")
    aps.get_leaf("Gd01").remove_creature("Warbear")
    aps.get_leaf("Gd01").remove_creature("Minotaur")
    aps.get_leaf("Gd01").remove_creature("Minotaur")
    aps.get_leaf("Gd01").remove_creature("Minotaur")
    aps.get_leaf("Gd02").remove_creature("Ranger")
    aps.get_leaf("Gd02").remove_creature("Ranger")
    aps.get_leaf("Bk05").reveal_creatures(["Giant", "Warbear", "Warbear",
                                           "Ranger", "Troll"])
    aps.get_leaf("Gd09").reveal_creatures(["Serpent", "Angel"])
    aps.get_leaf("Gd09").remove_creature("Serpent")
    aps.get_leaf("Bk05").remove_creature("Giant")
    aps.get_leaf("Bk05").remove_creature("Warbear")
    aps.get_leaf("Bk02").remove_creature("Archangel")
    aps.get_leaf("Bk05").add_creature("Archangel")
    aps.get_leaf("Gd09").remove_creature("Angel")
    aps.get_leaf("Bk05").reveal_creatures(["Archangel", "Warbear", "Ranger",
                                           "Troll"])
    aps.get_leaf("Bk05").add_creature("Angel")
    aps.get_leaf("Bk02").reveal_creatures(["Troll", "Troll", "Troll"])
    aps.get_leaf("Bk02").add_creature("Wyvern")
    aps.check()
    aps.print_leaves()
    turn = 54
    print("\nTurn", turn)
    aps.get_leaf("Gd05").split(2, "Gd07", turn)
    aps.get_leaf("Br03").reveal_creatures(["Behemoth"])
    aps.get_leaf("Br03").add_creature("Behemoth")
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Behemoth")
    aps.get_leaf("Gd06").reveal_creatures(["Griffon"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.get_leaf("Bk08").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk08").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 58
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd11", turn)
    aps.get_leaf("Br06").reveal_creatures(["Warlock"])
    aps.get_leaf("Br06").add_creature("Warlock")
    aps.get_leaf("Br12").reveal_creatures(["Unicorn"])
    aps.get_leaf("Br12").add_creature("Minotaur")
    aps.get_leaf("Br12").reveal_creatures(["Minotaur"])
    aps.get_leaf("Br12").add_creature("Minotaur")
    aps.get_leaf("Bk10").reveal_creatures(["Warlock"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 60
    print("\nTurn", turn)
    aps.get_leaf("Br12").split(2, "Br02", turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Gd12").remove_creature("Guardian")
    aps.get_leaf("Gd12").remove_creature("Gorgon")
    aps.get_leaf("Gd12").remove_creature("Gorgon")
    aps.get_leaf("Gd12").remove_creature("Gorgon")
    aps.get_leaf("Gd12").remove_creature("Gorgon")
    aps.get_leaf("Gd12").remove_creature("Cyclops")
    aps.get_leaf("Gd05").remove_creature("Guardian")
    aps.get_leaf("Gd05").remove_creature("Ranger")
    aps.get_leaf("Gd05").remove_creature("Ranger")
    aps.get_leaf("Gd05").remove_creature("Ranger")
    aps.get_leaf("Gd05").remove_creature("Troll")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Gd11").remove_creature("Griffon")
    aps.get_leaf("Gd11").remove_creature("Griffon")
    aps.get_leaf("Bk07").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk07").add_creature("Warbear")
    aps.get_leaf("Bk10").reveal_creatures(["Warlock"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.get_leaf("Br01").reveal_creatures(["Serpent"])
    aps.get_leaf("Br01").add_creature("Behemoth")
    aps.get_leaf("Br03").reveal_creatures(["Behemoth"])
    aps.get_leaf("Br03").add_creature("Behemoth")
    aps.check()
    aps.print_leaves()
    turn = 61
    print("\nTurn", turn)
    aps.get_leaf("Bk10").split(2, "Bk09", turn)
    aps.get_leaf("Gd07").remove_creature("Ranger")
    aps.get_leaf("Gd07").remove_creature("Ranger")
    aps.get_leaf("Bk07").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk07").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 62
    print("\nTurn", turn)
    aps.get_leaf("Br01").split(2, "Br05", turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Angel", "Angel",
                                           "Angel", "Warlock"])
    aps.get_leaf("Br12").reveal_creatures(["Unicorn", "Unicorn", "Unicorn",
                                           "Unicorn", "Unicorn"])
    aps.get_leaf("Br12").remove_creature("Unicorn")
    aps.get_leaf("Br12").remove_creature("Unicorn")
    aps.get_leaf("Br12").remove_creature("Unicorn")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk05").remove_creature("Archangel")
    aps.get_leaf("Bk10").add_creature("Archangel")
    aps.get_leaf("Br12").remove_creature("Unicorn")
    aps.get_leaf("Br12").remove_creature("Unicorn")
    aps.get_leaf("Bk10").remove_creature("Archangel")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Angel", "Warlock"])
    aps.get_leaf("Bk10").add_creature("Archangel")
    aps.get_leaf("Gd08").remove_creature("Guardian")
    aps.get_leaf("Gd08").remove_creature("Ranger")
    aps.get_leaf("Gd08").remove_creature("Ranger")
    aps.get_leaf("Gd08").remove_creature("Ranger")
    aps.get_leaf("Bk02").add_creature("Angel")
    aps.get_leaf("Bk03").reveal_creatures(["Guardian", "Guardian", "Ranger",
                                           "Ranger", "Ranger"])
    aps.get_leaf("Br06").reveal_creatures(["Warlock", "Warlock", "Gorgon"])
    aps.get_leaf("Br06").remove_creature("Warlock")
    aps.get_leaf("Bk03").remove_creature("Ranger")
    aps.get_leaf("Bk03").remove_creature("Ranger")
    aps.get_leaf("Br06").remove_creature("Warlock")
    aps.get_leaf("Br06").remove_creature("Gorgon")
    aps.get_leaf("Bk03").reveal_creatures(["Guardian", "Guardian", "Ranger"])
    aps.get_leaf("Bk07").reveal_creatures(["Warbear", "Warbear", "Troll",
                                           "Troll"])
    aps.get_leaf("Br07").reveal_creatures(["Warbear", "Minotaur"])
    aps.get_leaf("Br07").remove_creature("Warbear")
    aps.get_leaf("Bk07").remove_creature("Warbear")
    aps.get_leaf("Br07").remove_creature("Minotaur")
    aps.get_leaf("Bk07").reveal_creatures(["Warbear", "Troll", "Troll"])
    aps.get_leaf("Bk07").add_creature("Angel")
    aps.get_leaf("Bk08").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk08").add_creature("Warbear")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Wyvern")
    aps.check()
    aps.print_leaves()
    turn = 63
    print("\nTurn", turn)
    aps.get_leaf("Bk02").split(2, "Bk11", turn)
    aps.get_leaf("Bk06").split(2, "Bk04", turn)
    aps.get_leaf("Bk02").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk02").add_creature("Wyvern")
    aps.get_leaf("Bk06").reveal_creatures(["Hydra"])
    aps.get_leaf("Bk06").add_creature("Wyvern")
    aps.get_leaf("Bk07").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk07").add_creature("Warbear")
    aps.get_leaf("Bk09").reveal_creatures(["Warlock"])
    aps.get_leaf("Bk09").add_creature("Warlock")
    aps.get_leaf("Bk10").reveal_creatures(["Warlock"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.check()
    aps.print_leaves()
    turn = 64
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd07", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd07"), turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").add_creature("Warlock")
    aps.get_leaf("Br02").remove_creature("Minotaur")
    aps.get_leaf("Br02").remove_creature("Minotaur")
    aps.check()
    aps.print_leaves()
    turn = 65
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd08", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd08"), turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Archangel", "Angel",
                                           "Warlock", "Warlock"])
    aps.get_leaf("Br03").reveal_creatures(["Angel", "Behemoth", "Behemoth",
                                           "Behemoth"])
    aps.get_leaf("Br03").remove_creature("Angel")
    aps.get_leaf("Br03").remove_creature("Behemoth")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Bk05").remove_creature("Angel")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Br03").remove_creature("Behemoth")
    aps.get_leaf("Bk10").remove_creature("Warlock")
    aps.get_leaf("Bk10").remove_creature("Warlock")
    aps.get_leaf("Br03").remove_creature("Behemoth")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Archangel", "Angel"])
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Bk02").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk02").add_creature("Wyvern")
    aps.get_leaf("Bk05").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk05").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 66
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd05", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Warlock"])
    aps.get_leaf("Gd03").add_creature("Warlock")
    aps.get_leaf("Bk06").reveal_creatures(["Hydra"])
    aps.get_leaf("Bk06").add_creature("Griffon")
    aps.get_leaf("Bk07").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk07").add_creature("Warbear")
    aps.get_leaf("Bk08").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk08").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 67
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd02", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").add_creature("Warlock")
    aps.get_leaf("Bk02").split(2, "Bk01", turn)
    aps.get_leaf("Gd05").remove_creature("Wyvern")
    aps.get_leaf("Gd05").remove_creature("Griffon")
    aps.get_leaf("Br05").remove_creature("Behemoth")
    aps.get_leaf("Br05").remove_creature("Behemoth")
    aps.get_leaf("Bk05").reveal_creatures(["Warbear"])
    aps.get_leaf("Bk05").add_creature("Warbear")
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Gd03").add_creature("Guardian")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Wyvern")
    aps.check()
    aps.print_leaves()
    turn = 68
    print("\nTurn", turn)
    aps.get_leaf("Bk06").split(2, "Gr01", turn)
    aps.get_leaf("Bk06").merge(aps.get_leaf("Gr01"), turn)
    aps.check()
    aps.print_leaves()
    turn = 69
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd12", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Gd03").add_creature("Guardian")
    aps.get_leaf("Gd06").reveal_creatures(["Wyvern"])
    aps.get_leaf("Gd06").add_creature("Wyvern")
    aps.get_leaf("Bk06").split(2, "Bu09", turn)
    aps.get_leaf("Bk11").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk11").add_creature("Warbear")
    aps.check()
    aps.print_leaves()
    turn = 70
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd01", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd01").reveal_creatures(["Wyvern", "Wyvern"])
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Archangel", "Angel",
                                           "Angel"])
    aps.get_leaf("Gd01").remove_creature("Wyvern")
    aps.get_leaf("Gd01").remove_creature("Wyvern")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Archangel", "Angel",
                                           "Angel"])
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Gd03").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Gd03").add_creature("Guardian")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Wyvern")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Gd12").remove_creature("Guardian")
    aps.get_leaf("Gd12").remove_creature("Warlock")
    aps.get_leaf("Bk01").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk01").add_creature("Wyvern")
    aps.get_leaf("Bk04").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk04").add_creature("Wyvern")
    aps.get_leaf("Bk05").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Bk05").add_creature("Giant")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.check()
    aps.print_leaves()
    turn = 71
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd04", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Bk03").remove_creature("Guardian")
    aps.get_leaf("Bk03").remove_creature("Guardian")
    aps.get_leaf("Bk03").remove_creature("Ranger")
    aps.get_leaf("Bk06").reveal_creatures(["Hydra"])
    aps.get_leaf("Bk06").add_creature("Griffon")
    aps.get_leaf("Gd06").reveal_creatures(["Wyvern"])
    aps.get_leaf("Gd06").add_creature("Wyvern")
    aps.get_leaf("Br01").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Br01").add_creature("Guardian")
    aps.get_leaf("Bu09").reveal_creatures(["Hydra"])
    aps.get_leaf("Bu09").add_creature("Wyvern")
    aps.check()
    aps.print_leaves()
    turn = 74
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd11", turn)
    aps.get_leaf("Br01").reveal_creatures(["Titan"])
    aps.get_leaf("Br01").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Br01").add_creature("Guardian")
    aps.get_leaf("Bk02").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk02").add_creature("Wyvern")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 75
    print("\nTurn", turn)
    aps.get_leaf("Br01").split(2, "Br05", turn)
    aps.get_leaf("Bu09").reveal_creatures(["Griffon"])
    aps.get_leaf("Bu09").add_creature("Griffon")
    aps.get_leaf("Gd06").reveal_creatures(["Griffon"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.get_leaf("Gd11").reveal_creatures(["Wyvern"])
    aps.get_leaf("Gd11").add_creature("Wyvern")
    aps.get_leaf("Gd11").remove_creature("Wyvern")
    aps.get_leaf("Gd11").remove_creature("Wyvern")
    aps.get_leaf("Gd11").remove_creature("Wyvern")
    aps.get_leaf("Bk02").reveal_creatures(["Wyvern"])
    aps.get_leaf("Bk02").add_creature("Wyvern")
    aps.get_leaf("Bk06").reveal_creatures(["Griffon"])
    aps.get_leaf("Bk06").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 77
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd08", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent", "Serpent", "Serpent"])
    aps.get_leaf("Gd03").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 78
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd01", turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Archangel", "Angel",
                                           "Angel", "Angel", "Warlock"])
    aps.get_leaf("Br01").reveal_creatures(["Titan", "Serpent", "Serpent",
                                           "Serpent", "Serpent"])
    aps.get_leaf("Br01").remove_creature("Serpent")
    aps.get_leaf("Bk07").remove_creature("Angel")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Br01").remove_creature("Serpent")
    aps.get_leaf("Br01").remove_creature("Serpent")
    aps.get_leaf("Bk10").remove_creature("Angel")
    aps.get_leaf("Br01").remove_creature("Titan")
    aps.get_leaf("Bk10").remove_creature("Archangel")
    aps.get_leaf("Br01").remove_creature("Serpent")
    aps.get_leaf("Br05").remove_creature("Guardian")
    aps.get_leaf("Br05").remove_creature("Guardian")
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Angel", "Angel",
                                           "Angel", "Warlock"])
    aps.get_leaf("Bk10").add_creature("Archangel")
    aps.get_leaf("Bk10").add_creature("Angel")
    aps.get_leaf("Gd04").remove_creature("Guardian")
    aps.get_leaf("Gd04").remove_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 79
    print("\nTurn", turn)
    aps.get_leaf("Bk10").split(2, "Bk03", turn)
    aps.get_leaf("Gd01").remove_creature("Guardian")
    aps.get_leaf("Gd01").remove_creature("Behemoth")
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Gd08").reveal_creatures(["Griffon"])
    aps.get_leaf("Gd08").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 80
    print("\nTurn", turn)
    aps.get_leaf("Bk02").split(2, "Gr11", turn)
    aps.get_leaf("Bk02").reveal_creatures(["Guardian"])
    aps.get_leaf("Bk02").add_creature("Guardian")
    aps.get_leaf("Bu09").reveal_creatures(["Griffon"])
    aps.get_leaf("Bu09").add_creature("Griffon")
    aps.get_leaf("Bk05").reveal_creatures(["Giant"])
    aps.get_leaf("Bk05").add_creature("Giant")
    aps.get_leaf("Bk04").reveal_creatures(["Wyvern", "Wyvern", "Wyvern"])
    aps.get_leaf("Bk04").add_creature("Guardian")
    aps.get_leaf("Bu09").reveal_creatures(["Griffon"])
    aps.get_leaf("Bu09").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 84
    print("\nTurn", turn)
    aps.get_leaf("Bk05").split(2, "Gr06", turn)
    aps.get_leaf("Gd08").remove_creature("Griffon")
    aps.get_leaf("Gd08").remove_creature("Griffon")
    aps.get_leaf("Gd08").remove_creature("Griffon")
    aps.get_leaf("Bk04").add_creature("Angel")
    aps.get_leaf("Bu09").reveal_creatures(["Griffon"])
    aps.get_leaf("Bu09").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 87
    print("\nTurn", turn)
    aps.get_leaf("Bu09").split(2, "Br07", turn)
    aps.get_leaf("Bk04").reveal_creatures(["Guardian"])
    aps.get_leaf("Bk04").add_creature("Guardian")
    aps.get_leaf("Bk05").reveal_creatures(["Giant", "Giant"])
    aps.get_leaf("Bk05").add_creature("Colossus")
    aps.get_leaf("Bk08").reveal_creatures(["Warbear", "Warbear", "Warbear"])
    aps.get_leaf("Bk08").add_creature("Guardian")
    aps.get_leaf("Bu09").reveal_creatures(["Griffon", "Griffon", "Griffon"])
    aps.get_leaf("Bu09").add_creature("Guardian")
    aps.check()
    aps.print_leaves()
    turn = 89
    print("\nTurn", turn)
    aps.get_leaf("Bk08").split(2, "Gr09", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Br07").reveal_creatures(["Griffon"])
    aps.get_leaf("Br07").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 91
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    aps.get_leaf("Bk07").remove_creature("Warbear")
    aps.get_leaf("Bk07").remove_creature("Warbear")
    aps.get_leaf("Bk07").remove_creature("Warbear")
    aps.get_leaf("Bk07").remove_creature("Troll")
    aps.get_leaf("Bk07").remove_creature("Troll")
    aps.get_leaf("Bk08").reveal_creatures(["Giant"])
    aps.get_leaf("Bk08").add_creature("Giant")
    aps.check()
    aps.print_leaves()
    turn = 92
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd07", turn)
    aps.get_leaf("Gd03").merge(aps.get_leaf("Gd07"), turn)
    aps.check()
    aps.print_leaves()
    turn = 93
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd10", turn)
    aps.get_leaf("Gd03").reveal_creatures(["Serpent"])
    aps.get_leaf("Gd03").add_creature("Behemoth")
    aps.get_leaf("Gd02").remove_creature("Warlock")
    aps.get_leaf("Gd02").remove_creature("Warlock")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra"])
    aps.get_leaf("Gd06").add_creature("Griffon")
    aps.get_leaf("Gd10").remove_creature("Behemoth")
    aps.get_leaf("Gd10").remove_creature("Behemoth")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra", "Hydra", "Hydra",
                                           "Hydra", "Hydra", "Griffon"])
    aps.get_leaf("Bk03").reveal_creatures(["Angel", "Warlock"])
    aps.get_leaf("Bk03").remove_creature("Angel")
    aps.get_leaf("Bk03").remove_creature("Warlock")
    aps.get_leaf("Gd06").reveal_creatures(["Hydra", "Hydra", "Hydra",
                                           "Hydra", "Hydra", "Griffon"])
    aps.get_leaf("Gd06").add_creature("Angel")
    aps.get_leaf("Bk05").reveal_creatures(["Colossus"])
    aps.get_leaf("Bk05").add_creature("Colossus")
    aps.check()
    aps.print_leaves()
    turn = 97
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd09", turn)
    aps.get_leaf("Gd06").merge(aps.get_leaf("Gd09"), turn)
    aps.get_leaf("Bk01").remove_creature("Wyvern")
    aps.get_leaf("Bk01").remove_creature("Wyvern")
    aps.get_leaf("Bk01").remove_creature("Troll")
    aps.check()
    aps.print_leaves()
    turn = 98
    print("\nTurn", turn)
    aps.get_leaf("Gd06").split(2, "Gd02", turn)
    aps.get_leaf("Gd02").reveal_creatures(["Griffon"])
    aps.get_leaf("Gd02").add_creature("Griffon")
    aps.check()
    aps.print_leaves()
    turn = 99
    print("\nTurn", turn)
    aps.get_leaf("Bk06").split(2, "Bk07", turn)
    aps.get_leaf("Bk06").reveal_creatures(["Hydra", "Hydra", "Hydra",
                                           "Angel", "Wyvern"])
    aps.get_leaf("Gd02").reveal_creatures(["Angel", "Griffon", "Griffon"])
    aps.get_leaf("Gd02").remove_creature("Griffon")
    aps.get_leaf("Gd02").remove_creature("Griffon")
    aps.get_leaf("Bk06").remove_creature("Angel")
    aps.get_leaf("Bk10").remove_creature("Archangel")
    aps.get_leaf("Bk06").add_creature("Archangel")
    aps.get_leaf("Gd02").remove_creature("Angel")
    aps.get_leaf("Bk06").reveal_creatures(["Archangel", "Hydra", "Hydra",
                                           "Hydra", "Wyvern"])
    aps.get_leaf("Bk06").add_creature("Angel")
    aps.get_leaf("Bk02").reveal_creatures(["Angel"])
    aps.get_leaf("Bk07").remove_creature("Griffon")
    aps.get_leaf("Bk07").remove_creature("Griffon")
    aps.get_leaf("Gd06").remove_creature("Hydra")
    aps.get_leaf("Gd06").remove_creature("Hydra")
    aps.get_leaf("Gd06").remove_creature("Hydra")
    aps.get_leaf("Gd06").remove_creature("Hydra")
    aps.get_leaf("Gd06").remove_creature("Hydra")
    aps.check()
    aps.print_leaves()
    turn = 105
    print("\nTurn", turn)
    aps.get_leaf("Bk05").split(2, "Bk03", turn)
    aps.get_leaf("Bk05").reveal_creatures(["Colossus"])
    aps.get_leaf("Bk05").add_creature("Colossus")
    aps.get_leaf("Bk09").reveal_creatures(["Warlock"])
    aps.get_leaf("Bk09").add_creature("Warlock")
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Bk10").add_creature("Warlock")
    aps.get_leaf("Gd03").reveal_creatures(["Titan"])
    aps.get_leaf("Gd03").add_creature("Warlock")
    aps.get_leaf("Gr09").reveal_creatures(["Warbear", "Warbear"])
    aps.get_leaf("Gr09").add_creature("Giant")
    aps.check()
    aps.print_leaves()
    turn = 107
    print("\nTurn", turn)
    aps.get_leaf("Gd03").split(2, "Gd12", turn)
    aps.get_leaf("Bk10").reveal_creatures(["Titan"])
    aps.get_leaf("Gd12").remove_creature("Behemoth")
    aps.get_leaf("Gd12").remove_creature("Warlock")
    aps.check()
    aps.print_leaves()
    print("\ntest 9 ends")


def test_predict_splits10():
    print("\ntest 10 begins")

    aps = AllPredictSplits()
    aps.print_leaves()

    turn = 1
    print("\nTurn", turn)
    ps = PredictSplits("Gr", "Gr07", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Gr07").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    ps = PredictSplits("Bu", "Bu08", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Bu08").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    ps = PredictSplits("Gd", "Gd01", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Gd01").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    ps = PredictSplits("Bk", "Bk10", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Bk10").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    ps = PredictSplits("Br", "Br12", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Br12").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    ps = PredictSplits("Rd", "Rd12", ["Titan", "Angel", "Gargoyle",
                                      "Gargoyle", "Centaur", "Centaur",
                                      "Ogre", "Ogre"])
    aps.append(ps)
    aps.get_leaf("Rd12").reveal_creatures(["Titan", "Angel", "Gargoyle",
                                           "Gargoyle", "Centaur", "Centaur",
                                           "Ogre", "Ogre"])
    aps.get_leaf("Gr07").split(4, "Gr12", turn)
    aps.get_leaf("Gr07").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gr07").add_creature("Troll")
    aps.get_leaf("Gr12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gr12").add_creature("Cyclops")
    aps.get_leaf("Bu08").split(4, "Bu12", turn)
    aps.get_leaf("Bu08").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu08").add_creature("Centaur")
    aps.get_leaf("Bu12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Bu12").add_creature("Cyclops")
    aps.get_leaf("Gd01").split(4, "Gd12", turn)
    aps.get_leaf("Gd01").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Gd01").add_creature("Troll")
    aps.get_leaf("Gd12").reveal_creatures(["Centaur"])
    aps.get_leaf("Gd12").add_creature("Centaur")
    aps.get_leaf("Bk10").split(4, "Bk03", turn)
    aps.get_leaf("Bk03").reveal_creatures(["Titan"])
    aps.get_leaf("Bk03").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Bk03").add_creature("Cyclops")
    aps.get_leaf("Bk10").reveal_creatures(["Centaur"])
    aps.get_leaf("Bk10").add_creature("Centaur")
    aps.get_leaf("Br12").split(4, "Br07", turn)
    aps.get_leaf("Br07").reveal_creatures(["Titan"])
    aps.get_leaf("Br07").reveal_creatures(["Titan"])
    aps.get_leaf("Br07").add_creature("Warlock")
    aps.get_leaf("Br12").reveal_creatures(["Ogre"])
    aps.get_leaf("Br12").add_creature("Ogre")
    aps.get_leaf("Rd12").split(4, "Rd03", turn)
    aps.get_leaf("Rd12").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Rd12").add_creature("Gargoyle")
    aps.print_leaves()
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1
    assert aps.get_leaf("Br07").num_uncertain_creatures == 3
    assert aps.get_leaf("Br12").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd01").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 2
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 4
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 3

    turn = 2
    print("\nTurn", turn)
    aps.get_leaf("Gr07").reveal_creatures(["Troll"])
    aps.get_leaf("Gr07").add_creature("Troll")
    aps.get_leaf("Gr12").reveal_creatures(["Centaur"])
    aps.get_leaf("Gr12").add_creature("Centaur")
    aps.get_leaf("Gd01").reveal_creatures(["Centaur"])
    aps.get_leaf("Gd01").add_creature("Centaur")
    aps.get_leaf("Gd12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Gd12").add_creature("Cyclops")
    aps.get_leaf("Br12").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Br12").add_creature("Lion")
    aps.get_leaf("Rd12").reveal_creatures(["Titan"])
    aps.get_leaf("Rd12").add_creature("Warlock")
    aps.get_leaf("Rd03").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Rd03").add_creature("Troll")
    aps.print_leaves()
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1
    assert aps.get_leaf("Br07").num_uncertain_creatures == 0
    assert aps.get_leaf("Br12").num_uncertain_creatures == 0
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd01").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 1

    turn = 3
    print("\nTurn", turn)
    aps.get_leaf("Bu08").reveal_creatures(["Ogre"])
    aps.get_leaf("Bu08").add_creature("Ogre")
    aps.get_leaf("Bu12").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu12").add_creature("Centaur")
    aps.get_leaf("Gd01").reveal_creatures(["Ogre"])
    aps.get_leaf("Gd01").add_creature("Ogre")
    aps.get_leaf("Bk03").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bk03").add_creature("Cyclops")
    aps.get_leaf("Bk10").reveal_creatures(["Ogre"])
    aps.get_leaf("Bk10").add_creature("Ogre")
    aps.get_leaf("Rd03").reveal_creatures(["Gargoyle"])
    aps.get_leaf("Rd03").add_creature("Gargoyle")
    aps.get_leaf("Rd12").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Rd12").add_creature("Lion")
    aps.print_leaves()
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1
    assert aps.get_leaf("Br07").num_uncertain_creatures == 0
    assert aps.get_leaf("Br12").num_uncertain_creatures == 0
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 1
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd01").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 0

    turn = 4
    print("\nTurn", turn)
    aps.get_leaf("Gr07").reveal_creatures(["Troll"])
    aps.get_leaf("Gr07").add_creature("Troll")
    aps.get_leaf("Gr12").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gr12").add_creature("Cyclops")
    aps.get_leaf("Bu08").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Bu08").add_creature("Lion")
    aps.get_leaf("Gd01").split(2, "Gd07", turn)
    aps.get_leaf("Gd01").reveal_creatures(["Troll"])
    aps.get_leaf("Gd01").add_creature("Troll")
    aps.get_leaf("Gd12").reveal_creatures(["Cyclops"])
    aps.get_leaf("Gd12").add_creature("Cyclops")
    aps.get_leaf("Bk03").reveal_creatures(["Cyclops"])
    aps.get_leaf("Bk03").add_creature("Cyclops")
    aps.get_leaf("Bk10").reveal_creatures(["Ogre"])
    aps.get_leaf("Bk10").add_creature("Ogre")
    aps.get_leaf("Br12").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Br12").add_creature("Troll")
    aps.get_leaf("Rd03").reveal_creatures(["Troll"])
    aps.get_leaf("Rd03").add_creature("Troll")
    aps.print_leaves()
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 1
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 1
    assert aps.get_leaf("Br07").num_uncertain_creatures == 0
    assert aps.get_leaf("Br12").num_uncertain_creatures == 0
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 1
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd01").num_uncertain_creatures == 3
    assert aps.get_leaf("Gd07").num_uncertain_creatures == 2
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 0

    turn = 5
    print("\nTurn", turn)
    aps.get_leaf("Gr07").split(2, "Gr05", turn)
    aps.get_leaf("Gr12").split(2, "Gr10", turn)
    aps.get_leaf("Gr05").reveal_creatures(["Ogre"])
    aps.get_leaf("Gr05").add_creature("Ogre")
    aps.get_leaf("Gr07").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Gr07").add_creature("Ranger")
    aps.get_leaf("Bu08").split(2, "Bu02", turn)
    aps.get_leaf("Bu08").reveal_creatures(["Ogre", "Ogre", "Ogre"])
    aps.get_leaf("Bu08").add_creature("Minotaur")
    aps.get_leaf("Bu12").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu12").add_creature("Centaur")
    aps.get_leaf("Gd12").split(2, "Gd11", turn)
    aps.get_leaf("Gd12").merge(aps.get_leaf("Gd11"), turn)
    aps.get_leaf("Gd07").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gd07").add_creature("Lion")
    aps.get_leaf("Bk03").split(2, "Bk04", turn)
    aps.get_leaf("Bk10").split(2, "Bk07", turn)
    aps.get_leaf("Bk10").merge(aps.get_leaf("Bk07"), turn)
    aps.get_leaf("Bk03").reveal_creatures(["Ogre"])
    aps.get_leaf("Bk03").add_creature("Ogre")
    aps.get_leaf("Br12").split(2, "Br10", turn)
    aps.get_leaf("Gr10").remove_creature("Gargoyle")
    aps.get_leaf("Gr10").remove_creature("Gargoyle")
    aps.get_leaf("Br07").reveal_creatures(["Ogre"])
    aps.get_leaf("Br07").add_creature("Ogre")
    aps.get_leaf("Br12").reveal_creatures(["Troll"])
    aps.get_leaf("Br12").add_creature("Troll")
    aps.get_leaf("Rd03").split(2, "Rd04", turn)
    aps.get_leaf("Rd12").split(2, "Rd10", turn)
    aps.get_leaf("Rd12").reveal_creatures(["Gargoyle", "Gargoyle"])
    aps.get_leaf("Rd12").add_creature("Cyclops")
    aps.print_leaves()
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 3
    assert aps.get_leaf("Bk04").num_uncertain_creatures == 2
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 0
    assert aps.get_leaf("Br07").num_uncertain_creatures == 0
    assert aps.get_leaf("Br10").num_uncertain_creatures == 2
    assert aps.get_leaf("Br12").num_uncertain_creatures == 4
    assert aps.get_leaf("Bu02").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 2
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd01").num_uncertain_creatures == 1
    assert aps.get_leaf("Gd07").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr05").num_uncertain_creatures == 1
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 3
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 1
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 5
    assert aps.get_leaf("Rd04").num_uncertain_creatures == 2
    assert aps.get_leaf("Rd10").num_uncertain_creatures == 2
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 3

    turn = 6
    print("\nTurn", turn)
    aps.get_leaf("Bk04").remove_creature("Gargoyle")
    aps.get_leaf("Bk04").remove_creature("Gargoyle")
    aps.get_leaf("Gr05").reveal_creatures(["Ogre", "Ogre", "Ogre"])
    aps.get_leaf("Rd10").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Rd10").remove_creature("Centaur")
    aps.get_leaf("Gr07").remove_creature("Angel")
    aps.get_leaf("Gr05").add_creature("Angel")
    aps.get_leaf("Rd10").remove_creature("Centaur")
    aps.get_leaf("Gr05").remove_creature("Ogre")
    aps.get_leaf("Gr05").reveal_creatures(["Angel", "Ogre", "Ogre"])
    aps.get_leaf("Gr07").reveal_creatures(["Ranger"])
    aps.get_leaf("Gr07").add_creature("Ranger")
    aps.get_leaf("Gr12").reveal_creatures(["Centaur", "Centaur"])
    aps.get_leaf("Gr12").add_creature("Lion")
    aps.get_leaf("Bu12").split(2, "Bu11", turn)
    aps.get_leaf("Bu12").reveal_creatures(["Titan", "Cyclops", "Centaur",
                                           "Centaur", "Centaur"])
    aps.get_leaf("Gd07").reveal_creatures(["Lion", "Centaur", "Centaur"])
    aps.get_leaf("Gd07").remove_creature("Centaur")
    aps.get_leaf("Bu12").remove_creature("Centaur")
    aps.get_leaf("Bu08").remove_creature("Angel")
    aps.get_leaf("Bu12").add_creature("Angel")
    aps.get_leaf("Bu12").remove_creature("Centaur")
    aps.get_leaf("Gd07").remove_creature("Lion")
    aps.get_leaf("Gd07").remove_creature("Centaur")
    aps.get_leaf("Bu12").reveal_creatures(["Titan", "Angel", "Cyclops",
                                           "Centaur"])
    aps.get_leaf("Bu12").reveal_creatures(["Centaur"])
    aps.get_leaf("Bu12").add_creature("Centaur")
    aps.get_leaf("Gd12").split(2, "Gd11", turn)
    aps.get_leaf("Gd12").merge(aps.get_leaf("Gd11"), turn)
    aps.get_leaf("Gd01").reveal_creatures(["Angel", "Troll", "Troll",
                                           "Ogre", "Ogre", "Ogre"])
    aps.get_leaf("Rd03").reveal_creatures(["Angel", "Troll", "Troll",
                                           "Gargoyle", "Gargoyle"])
    aps.get_leaf("Rd03").remove_creature("Troll")
    aps.get_leaf("Gd01").remove_creature("Angel")
    aps.get_leaf("Rd03").remove_creature("Gargoyle")
    aps.get_leaf("Gd01").remove_creature("Ogre")
    aps.get_leaf("Rd03").remove_creature("Gargoyle")
    aps.get_leaf("Gd01").remove_creature("Troll")
    aps.get_leaf("Rd03").reveal_creatures(["Troll"])
    aps.get_leaf("Rd03").add_creature("Troll")
    aps.get_leaf("Gd01").remove_creature("Troll")
    aps.get_leaf("Gd01").remove_creature("Ogre")
    aps.get_leaf("Rd03").remove_creature("Angel")
    aps.get_leaf("Gd01").remove_creature("Ogre")
    aps.get_leaf("Rd03").reveal_creatures(["Troll", "Troll"])
    aps.get_leaf("Bk10").split(2, "Bk01", turn)
    aps.get_leaf("Br07").reveal_creatures(["Ogre", "Ogre"])
    aps.get_leaf("Br07").add_creature("Troll")
    aps.print_leaves()
    assert aps.get_leaf("Bk01").num_uncertain_creatures == 2
    assert aps.get_leaf("Bk03").num_uncertain_creatures == 0
    assert aps.get_leaf("Bk10").num_uncertain_creatures == 3
    assert aps.get_leaf("Br07").num_uncertain_creatures == 0
    assert aps.get_leaf("Br10").num_uncertain_creatures == 2
    assert aps.get_leaf("Br12").num_uncertain_creatures == 4
    assert aps.get_leaf("Bu02").num_uncertain_creatures == 1
    assert aps.get_leaf("Bu08").num_uncertain_creatures == 1
    assert aps.get_leaf("Bu11").num_uncertain_creatures == 0
    assert aps.get_leaf("Bu12").num_uncertain_creatures == 0
    assert aps.get_leaf("Gd12").num_uncertain_creatures == 0
    assert aps.get_leaf("Gr05").num_uncertain_creatures == 0
    assert aps.get_leaf("Gr07").num_uncertain_creatures == 0
    assert aps.get_leaf("Gr12").num_uncertain_creatures == 0
    assert aps.get_leaf("Rd03").num_uncertain_creatures == 0
    assert aps.get_leaf("Rd04").num_uncertain_creatures == 0
    assert aps.get_leaf("Rd12").num_uncertain_creatures == 0

    print("\ntest 10 ends")


def test_predict_splits11():
    aps = AllPredictSplits()
    ps = PredictSplits('ai1', 'Bu12', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai4', 'Bk03', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai3', 'Rd07', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai2', 'Br11', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai6', 'Gr10', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai5', 'Gd07', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    aps.get_leaf('Bu12').split(4, 'Bu11', 1)
    aps.get_leaf('Bu12').reveal_creatures(['Centaur', 'Centaur', 'Gargoyle',
                                           'Titan'])
    aps.get_leaf('Bu11').reveal_creatures(['Angel', 'Ogre', 'Ogre',
                                           'Gargoyle'])
    aps.get_leaf('Bu11').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bu11').add_creature('Gargoyle')
    aps.get_leaf('Bu12').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bu12').add_creature('Lion')
    aps.get_leaf('Bk03').split(4, 'Bk02', 1)
    aps.get_leaf('Bk03').reveal_creatures(['Centaur'])
    aps.get_leaf('Bk03').add_creature('Centaur')
    aps.get_leaf('Bk02').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bk02').add_creature('Gargoyle')
    aps.get_leaf('Rd07').split(4, 'Rd06', 1)
    aps.get_leaf('Rd06').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Rd06').add_creature('Lion')
    aps.get_leaf('Rd07').reveal_creatures(['Ogre'])
    aps.get_leaf('Rd07').add_creature('Ogre')
    aps.get_leaf('Br11').split(4, 'Br04', 1)
    aps.get_leaf('Br11').reveal_creatures(['Titan'])
    aps.get_leaf('Br11').add_creature('Warlock')
    aps.get_leaf('Gr10').split(4, 'Gr07', 1)
    aps.get_leaf('Gr10').reveal_creatures(['Titan'])
    aps.get_leaf('Gr10').add_creature('Warlock')
    aps.get_leaf('Gr07').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Gr07').add_creature('Lion')
    aps.get_leaf('Gd07').split(4, 'Gd09', 1)
    aps.get_leaf('Gd07').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gd09').add_creature('Troll')
    aps.get_leaf('Br11').reveal_creatures(('Centaur', 'Gargoyle', 'Gargoyle',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Bu11').reveal_creatures(('Angel', 'Gargoyle', 'Gargoyle',
                                           'Ogre', 'Ogre'))
    aps.get_leaf('Br11').reveal_creatures(('Centaur', 'Gargoyle', 'Gargoyle',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Br11').reveal_creatures(['Titan'])
    aps.get_leaf('Br11').add_creature('Warlock')
    aps.get_leaf('Br11').remove_creatures(['Centaur', 'Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bu11').remove_creatures(['Angel', 'Ogre', 'Ogre', 'Gargoyle',
                                           'Gargoyle'])
    aps.get_leaf('Bu12').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bu12').add_creature('Gargoyle')
    aps.get_leaf('Rd07').reveal_creatures(('Angel', 'Gargoyle', 'Gargoyle',
                                           'Ogre', 'Ogre'))
    aps.get_leaf('Bk03').reveal_creatures(('Centaur', 'Centaur', 'Centaur',
                                           'Gargoyle', 'Titan'))
    aps.get_leaf('Bk03').remove_creatures(['Centaur', 'Centaur', 'Gargoyle',
                                           'Centaur'])
    aps.get_leaf('Rd07').remove_creatures(['Angel', 'Gargoyle', 'Gargoyle',
                                           'Ogre', 'Ogre'])
    aps.get_leaf('Br04').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Br04').add_creature('Troll')
    aps.get_leaf('Gr10').reveal_creatures(['Ogre'])
    aps.get_leaf('Gr10').add_creature('Ogre')
    aps.get_leaf('Gd07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Br11').reveal_creatures(('Titan', 'Warlock', 'Warlock'))
    aps.get_leaf('Bu12').reveal_creatures(('Centaur', 'Centaur', 'Gargoyle',
                                           'Gargoyle', 'Lion', 'Titan'))
    aps.get_leaf('Br11').reveal_creatures(('Titan', 'Warlock', 'Warlock'))
    aps.get_leaf('Br11').reveal_creatures(['Titan'])
    aps.get_leaf('Br11').add_creature('Warlock')
    aps.get_leaf('Bu12').remove_creatures(['Centaur', 'Gargoyle', 'Lion',
                                           'Gargoyle'])
    aps.get_leaf('Br11').remove_creatures(['Titan', 'Warlock'])
    aps.get_leaf('Br04').reveal_creatures(('Angel', 'Centaur', 'Ogre', 'Ogre',
                                           'Troll'))
    aps.get_leaf('Bu12').reveal_creatures(['Titan'])
    aps.get_leaf('Bu12').add_creature('Warlock')
    aps.get_leaf('Bk02').reveal_creatures(('Angel', 'Gargoyle', 'Gargoyle',
                                           'Ogre', 'Ogre'))
    aps.get_leaf('Rd06').reveal_creatures(('Centaur', 'Centaur', 'Lion',
                                           'Ogre', 'Titan'))
    aps.get_leaf('Bk02').remove_creatures(['Angel', 'Ogre', 'Gargoyle'])
    aps.get_leaf('Rd06').remove_creatures(['Titan', 'Centaur', 'Centaur',
                                           'Ogre', 'Lion'])
    aps.get_leaf('Bk02').add_creature('Angel')
    aps.get_leaf('Bk02').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bk02').add_creature('Gargoyle')
    aps.get_leaf('Gr10').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gr10').add_creature('Troll')
    aps.get_leaf('Gr07').reveal_creatures(['Ogre'])
    aps.get_leaf('Gr07').add_creature('Ogre')
    aps.get_leaf('Bk02').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bk02').add_creature('Cyclops')
    aps.get_leaf('Gr10').split(2, 'Gr11', 4)
    aps.get_leaf('Gr07').reveal_creatures(['Lion'])
    aps.get_leaf('Gr07').add_creature('Lion')
    aps.get_leaf('Bu12').reveal_creatures(['Centaur'])
    aps.get_leaf('Bu12').add_creature('Centaur')
    aps.get_leaf('Bk02').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk02').add_creature('Cyclops')
    aps.get_leaf('Gr07').split(2, 'Gr02', 5)
    aps.get_leaf('Gd07').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gd07').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Troll'])
    aps.get_leaf('Gd09').add_creature('Troll')
    aps.get_leaf('Bk02').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Gr10').reveal_creatures(['Troll'])
    aps.get_leaf('Gr10').add_creature('Troll')
    aps.get_leaf('Gr11').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gr11').add_creature('Troll')
    aps.get_leaf('Gd09').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Bu12').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bu12').add_creature('Lion')
    aps.get_leaf('Bk02').split(2, 'Bk10', 7)
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Gr11').reveal_creatures(['Troll'])
    aps.get_leaf('Gr11').add_creature('Troll')
    aps.get_leaf('Gd07').split(2, 'Gd02', 7)
    aps.get_leaf('Gd09').split(2, 'Gd06', 7)
    aps.get_leaf('Gd07').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd07').add_creature('Gorgon')
    aps.get_leaf('Bk10').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bk10').add_creature('Gargoyle')
    aps.get_leaf('Gr10').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr10').add_creature('Cyclops')
    aps.get_leaf('Gd07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Gd02').reveal_creatures(['Centaur'])
    aps.get_leaf('Gd02').add_creature('Centaur')
    aps.get_leaf('Gd06').reveal_creatures(('Ogre', 'Ogre'))
    aps.get_leaf('Gd06').reveal_creatures(('Ogre', 'Ogre'))
    aps.get_leaf('Bu12').reveal_creatures(['Lion'])
    aps.get_leaf('Bu12').add_creature('Lion')
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Bk10').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bk10').add_creature('Cyclops')
    aps.get_leaf('Gr10').split(2, 'Gr01', 9)
    aps.get_leaf('Gd02').reveal_creatures(('Centaur', 'Centaur', 'Gargoyle'))
    aps.get_leaf('Gd07').split(2, 'Gd12', 9)
    aps.get_leaf('Gd07').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd07').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gr10').reveal_creatures(('Cyclops', 'Titan', 'Troll',
                                           'Troll', 'Warlock'))
    aps.get_leaf('Bu12').reveal_creatures(('Centaur', 'Centaur', 'Lion',
                                           'Lion', 'Titan', 'Warlock'))
    aps.get_leaf('Gr10').reveal_creatures(('Cyclops', 'Titan', 'Troll',
                                           'Troll', 'Warlock'))
    aps.get_leaf('Bu12').remove_creatures(['Centaur', 'Warlock', 'Centaur',
                                           'Lion', 'Lion'])
    aps.get_leaf('Gr10').remove_creatures(['Titan', 'Warlock', 'Cyclops',
                                           'Troll', 'Troll'])
    aps.get_leaf('Gr11').reveal_creatures(('Ogre', 'Ogre', 'Troll', 'Troll'))
    aps.get_leaf('Gr01').reveal_creatures(('Gargoyle', 'Gargoyle'))
    aps.get_leaf('Gr07').reveal_creatures(('Angel', 'Centaur', 'Centaur',
                                           'Lion', 'Lion'))
    aps.get_leaf('Gr02').reveal_creatures(('Ogre', 'Ogre'))
    aps.get_leaf('Bu12').add_creature('Angel')
    aps.get_leaf('Bk02').split(2, 'Bk09', 10)
    aps.get_leaf('Bk10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk10').add_creature('Cyclops')
    aps.get_leaf('Gd12').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd12').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Bk10').reveal_creatures(['Ogre'])
    aps.get_leaf('Bk10').add_creature('Ogre')
    aps.get_leaf('Gd09').split(2, 'Gd08', 11)
    aps.get_leaf('Gd08').reveal_creatures(['Troll'])
    aps.get_leaf('Gd08').add_creature('Troll')
    aps.get_leaf('Gd07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Bk09').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk09').add_creature('Cyclops')
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Bk10').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bk10').add_creature('Gorgon')
    aps.get_leaf('Gd12').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gd12').add_creature('Gorgon')
    aps.get_leaf('Gd08').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd08').add_creature('Ranger')
    aps.get_leaf('Bk02').split(2, 'Bk07', 13)
    aps.get_leaf('Bk10').split(2, 'Bk04', 13)
    aps.get_leaf('Gd07').split(2, 'Gd05', 13)
    aps.get_leaf('Bk07').reveal_creatures(('Cyclops', 'Gorgon'))
    aps.get_leaf('Gd12').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd12').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Ranger')
    aps.get_leaf('Bk10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk10').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Bk04').reveal_creatures(['Ogre'])
    aps.get_leaf('Bk04').add_creature('Ogre')
    aps.get_leaf('Bk09').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk09').add_creature('Cyclops')
    aps.get_leaf('Gd09').split(2, 'Gd03', 15)
    aps.get_leaf('Gd05').reveal_creatures(('Cyclops', 'Cyclops'))
    aps.get_leaf('Bk02').reveal_creatures(('Angel', 'Gorgon', 'Gorgon',
                                           'Gorgon', 'Gorgon', 'Gorgon'))
    aps.get_leaf('Bk02').remove_creatures(['Gorgon'])
    aps.get_leaf('Gd05').remove_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Gd07').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd07').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Gd09').reveal_creatures(('Angel', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger', 'Ranger'))
    aps.get_leaf('Bu12').reveal_creatures(('Angel', 'Titan'))
    aps.get_leaf('Gd09').reveal_creatures(('Angel', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger', 'Ranger'))
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd09').remove_creatures(['Angel', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger'])
    aps.get_leaf('Bu12').remove_creatures(['Titan', 'Angel'])
    aps.get_leaf('Bk04').reveal_creatures(['Ogre', 'Ogre', 'Ogre'])
    aps.get_leaf('Bk04').add_creature('Minotaur')
    aps.get_leaf('Gd12').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd12').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd08').add_creature('Warbear')
    aps.get_leaf('Bk09').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bk09').add_creature('Gorgon')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Bk02').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk02').add_creature('Gorgon')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Bk09').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk09').add_creature('Gorgon')
    aps.get_leaf('Gd12').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd12').add_creature('Cyclops')
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Ranger')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger', 'Ranger', 'Ranger'])
    aps.get_leaf('Gd03').add_creature('Guardian')
    aps.get_leaf('Gd12').split(2, 'Gd10', 22)
    aps.get_leaf('Gd08').split(2, 'Gd06', 22)
    aps.get_leaf('Gd07').split(2, 'Gd01', 22)
    aps.get_leaf('Gd03').split(2, 'Gd05', 22)
    aps.get_leaf('Gd12').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd12').add_creature('Gorgon')
    aps.get_leaf('Gd08').reveal_creatures(['Warbear'])
    aps.get_leaf('Gd08').add_creature('Warbear')
    aps.get_leaf('Gd05').reveal_creatures(['Troll'])
    aps.get_leaf('Gd05').add_creature('Troll')
    aps.get_leaf('Gd06').reveal_creatures(['Troll'])
    aps.get_leaf('Gd06').add_creature('Troll')
    aps.get_leaf('Gd10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd10').add_creature('Cyclops')
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Ranger')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd05').add_creature('Ranger')
    aps.get_leaf('Gd06').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd06').add_creature('Ranger')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Bk04').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Bk04').add_creature('Troll')
    aps.get_leaf('Bk09').reveal_creatures(['Cyclops', 'Cyclops', 'Cyclops'])
    aps.get_leaf('Bk09').add_creature('Behemoth')
    aps.get_leaf('Gd08').split(2, 'Gd04', 24)
    aps.get_leaf('Gd12').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd12').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd05').add_creature('Ranger')
    aps.get_leaf('Gd01').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gd01').add_creature('Gorgon')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Gd03').split(2, 'Gd02', 25)
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Warbear', 'Warbear'])
    aps.get_leaf('Gd08').add_creature('Unicorn')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd05').add_creature('Ranger')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Ranger')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Ranger')
    aps.get_leaf('Gd12').split(2, 'Gd11', 26)
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Ranger')
    aps.get_leaf('Gd08').split(2, 'Bu07', 27)
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Unicorn'])
    aps.get_leaf('Gd08').add_creature('Unicorn')
    aps.get_leaf('Gd04').reveal_creatures(['Troll'])
    aps.get_leaf('Gd04').add_creature('Troll')
    aps.get_leaf('Gd07').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd07').add_creature('Gorgon')
    aps.get_leaf('Gd06').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd06').add_creature('Warbear')
    aps.get_leaf('Gd01').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd01').add_creature('Gorgon')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Troll')
    aps.get_leaf('Bk10').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk10').add_creature('Gorgon')
    aps.get_leaf('Bk04').reveal_creatures(['Troll'])
    aps.get_leaf('Bk04').add_creature('Troll')
    aps.get_leaf('Gd10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd10').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gd11').add_creature('Gorgon')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Troll')
    aps.get_leaf('Gd06').reveal_creatures(['Warbear'])
    aps.get_leaf('Gd06').add_creature('Warbear')
    aps.get_leaf('Gd01').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd01').add_creature('Gorgon')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Troll')
    aps.get_leaf('Bk10').split(2, 'Bk08', 29)
    aps.get_leaf('Bk09').split(2, 'Bk05', 29)
    aps.get_leaf('Bk04').reveal_creatures(['Minotaur'])
    aps.get_leaf('Bk04').add_creature('Minotaur')
    aps.get_leaf('Gd09').split(2, 'Bu09', 29)
    aps.get_leaf('Gd08').split(2, 'Gr04', 29)
    aps.get_leaf('Bk08').reveal_creatures(('Gargoyle', 'Gargoyle'))
    aps.get_leaf('Bu07').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu07').add_creature('Lion')
    aps.get_leaf('Gd11').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd11').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd09').add_creature('Troll')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Troll')
    aps.get_leaf('Bu09').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu09').add_creature('Lion')
    aps.get_leaf('Gr04').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr04').add_creature('Troll')
    aps.get_leaf('Bu07').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu07').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd08').add_creature('Lion')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd05').add_creature('Troll')
    aps.get_leaf('Gd05').split(2, 'Bu06', 31)
    aps.get_leaf('Bu09').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu09').add_creature('Troll')
    aps.get_leaf('Gr04').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr04').add_creature('Troll')
    aps.get_leaf('Bu07').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu07').add_creature('Troll')
    aps.get_leaf('Bu06').reveal_creatures(['Troll'])
    aps.get_leaf('Bu06').add_creature('Troll')
    aps.get_leaf('Gd12').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd12').add_creature('Cyclops')
    aps.get_leaf('Gd09').reveal_creatures(['Troll'])
    aps.get_leaf('Gd09').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Unicorn'])
    aps.get_leaf('Gd08').add_creature('Unicorn')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd05').add_creature('Troll')
    aps.get_leaf('Gd01').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd01').add_creature('Cyclops')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Lion')
    aps.get_leaf('Gd02').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd02').add_creature('Warbear')
    aps.get_leaf('Bk09').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bk09').add_creature('Cyclops')
    aps.get_leaf('Gd08').split(2, 'Gr10', 32)
    aps.get_leaf('Gd03').split(2, 'Br10', 32)
    aps.get_leaf('Br10').reveal_creatures(['Lion'])
    aps.get_leaf('Br10').add_creature('Lion')
    aps.get_leaf('Bu09').reveal_creatures([])
    aps.get_leaf('Bu09').add_creature('Gargoyle')
    aps.get_leaf('Gr10').reveal_creatures(['Lion'])
    aps.get_leaf('Gr10').add_creature('Lion')
    aps.get_leaf('Gd05').reveal_creatures(['Ranger', 'Ranger', 'Ranger'])
    aps.get_leaf('Gd05').add_creature('Guardian')
    aps.get_leaf('Gd04').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd04').add_creature('Ogre')
    aps.get_leaf('Gd06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd06').add_creature('Lion')
    aps.get_leaf('Gd03').reveal_creatures(['Guardian'])
    aps.get_leaf('Gd03').add_creature('Guardian')
    aps.get_leaf('Gd06').split(2, 'Gr05', 33)
    aps.get_leaf('Gd02').split(2, 'Bu11', 33)
    aps.get_leaf('Bk05').reveal_creatures(('Cyclops', 'Gargoyle'))
    aps.get_leaf('Gd03').add_creature('Angel')
    aps.get_leaf('Br10').reveal_creatures(['Lion'])
    aps.get_leaf('Br10').add_creature('Lion')
    aps.get_leaf('Gr10').reveal_creatures(['Lion'])
    aps.get_leaf('Gr10').add_creature('Lion')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Ogre')
    aps.get_leaf('Br10').reveal_creatures(['Lion', 'Lion', 'Lion'])
    aps.get_leaf('Br10').add_creature('Griffon')
    aps.get_leaf('Gr10').reveal_creatures(['Lion', 'Lion', 'Lion'])
    aps.get_leaf('Gr10').add_creature('Griffon')
    aps.get_leaf('Bk04').split(2, 'Bk08', 35)
    aps.get_leaf('Bu11').reveal_creatures(('Troll', 'Troll'))
    aps.get_leaf('Bk04').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Bk04').add_creature('Warbear')
    aps.get_leaf('Br10').reveal_creatures(['Ranger'])
    aps.get_leaf('Br10').add_creature('Ogre')
    aps.get_leaf('Bu09').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu09').add_creature('Lion')
    aps.get_leaf('Gr10').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr10').add_creature('Ogre')
    aps.get_leaf('Gd10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd10').add_creature('Cyclops')
    aps.get_leaf('Gd04').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd04').add_creature('Warbear')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger', 'Ranger', 'Ranger'])
    aps.get_leaf('Gd02').add_creature('Guardian')
    aps.get_leaf('Bk10').reveal_creatures(['Cyclops', 'Cyclops', 'Cyclops'])
    aps.get_leaf('Bk10').add_creature('Behemoth')
    aps.get_leaf('Gd02').split(2, 'Br09', 36)
    aps.get_leaf('Bu07').reveal_creatures(['Ranger'])
    aps.get_leaf('Bu07').add_creature('Lion')
    aps.get_leaf('Bu06').reveal_creatures(['Troll', 'Troll', 'Troll'])
    aps.get_leaf('Bu06').add_creature('Wyvern')
    aps.get_leaf('Gd12').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd12').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd11').add_creature('Cyclops')
    aps.get_leaf('Gd08').reveal_creatures(['Unicorn'])
    aps.get_leaf('Gd08').add_creature('Unicorn')
    aps.get_leaf('Gd07').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd07').add_creature('Cyclops')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Lion')
    aps.get_leaf('Bk04').reveal_creatures(['Minotaur', 'Minotaur'])
    aps.get_leaf('Bk04').add_creature('Unicorn')
    aps.get_leaf('Br10').reveal_creatures(['Lion', 'Lion'])
    aps.get_leaf('Br10').add_creature('Minotaur')
    aps.get_leaf('Br09').reveal_creatures(['Troll'])
    aps.get_leaf('Br09').add_creature('Ogre')
    aps.get_leaf('Bu09').reveal_creatures(['Lion'])
    aps.get_leaf('Bu09').add_creature('Lion')
    aps.get_leaf('Gr04').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr04').add_creature('Ogre')
    aps.get_leaf('Gr10').reveal_creatures(['Lion', 'Lion'])
    aps.get_leaf('Gr10').add_creature('Minotaur')
    aps.get_leaf('Gd10').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd10').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd11').add_creature('Cyclops')
    aps.get_leaf('Gd04').reveal_creatures(['Warbear'])
    aps.get_leaf('Gd04').add_creature('Warbear')
    aps.get_leaf('Bk04').split(2, 'Bk06', 38)
    aps.get_leaf('Bk04').reveal_creatures(['Unicorn'])
    aps.get_leaf('Bk04').add_creature('Unicorn')
    aps.get_leaf('Bk08').reveal_creatures(['Ogre'])
    aps.get_leaf('Bk08').add_creature('Ogre')
    aps.get_leaf('Gd06').reveal_creatures(('Ranger', 'Troll', 'Troll',
                                           'Warbear', 'Warbear'))
    aps.get_leaf('Bk04').reveal_creatures(('Minotaur', 'Minotaur', 'Troll',
                                           'Unicorn', 'Unicorn', 'Warbear'))
    aps.get_leaf('Gd03').reveal_creatures(['Angel'])
    aps.get_leaf('Gd03').reveal_creatures(['Angel'])
    aps.get_leaf('Gd03').remove_creature('Angel')
    aps.get_leaf('Gd06').add_creature('Angel')
    aps.get_leaf('Bk04').reveal_creatures(['Unicorn'])
    aps.get_leaf('Bk04').add_creature('Unicorn')
    aps.get_leaf('Bk04').remove_creatures(['Warbear', 'Minotaur', 'Minotaur',
                                           'Troll'])
    aps.get_leaf('Gd06').remove_creatures(['Warbear', 'Warbear', 'Ranger',
                                           'Troll', 'Troll', 'Angel'])
    aps.get_leaf('Bk04').add_creature('Angel')
    aps.get_leaf('Bk04').add_creature('Angel')
    aps.get_leaf('Gr04').reveal_creatures(['Troll', 'Troll', 'Troll'])
    aps.get_leaf('Gr04').add_creature('Guardian')
    aps.get_leaf('Bu07').reveal_creatures(['Lion'])
    aps.get_leaf('Bu07').add_creature('Lion')
    aps.get_leaf('Gd04').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd04').add_creature('Lion')
    aps.get_leaf('Bk08').reveal_creatures(['Ogre', 'Ogre', 'Ogre'])
    aps.get_leaf('Bk08').add_creature('Guardian')
    aps.get_leaf('Bu07').split(2, 'Gd06', 39)
    aps.get_leaf('Gr10').split(2, 'Br07', 39)
    aps.get_leaf('Gd04').split(2, 'Br06', 39)
    aps.get_leaf('Bk06').reveal_creatures(('Ogre', 'Troll'))
    aps.get_leaf('Gd04').reveal_creatures(['Warbear', 'Warbear'])
    aps.get_leaf('Gd04').add_creature('Unicorn')
    aps.get_leaf('Gd03').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd03').add_creature('Lion')
    aps.get_leaf('Gd02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd02').add_creature('Lion')
    aps.get_leaf('Gr04').reveal_creatures(['Troll', 'Troll', 'Troll'])
    aps.get_leaf('Gr04').add_creature('Wyvern')
    aps.get_leaf('Bu07').reveal_creatures(['Lion'])
    aps.get_leaf('Bu07').add_creature('Lion')
    aps.get_leaf('Gr10').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr10').add_creature('Lion')
    aps.get_leaf('Gd06').reveal_creatures(('Lion', 'Lion'))
    aps.get_leaf('Gr04').split(2, 'Gd06', 40)
    aps.get_leaf('Bu09').split(2, 'Bu11', 40)
    aps.get_leaf('Br10').split(2, 'Bu08', 40)
    aps.get_leaf('Bu11').reveal_creatures(['Lion'])
    aps.get_leaf('Bu11').add_creature('Lion')
    aps.get_leaf('Gd06').reveal_creatures(['Ogre'])
    aps.get_leaf('Gd06').add_creature('Ogre')
    aps.get_leaf('Bu08').reveal_creatures(['Lion'])
    aps.get_leaf('Bu08').add_creature('Lion')
    aps.get_leaf('Gr10').reveal_creatures([])
    aps.get_leaf('Gr10').add_creature('Gargoyle')
    aps.get_leaf('Bk04').reveal_creatures(('Angel', 'Angel', 'Unicorn',
                                           'Unicorn', 'Unicorn'))
    aps.get_leaf('Gr04').reveal_creatures(('Guardian', 'Ranger', 'Troll',
                                           'Troll', 'Wyvern'))
    aps.get_leaf('Bk02').reveal_creatures(['Angel'])
    aps.get_leaf('Bk02').remove_creature('Angel')
    aps.get_leaf('Bk04').add_creature('Angel')
    aps.get_leaf('Bk04').reveal_creatures(['Angel'])
    aps.get_leaf('Bk04').remove_creature('Angel')
    aps.get_leaf('Bk02').add_creature('Angel')
    aps.get_leaf('Bk02').reveal_creatures(['Angel'])
    aps.get_leaf('Bk02').remove_creature('Angel')
    aps.get_leaf('Bk04').add_creature('Angel')


def test_predict_splits12():
    aps = AllPredictSplits()
    ps = PredictSplits('ai3', 'Gr08', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai2', 'Br03', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai6', 'Gd11', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai5', 'Bu06', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai1', 'Bk03', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    ps = PredictSplits('ai4', 'Rd08', ('Titan', 'Angel', 'Ogre', 'Ogre',
                                       'Centaur', 'Centaur',
                                       'Gargoyle', 'Gargoyle'))
    aps.append(ps)
    aps.get_leaf('Gr08').split(4, 'Gr02', 1)
    aps.get_leaf('Gr08').reveal_creatures(['Angel', 'Centaur', 'Gargoyle',
                                           'Gargoyle'])
    aps.get_leaf('Gr02').reveal_creatures(['Titan', 'Ogre', 'Ogre', 'Centaur'])
    aps.get_leaf('Gr02').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gr02').add_creature('Troll')
    aps.get_leaf('Gr08').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr08').add_creature('Cyclops')
    aps.get_leaf('Br03').split(4, 'Br07', 1)
    aps.get_leaf('Br03').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Br03').add_creature('Troll')
    aps.get_leaf('Br07').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Br07').add_creature('Lion')
    aps.get_leaf('Gd11').split(4, 'Gd08', 1)
    aps.get_leaf('Gd11').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gd11').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Gd08').add_creature('Gargoyle')
    aps.get_leaf('Bu06').split(4, 'Bu05', 1)
    aps.get_leaf('Bu06').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bu06').add_creature('Lion')
    aps.get_leaf('Bu05').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bu05').add_creature('Cyclops')
    aps.get_leaf('Bk03').split(4, 'Bk07', 1)
    aps.get_leaf('Bk07').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bk07').add_creature('Cyclops')
    aps.get_leaf('Rd08').split(4, 'Rd04', 1)
    aps.get_leaf('Rd04').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Rd04').add_creature('Gargoyle')
    aps.get_leaf('Rd08').reveal_creatures(['Titan'])
    aps.get_leaf('Rd08').add_creature('Warlock')
    aps.get_leaf('Gr02').reveal_creatures(['Troll'])
    aps.get_leaf('Gr02').add_creature('Troll')
    aps.get_leaf('Br03').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Br03').add_creature('Gargoyle')
    aps.get_leaf('Gd11').reveal_creatures(['Troll'])
    aps.get_leaf('Gd11').add_creature('Troll')
    aps.get_leaf('Bu06').reveal_creatures(['Ogre'])
    aps.get_leaf('Bu06').add_creature('Ogre')
    aps.get_leaf('Bk03').reveal_creatures(['Centaur'])
    aps.get_leaf('Bk03').add_creature('Centaur')
    aps.get_leaf('Bk07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk07').add_creature('Cyclops')
    aps.get_leaf('Rd04').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Rd04').add_creature('Lion')
    aps.get_leaf('Rd08').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Rd08').add_creature('Gargoyle')
    aps.get_leaf('Gr02').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Gr08').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gr08').add_creature('Cyclops')
    aps.get_leaf('Br03').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Br03').add_creature('Cyclops')
    aps.get_leaf('Br07').reveal_creatures(['Lion'])
    aps.get_leaf('Br07').add_creature('Lion')
    aps.get_leaf('Gd08').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gd08').add_creature('Cyclops')
    aps.get_leaf('Bu06').reveal_creatures(['Lion'])
    aps.get_leaf('Bu06').add_creature('Lion')
    aps.get_leaf('Bu05').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bu05').add_creature('Cyclops')
    aps.get_leaf('Bk03').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bk03').add_creature('Lion')
    aps.get_leaf('Bk07').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bk07').add_creature('Gorgon')
    aps.get_leaf('Rd04').reveal_creatures(['Centaur'])
    aps.get_leaf('Rd04').add_creature('Centaur')
    aps.get_leaf('Rd08').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Rd08').add_creature('Cyclops')
    aps.get_leaf('Gr02').split(2, 'Gr05', 4)
    aps.get_leaf('Gr02').reveal_creatures(['Titan', 'Ranger', 'Troll', 'Troll',
                                           'Centaur'])
    aps.get_leaf('Gr05').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Gr08').reveal_creatures([])
    aps.get_leaf('Gr08').add_creature('Gargoyle')
    aps.get_leaf('Br03').split(2, 'Br12', 4)
    aps.get_leaf('Br03').reveal_creatures(['Cyclops'])
    aps.get_leaf('Br03').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd11').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures([])
    aps.get_leaf('Gd08').add_creature('Gargoyle')
    aps.get_leaf('Bu06').split(2, 'Bu10', 4)
    aps.get_leaf('Bu05').reveal_creatures(['Ogre'])
    aps.get_leaf('Bu05').add_creature('Ogre')
    aps.get_leaf('Bk07').split(2, 'Bk05', 4)
    aps.get_leaf('Bk03').reveal_creatures(['Lion'])
    aps.get_leaf('Bk03').add_creature('Lion')
    aps.get_leaf('Bk05').reveal_creatures(['Centaur'])
    aps.get_leaf('Bk05').add_creature('Centaur')
    aps.get_leaf('Rd04').split(2, 'Rd03', 4)
    aps.get_leaf('Rd08').split(2, 'Rd02', 4)
    aps.get_leaf('Gr08').split(2, 'Gr11', 5)
    aps.get_leaf('Gr08').reveal_creatures(['Angel', 'Cyclops', 'Cyclops',
                                           'Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr11').reveal_creatures(['Gargoyle', 'Centaur'])
    aps.get_leaf('Rd03').reveal_creatures(('Centaur', 'Centaur'))
    aps.get_leaf('Gr08').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gr08').add_creature('Gorgon')
    aps.get_leaf('Gr11').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Gr11').add_creature('Gargoyle')
    aps.get_leaf('Br07').reveal_creatures(('Angel', 'Centaur', 'Centaur',
                                           'Gargoyle', 'Lion', 'Lion'))
    aps.get_leaf('Br03').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Br03').add_creature('Gorgon')
    aps.get_leaf('Br07').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Br07').add_creature('Gargoyle')
    aps.get_leaf('Gd11').split(2, 'Gd09', 5)
    aps.get_leaf('Gd08').split(2, 'Gd03', 5)
    aps.get_leaf('Gd11').reveal_creatures(('Gargoyle', 'Ranger', 'Titan',
                                           'Troll', 'Troll'))
    aps.get_leaf('Rd04').reveal_creatures(('Angel', 'Centaur', 'Gargoyle',
                                           'Gargoyle', 'Lion'))
    aps.get_leaf('Gd11').reveal_creatures(('Gargoyle', 'Ranger', 'Titan',
                                           'Troll', 'Troll'))
    aps.get_leaf('Rd04').reveal_creatures(('Angel', 'Centaur', 'Gargoyle',
                                           'Gargoyle', 'Lion'))
    aps.get_leaf('Gd08').reveal_creatures(['Angel'])
    aps.get_leaf('Gd08').reveal_creatures(['Angel'])
    aps.get_leaf('Gd08').remove_creature('Angel')
    aps.get_leaf('Gd11').add_creature('Angel')
    aps.get_leaf('Gd11').remove_creatures(['Ranger', 'Troll', 'Gargoyle'])
    aps.get_leaf('Rd04').remove_creatures(['Angel', 'Lion', 'Gargoyle',
                                           'Gargoyle', 'Centaur'])
    aps.get_leaf('Gd08').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd08').add_creature('Cyclops')
    aps.get_leaf('Bu05').split(2, 'Bu07', 5)
    aps.get_leaf('Bu05').reveal_creatures(['Titan'])
    aps.get_leaf('Bu05').add_creature('Warlock')
    aps.get_leaf('Bk03').split(2, 'Bk08', 5)
    aps.get_leaf('Bk03').reveal_creatures(['Lion', 'Lion'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Bk05').reveal_creatures(['Centaur'])
    aps.get_leaf('Bk05').add_creature('Centaur')
    aps.get_leaf('Br03').split(2, 'Br09', 6)
    aps.get_leaf('Br07').split(2, 'Br02', 6)
    aps.get_leaf('Br07').reveal_creatures(['Lion', 'Lion'])
    aps.get_leaf('Br07').add_creature('Ranger')
    aps.get_leaf('Gd03').reveal_creatures(('Centaur', 'Centaur'))
    aps.get_leaf('Rd08').reveal_creatures(('Cyclops', 'Gargoyle', 'Gargoyle',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Gd03').reveal_creatures(('Centaur', 'Centaur'))
    aps.get_leaf('Rd08').reveal_creatures(('Cyclops', 'Gargoyle', 'Gargoyle',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Gd11').reveal_creatures(['Angel'])
    aps.get_leaf('Gd11').reveal_creatures(['Angel'])
    aps.get_leaf('Gd11').remove_creature('Angel')
    aps.get_leaf('Gd03').add_creature('Angel')
    aps.get_leaf('Rd08').remove_creatures(['Warlock', 'Cyclops', 'Gargoyle',
                                           'Gargoyle'])
    aps.get_leaf('Gd03').remove_creatures(['Centaur', 'Centaur', 'Angel'])
    aps.get_leaf('Bu05').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bu05').add_creature('Gorgon')
    aps.get_leaf('Bk07').reveal_creatures(('Angel', 'Cyclops', 'Cyclops',
                                           'Gargoyle', 'Gorgon'))
    aps.get_leaf('Bu06').reveal_creatures(('Angel', 'Centaur', 'Centaur',
                                           'Lion', 'Lion'))
    aps.get_leaf('Bk07').reveal_creatures(('Angel', 'Cyclops', 'Cyclops',
                                           'Gargoyle', 'Gorgon'))
    aps.get_leaf('Bu06').reveal_creatures(('Angel', 'Centaur', 'Centaur',
                                           'Lion', 'Lion'))
    aps.get_leaf('Bk07').remove_creatures(['Angel', 'Gorgon', 'Cyclops',
                                           'Gargoyle'])
    aps.get_leaf('Bu06').remove_creatures(['Angel', 'Lion', 'Lion', 'Centaur',
                                           'Centaur'])
    aps.get_leaf('Bk08').reveal_creatures(['Ogre'])
    aps.get_leaf('Bk08').add_creature('Ogre')
    aps.get_leaf('Bk07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bk07').add_creature('Cyclops')
    aps.get_leaf('Rd08').reveal_creatures(['Titan'])
    aps.get_leaf('Rd08').add_creature('Warlock')
    aps.get_leaf('Bu05').split(2, 'Bu04', 7)
    aps.get_leaf('Bu05').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bu05').add_creature('Gorgon')
    aps.get_leaf('Bk03').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Bk05').reveal_creatures(['Gargoyle'])
    aps.get_leaf('Bk05').add_creature('Gargoyle')
    aps.get_leaf('Gr02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Gr08').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gr08').add_creature('Gorgon')
    aps.get_leaf('Br02').reveal_creatures(('Centaur', 'Centaur'))
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Gorgon', 'Titan', 'Warlock'))
    aps.get_leaf('Br02').reveal_creatures(('Centaur', 'Centaur'))
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Gorgon', 'Titan', 'Warlock'))
    aps.get_leaf('Br02').remove_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bu05').reveal_creatures(['Gorgon'])
    aps.get_leaf('Bu05').add_creature('Gorgon')
    aps.get_leaf('Br09').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Br09').add_creature('Cyclops')
    aps.get_leaf('Br07').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Br07').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Troll'])
    aps.get_leaf('Gd11').add_creature('Troll')
    aps.get_leaf('Bu04').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bu04').add_creature('Cyclops')
    aps.get_leaf('Bk03').split(2, 'Bk11', 8)
    aps.get_leaf('Bk03').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Gr08').split(2, 'Gr12', 9)
    aps.get_leaf('Gr08').reveal_creatures(['Angel', 'Gorgon', 'Gorgon',
                                           'Cyclops', 'Cyclops'])
    aps.get_leaf('Gr12').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr12').reveal_creatures([])
    aps.get_leaf('Gr12').add_creature('Centaur')
    aps.get_leaf('Br07').split(2, 'Br08', 9)
    aps.get_leaf('Br03').reveal_creatures(['Cyclops'])
    aps.get_leaf('Br03').add_creature('Cyclops')
    aps.get_leaf('Br09').reveal_creatures(['Cyclops'])
    aps.get_leaf('Br09').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd11').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gd08').add_creature('Gorgon')
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Gorgon', 'Gorgon',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Br07').reveal_creatures(('Angel', 'Cyclops', 'Lion', 'Lion',
                                           'Ranger'))
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Gorgon', 'Gorgon',
                                           'Titan', 'Warlock'))
    aps.get_leaf('Br07').reveal_creatures(('Angel', 'Cyclops', 'Lion', 'Lion',
                                           'Ranger'))
    aps.get_leaf('Bu05').remove_creatures(['Warlock', 'Gorgon', 'Gorgon'])
    aps.get_leaf('Br07').remove_creatures(['Angel', 'Cyclops', 'Ranger',
                                           'Lion', 'Lion'])
    aps.get_leaf('Bu05').add_creature('Angel')
    aps.get_leaf('Bu05').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bu05').add_creature('Cyclops')
    aps.get_leaf('Bk03').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Bk05').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bk05').add_creature('Lion')
    aps.get_leaf('Gr02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Br09').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Br09').add_creature('Gorgon')
    aps.get_leaf('Bu04').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bu04').add_creature('Cyclops')
    aps.get_leaf('Bk03').split(2, 'Bk04', 10)
    aps.get_leaf('Bk03').reveal_creatures(['Ranger', 'Ranger', 'Ranger'])
    aps.get_leaf('Bk03').add_creature('Guardian')
    aps.get_leaf('Rd08').reveal_creatures(('Titan', 'Warlock'))
    aps.get_leaf('Gd11').reveal_creatures(('Ranger', 'Titan', 'Troll',
                                           'Troll'))
    aps.get_leaf('Rd08').reveal_creatures(('Titan', 'Warlock'))
    aps.get_leaf('Gd11').reveal_creatures(('Ranger', 'Titan', 'Troll',
                                           'Troll'))
    aps.get_leaf('Gd11').reveal_creatures(['Troll'])
    aps.get_leaf('Gd11').add_creature('Troll')
    aps.get_leaf('Gd11').remove_creatures(['Troll', 'Ranger'])
    aps.get_leaf('Rd08').remove_creatures(['Titan', 'Warlock'])
    aps.get_leaf('Gd11').add_creature('Angel')
    aps.get_leaf('Gr02').split(2, 'Gr09', 11)
    aps.get_leaf('Gr02').reveal_creatures(['Titan', 'Ranger', 'Ranger',
                                           'Ranger', 'Troll'])
    aps.get_leaf('Gr09').reveal_creatures(['Troll', 'Centaur'])
    aps.get_leaf('Gr02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Gr05').reveal_creatures(['Ogre'])
    aps.get_leaf('Gr05').add_creature('Ogre')
    aps.get_leaf('Br08').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Br08').add_creature('Cyclops')
    aps.get_leaf('Bk05').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Bk05').add_creature('Cyclops')
    aps.get_leaf('Br08').reveal_creatures(('Cyclops', 'Gargoyle', 'Gargoyle'))
    aps.get_leaf('Gr08').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gr08').add_creature('Gorgon')
    aps.get_leaf('Gr12').reveal_creatures(['Centaur'])
    aps.get_leaf('Gr12').add_creature('Centaur')
    aps.get_leaf('Br12').reveal_creatures(['Ogre', 'Ogre'])
    aps.get_leaf('Br12').add_creature('Troll')
    aps.get_leaf('Br09').reveal_creatures(['Gorgon'])
    aps.get_leaf('Br09').add_creature('Gorgon')
    aps.get_leaf('Bk03').reveal_creatures(['Guardian'])
    aps.get_leaf('Bk03').add_creature('Guardian')
    aps.get_leaf('Gr02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Gr12').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Gr12').add_creature('Lion')
    aps.get_leaf('Br09').reveal_creatures(('Cyclops', 'Cyclops', 'Gargoyle',
                                           'Gargoyle', 'Gorgon', 'Gorgon'))
    aps.get_leaf('Br03').reveal_creatures(['Troll'])
    aps.get_leaf('Br03').add_creature('Troll')
    aps.get_leaf('Br09').reveal_creatures(['Cyclops'])
    aps.get_leaf('Br09').add_creature('Cyclops')
    aps.get_leaf('Gd11').reveal_creatures(['Troll'])
    aps.get_leaf('Gd11').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gd08').add_creature('Cyclops')
    aps.get_leaf('Bk03').split(2, 'Bk10', 13)
    aps.get_leaf('Bk03').reveal_creatures(['Guardian'])
    aps.get_leaf('Bk03').add_creature('Guardian')
    aps.get_leaf('Bk10').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk10').add_creature('Ranger')
    aps.get_leaf('Gr02').split(2, 'Gr06', 14)
    aps.get_leaf('Gr02').reveal_creatures(['Titan', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger'])
    aps.get_leaf('Gr06').reveal_creatures(['Ranger', 'Troll'])
    aps.get_leaf('Gr12').reveal_creatures(['Lion'])
    aps.get_leaf('Gr12').add_creature('Lion')
    aps.get_leaf('Gr06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr06').add_creature('Ranger')
    aps.get_leaf('Br03').split(2, 'Br06', 14)
    aps.get_leaf('Br09').reveal_creatures(('Cyclops', 'Cyclops', 'Cyclops',
                                           'Gargoyle', 'Gargoyle',
                                           'Gorgon', 'Gorgon'))
    aps.get_leaf('Bu05').reveal_creatures(('Angel', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon', 'Titan'))
    aps.get_leaf('Br09').reveal_creatures(('Cyclops', 'Cyclops', 'Cyclops',
                                           'Gargoyle', 'Gargoyle',
                                           'Gorgon', 'Gorgon'))
    aps.get_leaf('Bu05').reveal_creatures(('Angel', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon', 'Titan'))
    aps.get_leaf('Bu05').remove_creatures(['Cyclops', 'Cyclops', 'Gorgon',
                                           'Angel'])
    aps.get_leaf('Br09').remove_creatures(['Gargoyle', 'Gargoyle', 'Cyclops',
                                           'Cyclops', 'Gorgon',
                                           'Gorgon', 'Cyclops'])
    aps.get_leaf('Bu05').add_creature('Angel')
    aps.get_leaf('Gd08').split(2, 'Gd10', 14)
    aps.get_leaf('Bu04').reveal_creatures(('Cyclops', 'Cyclops', 'Gargoyle',
                                           'Gargoyle'))
    aps.get_leaf('Bk05').reveal_creatures(('Centaur', 'Centaur', 'Centaur',
                                           'Cyclops', 'Gargoyle',
                                           'Gargoyle', 'Lion'))
    aps.get_leaf('Bu05').reveal_creatures(['Angel'])
    aps.get_leaf('Bu05').reveal_creatures(['Angel'])
    aps.get_leaf('Bu05').remove_creature('Angel')
    aps.get_leaf('Bu04').add_creature('Angel')
    aps.get_leaf('Bk05').remove_creatures(['Gargoyle', 'Centaur', 'Centaur',
                                           'Gargoyle', 'Lion', 'Cyclops'])
    aps.get_leaf('Bu04').remove_creatures(['Gargoyle', 'Gargoyle', 'Cyclops',
                                           'Cyclops', 'Angel'])
    aps.get_leaf('Bk05').add_creature('Angel')
    aps.get_leaf('Bk11').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Bk11').add_creature('Lion')
    aps.get_leaf('Gr08').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gr08').add_creature('Gorgon')
    aps.get_leaf('Gr12').reveal_creatures(['Lion', 'Lion'])
    aps.get_leaf('Gr12').add_creature('Ranger')
    aps.get_leaf('Gd08').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gd08').add_creature('Gorgon')
    aps.get_leaf('Bk03').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Gr08').split(2, 'Gr07', 16)
    aps.get_leaf('Gr08').reveal_creatures(['Angel', 'Gorgon', 'Gorgon',
                                           'Gorgon', 'Gorgon'])
    aps.get_leaf('Gr07').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gr12').split(2, 'Gr10', 16)
    aps.get_leaf('Gr12').reveal_creatures(['Ranger', 'Lion', 'Lion',
                                           'Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr10').reveal_creatures(['Centaur', 'Centaur'])
    aps.get_leaf('Gr09').reveal_creatures(['Centaur'])
    aps.get_leaf('Gr09').add_creature('Centaur')
    aps.get_leaf('Gr12').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr12').add_creature('Cyclops')
    aps.get_leaf('Gr07').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gr07').add_creature('Cyclops')
    aps.get_leaf('Gr06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr06').add_creature('Ranger')
    aps.get_leaf('Br03').reveal_creatures(['Gorgon'])
    aps.get_leaf('Br03').add_creature('Gorgon')
    aps.get_leaf('Br06').reveal_creatures(['Troll'])
    aps.get_leaf('Br06').add_creature('Troll')
    aps.get_leaf('Gd08').reveal_creatures(['Cyclops', 'Cyclops', 'Cyclops'])
    aps.get_leaf('Gd08').add_creature('Behemoth')
    aps.get_leaf('Bu05').reveal_creatures(['Cyclops'])
    aps.get_leaf('Bu05').add_creature('Cyclops')
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger'))
    aps.get_leaf('Bk10').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk10').add_creature('Ranger')
    aps.get_leaf('Bk11').reveal_creatures(['Lion'])
    aps.get_leaf('Bk11').add_creature('Lion')
    aps.get_leaf('Gr12').reveal_creatures(['Cyclops'])
    aps.get_leaf('Gr12').add_creature('Cyclops')
    aps.get_leaf('Gr06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr06').add_creature('Ranger')
    aps.get_leaf('Gd10').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gd10').add_creature('Cyclops')
    aps.get_leaf('Gr12').split(2, 'Gr04', 18)
    aps.get_leaf('Gr12').reveal_creatures(['Cyclops', 'Cyclops', 'Ranger',
                                           'Lion', 'Lion'])
    aps.get_leaf('Gr04').reveal_creatures(['Gargoyle', 'Gargoyle'])
    aps.get_leaf('Gr12').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr12').add_creature('Ranger')
    aps.get_leaf('Gr06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr06').add_creature('Ranger')
    aps.get_leaf('Gd08').split(2, 'Gd07', 18)
    aps.get_leaf('Bu05').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Bu05').add_creature('Gorgon')
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger'))
    aps.get_leaf('Bk11').reveal_creatures(('Centaur', 'Centaur', 'Lion',
                                           'Lion'))
    aps.get_leaf('Gr09').reveal_creatures(['Troll'])
    aps.get_leaf('Gr09').add_creature('Troll')
    aps.get_leaf('Gr08').reveal_creatures(['Gorgon'])
    aps.get_leaf('Gr08').add_creature('Gorgon')
    aps.get_leaf('Br03').reveal_creatures(['Cyclops', 'Cyclops', 'Cyclops'])
    aps.get_leaf('Br03').add_creature('Behemoth')
    aps.get_leaf('Br06').reveal_creatures(['Troll', 'Troll', 'Troll'])
    aps.get_leaf('Br06').add_creature('Wyvern')
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Titan'))
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Titan'))
    aps.get_leaf('Gr02').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger', 'Titan'))
    aps.get_leaf('Bu05').reveal_creatures(('Cyclops', 'Cyclops', 'Gorgon',
                                           'Titan'))
    aps.get_leaf('Gr02').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger', 'Titan'))
    aps.get_leaf('Gr02').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr02').add_creature('Ranger')
    aps.get_leaf('Gr02').remove_creatures(['Ranger', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger'])
    aps.get_leaf('Bu05').remove_creatures(['Titan', 'Cyclops', 'Cyclops',
                                           'Gorgon'])
    aps.get_leaf('Gr02').add_creature('Angel')
    aps.get_leaf('Br06').reveal_creatures(('Troll', 'Troll', 'Troll',
                                           'Wyvern'))
    aps.get_leaf('Br03').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon',
                                           'Gorgon', 'Titan'))
    aps.get_leaf('Br03').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon',
                                           'Gorgon', 'Titan'))
    aps.get_leaf('Gr08').reveal_creatures(('Angel', 'Gorgon', 'Gorgon',
                                           'Gorgon', 'Gorgon', 'Gorgon'))
    aps.get_leaf('Br03').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon',
                                           'Gorgon', 'Titan'))
    aps.get_leaf('Gr08').reveal_creatures(('Angel', 'Gorgon', 'Gorgon',
                                           'Gorgon', 'Gorgon', 'Gorgon'))
    aps.get_leaf('Br03').remove_creatures(['Gorgon', 'Cyclops', 'Cyclops',
                                           'Gorgon', 'Behemoth'])
    aps.get_leaf('Gr08').remove_creatures(['Angel', 'Gorgon', 'Gorgon',
                                           'Gorgon', 'Gorgon', 'Gorgon'])
    aps.get_leaf('Br03').add_creature('Angel')
    aps.get_leaf('Gr07').reveal_creatures(['Cyclops', 'Cyclops', 'Cyclops'])
    aps.get_leaf('Gr07').add_creature('Behemoth')
    aps.get_leaf('Gd11').reveal_creatures(['Troll', 'Troll'])
    aps.get_leaf('Gd11').add_creature('Ranger')
    aps.get_leaf('Gr12').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gr12').add_creature('Gorgon')
    aps.get_leaf('Gr07').reveal_creatures(['Cyclops', 'Cyclops'])
    aps.get_leaf('Gr07').add_creature('Gorgon')
    aps.get_leaf('Gr06').reveal_creatures(['Ranger'])
    aps.get_leaf('Gr06').add_creature('Ranger')
    aps.get_leaf('Gd11').reveal_creatures(('Angel', 'Ranger', 'Titan', 'Troll',
                                           'Troll', 'Troll'))
    aps.get_leaf('Gd11').reveal_creatures(['Ranger'])
    aps.get_leaf('Gd11').add_creature('Ranger')
    aps.get_leaf('Bk03').split(2, 'Bk09', 22)
    aps.get_leaf('Bk09').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk09').add_creature('Ranger')
    aps.get_leaf('Gr06').split(2, 'Gr05', 23)
    aps.get_leaf('Gr06').reveal_creatures(['Ranger', 'Ranger', 'Ranger',
                                           'Ranger', 'Ranger'])
    aps.get_leaf('Gr05').reveal_creatures(['Ranger', 'Troll'])
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger'))
    aps.get_leaf('Gr07').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon'))
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger'))
    aps.get_leaf('Gr02').reveal_creatures(['Angel'])
    aps.get_leaf('Gr02').reveal_creatures(['Angel'])
    aps.get_leaf('Gr02').remove_creature('Angel')
    aps.get_leaf('Gr07').add_creature('Angel')
    aps.get_leaf('Gr07').reveal_creatures(['Angel'])
    aps.get_leaf('Gr07').remove_creature('Angel')
    aps.get_leaf('Gr02').add_creature('Angel')
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger'))
    aps.get_leaf('Gr07').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Cyclops', 'Gorgon'))
    aps.get_leaf('Bk10').reveal_creatures(('Ranger', 'Ranger', 'Ranger',
                                           'Ranger'))
    aps.get_leaf('Gr07').add_creature('Angel')
    aps.get_leaf('Gr02').reveal_creatures(['Titan'])
    aps.get_leaf('Gr02').add_creature('Warlock')
    aps.get_leaf('Gr07').reveal_creatures(['Behemoth'])
    aps.get_leaf('Gr07').add_creature('Behemoth')
    aps.get_leaf('Gd11').split(2, 'Gd09', 23)
    aps.get_leaf('Gd08').reveal_creatures(('Behemoth', 'Cyclops', 'Cyclops',
                                           'Gorgon', 'Gorgon'))
    aps.get_leaf('Gd08').add_creature('Angel')
    aps.get_leaf('Bk03').reveal_creatures(['Ranger'])
    aps.get_leaf('Bk03').add_creature('Ranger')
    aps.get_leaf('Gr12').split(2, 'Gr11', 24)
    aps.get_leaf('Gr12').reveal_creatures(['Gorgon', 'Cyclops', 'Cyclops',
                                           'Ranger', 'Ranger'])
    aps.get_leaf('Gr11').reveal_creatures(['Lion', 'Lion'])
    aps.print_leaves()
