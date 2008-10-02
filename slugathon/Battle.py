from Observed import Observed
import BattleMap

class Battle(Observed):
    def __init__(self, game, attacker_legion, defender_legion):
        Observed.__init__(self)
        self.game = game
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        assert defender_legion.hexlabel == attacker_legion.hexlabel
        self.hexlabel = attacker_legion.hexlabel
        self.masterhex = self.game.board.hexes[self.hexlabel]
        self.entry_side = attacker_legion.entry_side
        self.battlemap = BattleMap.BattleMap(self.masterhex.terrain,
          self.entry_side)
