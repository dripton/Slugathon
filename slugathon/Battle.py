import sys

from Observed import Observed
import BattleMap
import Phase

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
        self.turn = 1
        self.phase = Phase.MANEUVER
        self.active_player = self.defender_legion.player
        self.defender_legion.enter_battle("DEFENDER")
        self.attacker_legion.enter_battle("ATTACKER")
        self.legions = [self.defender_legion, self.attacker_legion]

    def is_hex_occupied(self, hexlabel):
        """Return True iff there's a creature in the hex with hexlabel."""
        for legion in self.legions:
            for creature in legion.creatures:
                if creature.hexlabel == hexlabel:
                    return True
        return False

    def hex_entry_cost(self, creature, terrain, border):
        """Return the cost for creature to enter a battle hex with terrain,
        crossing border.  For fliers, this means landing in the hex, not
        just flying over it.

        If the creature cannot enter the hex, return sys.maxint.
        
        This does not take other creatures in the hex into account.
        """
        cost = 1
        if terrain in ["Tree"]:
            return sys.maxint
        elif terrain in ["Bog", "Volcano"]:
            if not creature.is_native(terrain):
                return sys.maxint
        elif terrain in ["Bramble", "Drift", "Sand"]:
            if not creature.is_native(terrain):
                cost += 1
        if border in ["Slope", "Wall"]:
            if not creature.is_native(border) and not creature.flies:
                cost += 1
        elif border in ["Cliff"]:
            if not creature.flies:
                return sys.maxint
        return cost

    def hex_flyover_cost(self, creature, terrain):
        """Return the cost for creature to fly over the hex with terrain.  
        This does not include landing in the hex.

        If the creature cannot fly over the hex, return sys.maxint.
        """
        if not creature.flies:
            return sys.maxint
        if terrain in ["Volcano"]:
            if not creature.is_native(terrain):
                return sys.maxint
        return 1

    def _find_moves_inner(self, creature, hexlabel, movement_left):
        """Return a set of all hexlabels to which creature can move,
        starting from hexlabel, with movement_left.
        
        Do not include hexlabel itself.
        """
        result = set()
        if movement_left <= 0:
            return result
        hex1 = self.battlemap.hexes[hexlabel]
        for hexside, hex2 in hex1.neighbors.iteritems():
            if not self.is_hex_occupied(hex2.label):
                if hex1.entrance:
                    # Ignore hexside penalties from entrances.
                    border = None
                else:
                    reverse_dir = (hexside + 3) % 6
                    border = hex2.borders[reverse_dir]
                cost = self.hex_entry_cost(creature, hex2.terrain, border)
                if cost <= movement_left:
                    result.add(hex2.label)
                if creature.flies:
                    flyover_cost = self.hex_flyover_cost(creature, 
                      hex2.terrain)
                    if flyover_cost < movement_left:
                        result.update(self._find_moves_inner(creature, 
                          hex2.label, movement_left - flyover_cost))
                else:
                    if cost < movement_left: 
                        result.update(self._find_moves_inner(creature, 
                          hex2.label, movement_left - cost))
        result.discard(hexlabel)
        return result

    def find_moves(self, creature):
        """Return a set of all hexlabels to which creature can move,
        excluding its current hex"""
        result = set()
        if creature.moved or creature.is_engaged():
            return result
        hexlabel = creature.hexlabel
        if (self.turn == 1 and creature.legion == self.defender_legion
          and self.battlemap.startlist):
            for hexlabel2 in self.battlemap.startlist:
                if not self.is_hex_occupied(hexlabel2):
                    result.add(hexlabel2)
            return result
        return self._find_moves_inner(creature, hexlabel, creature.skill)

