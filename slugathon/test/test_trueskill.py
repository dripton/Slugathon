__copyright__ = "Copyright (c) 2012 David Ripton"
__license__ = "GNU GPL v2"


import trueskill


def test_6_players_no_draws():
    r1 = trueskill.Rating()
    r2 = trueskill.Rating()
    r3 = trueskill.Rating()
    r4 = trueskill.Rating()
    r5 = trueskill.Rating()
    r6 = trueskill.Rating()
    sigma0 = r1.sigma
    [(r1, ), (r2, ), (r3, ), (r4, ), (r5, ), (r6, )] = \
        trueskill.rate([(r1, ), (r2, ), (r3, ), (r4, ), (r5, ),
                        (r6, )])
    assert r1.mu > r2.mu > r3.mu > r4.mu > r5.mu > r6.mu
    for rating in [r1, r2, r3, r4, r5, r6]:
        assert rating.sigma < sigma0


def test_3_player_draw():
    r1 = trueskill.Rating()
    r2 = trueskill.Rating()
    r3 = trueskill.Rating()
    sigma0 = r1.sigma
    [(r1, ), (r2, ), (r3, )] = trueskill.rate([(r1, ),
                                              (r2, ),
                                              (r3, )],
                                              ranks=(1, 1, 3))
    # We would hope it would be zero, but trueskill isn't that accurate.
    assert abs(r1.mu - r2.mu) < 0.01
    assert r1.mu > r3.mu
    assert r2.mu > r3.mu
    for rating in [r1, r2, r3]:
        assert rating.sigma < sigma0
