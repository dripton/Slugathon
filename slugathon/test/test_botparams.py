__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.ai import BotParams


def test_default_bot_params():
    bp = BotParams.default_bot_params
    assert bp.SQUASH == 0.6


def test_mutate_field():
    bp = BotParams.default_bot_params
    for unused in range(10):
        bp2 = bp.mutate_field("SQUASH", ratio=0.25)
        assert 0.45 <= bp2.SQUASH <= 0.75


def test_mutate_random_field():
    bp = BotParams.default_bot_params
    for unused in range(10):
        count = 0
        bp2 = bp.mutate_random_field(ratio=0.25)
        for field in bp._fields:
            if getattr(bp, field) != getattr(bp2, field):
                count += 1
        assert count == 1


def test_mutate_all_fields():
    bp = BotParams.default_bot_params
    for unused in range(10):
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


def test_fromstring_complete():
    st = """version=2 ai_time_limit=5 BotParams(SQUASH=0.6, BE_SQUASHED=1.0,
    FLEE_RATIO=1.5, ATTACKER_AGGRESSION_BONUS=1.0,
    ATTACKER_DISTANCE_PENALTY=-1.0, HIT_BONUS=1.0, KILL_MULTIPLIER=1.0,
    DAMAGE_PENALTY=-1.0, DEATH_MULTIPLIER=-1.0, ELEVATION_BONUS=0.5,
    NATIVE_BRAMBLE_BONUS=0.3, NON_NATIVE_BRAMBLE_PENALTY=-0.7, TOWER_BONUS=1.0,
    FRONT_OF_TOWER_BONUS=0.5, MIDDLE_OF_TOWER_BONUS=0.25,
    CENTER_OF_TOWER_BONUS=1.0, TITAN_IN_CENTER_OF_TOWER_BONUS=2.0,
    NON_NATIVE_DRIFT_PENALTY=-2.0, NATIVE_VOLCANO_BONUS=1.0,
    ADJACENT_ALLY_BONUS=0.5, RANGESTRIKE_BONUS=2.0, TITAN_FORWARD_PENALTY=-1.0,
    DEFENDER_FORWARD_PENALTY=-0.5, NATIVE_SLOPE_BONUS=0.5,
    NATIVE_DUNE_BONUS=0.5, NON_NATIVE_SLOPE_PENALTY=-0.3,
    NON_NATIVE_DUNE_PENALTY=-0.3, ENGAGE_RANGESTRIKER_BONUS=0.5,
    THIRD_CREATURE_RATIO=0.6)"""
    st = st.replace("\n", "")
    bp = BotParams.BotParams.fromstring(st)
    assert bp is not None
    assert bp.SQUASH == 0.6


def test_fromstring_incomplete():
    st = """version=2 ai_time_limit=5 BotParams(SQUASH=0.6, BE_SQUASHED=1.0,
    FLEE_RATIO=1.5, ATTACKER_AGGRESSION_BONUS=1.0,
    ATTACKER_DISTANCE_PENALTY=-1.0, HIT_BONUS=1.0, KILL_MULTIPLIER=1.0,
    DAMAGE_PENALTY=-1.0, DEATH_MULTIPLIER=-1.0, ELEVATION_BONUS=0.5,
    NATIVE_BRAMBLE_BONUS=0.3, NON_NATIVE_BRAMBLE_PENALTY=-0.7, TOWER_BONUS=1.0,
    FRONT_OF_TOWER_BONUS=0.5, MIDDLE_OF_TOWER_BONUS=0.25,
    CENTER_OF_TOWER_BONUS=1.0, TITAN_IN_CENTER_OF_TOWER_BONUS=2.0,
    NON_NATIVE_DRIFT_PENALTY=-2.0, NATIVE_VOLCANO_BONUS=1.0,
    ADJACENT_ALLY_BONUS=0.5, RANGESTRIKE_BONUS=2.0, TITAN_FORWARD_PENALTY=-1.0,
    DEFENDER_FORWARD_PENALTY=-0.5, NATIVE_SLOPE_BONUS=0.5,
    NATIVE_DUNE_BONUS=0.5, NON_NATIVE_SLOPE_PENALTY=-0.3,
    NON_NATIVE_DUNE_PENALTY=-0.3, ENGAGE_RANGESTRIKER_BONUS=0.5)"""
    st = st.replace("\n", "")
    bp = BotParams.BotParams.fromstring(st)
    assert bp is not None
    assert bp.SQUASH == 0.6
