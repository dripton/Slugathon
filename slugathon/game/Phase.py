__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


"""Phase constants"""

# Master
SPLIT, MOVE, FIGHT, MUSTER = range(4)

# Battle
REINFORCE, MANEUVER, DRIFTDAMAGE, STRIKE, COUNTERSTRIKE, CLEANUP = range(6)

phase_names = {
    SPLIT:  "Split",
    MOVE:   "Move",
    FIGHT:  "Fight",
    MUSTER: "Muster",
}

battle_phase_names = {
    REINFORCE: "Reinforce",
    MANEUVER: "Maneuver",
    DRIFTDAMAGE: "Drift damage",
    STRIKE: "Strike",
    COUNTERSTRIKE: "Counterstrike",
    CLEANUP: "Cleanup",
}
