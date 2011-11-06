__copyright__ = "Copyright (c) 2011 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.ai import CleverBot


def test_gen_legion_moves():
    cleverbot = CleverBot.CleverBot("player")

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
