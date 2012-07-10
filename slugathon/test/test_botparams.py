__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.ai import BotParams


def test_default_bot_params():
    bp = BotParams.default_bot_params
    assert bp.SQUASH == 0.6


def test_mutate_field():
    bp = BotParams.default_bot_params
    for unused in xrange(10):
        bp2 = bp.mutate_field("SQUASH", ratio=0.25)
        assert 0.45 <= bp2.SQUASH <= 0.75


def test_mutate_random_field():
    bp = BotParams.default_bot_params
    for unused in xrange(10):
        count = 0
        bp2 = bp.mutate_random_field(ratio=0.25)
        for field in bp._fields:
            if getattr(bp, field) != getattr(bp2, field):
                count += 1
        assert count == 1


def test_mutate_all_fields():
    bp = BotParams.default_bot_params
    for unused in xrange(10):
        bp2 = bp.mutate_all_fields(ratio=0.25)
        for field in bp._fields:
            assert getattr(bp, field) != getattr(bp2, field)


def test_cross_degenerate():
    bp1 = BotParams.default_bot_params
    bp2 = BotParams.default_bot_params
    bp3 = bp1.cross(bp2)
    assert bp3 == bp1


def test_cross():
    bp1 = BotParams.default_bot_params
    bp2 = BotParams.default_bot_params.mutate_all_fields()
    bp3 = bp1.cross(bp2)
    assert bp3 != bp1
    assert bp3 != bp2
    for field in bp3._fields:
        val1 = getattr(bp1, field)
        val2 = getattr(bp2, field)
        val3 = getattr(bp3, field)
        assert val3 >= min(val1, val2)
        assert val3 <= max(val1, val2)
