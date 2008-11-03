"""
Fredrik Lundh, comp.lang.python, 2005-11-22
"""

import py

from reval import reval

def test_reval_good():
    assert reval("{'test':'123','hehe':['hooray',0x10]}") == \
      {'test': '123', 'hehe': ['hooray', 16]}

def test_reval_good2():
    dicstr = "{'markername': 'Rd01', 'entry_side': 1, 'teleport': False, \
'playername': 'player', 'teleporting_lord': None, 'game_name': 'game',\
'hexlabel': 1}"
    assert reval(dicstr) == eval(dicstr)

def test_reval_error():
    try:
        reval("{'test':'123','hehe':['hooray',0x10 ** 20 ** 30]}")
    except SyntaxError:
        pass
    else:
        py.test.fail("should have raised")
