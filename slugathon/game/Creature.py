__copyright__ = "Copyright (c) 2003-2009 David Ripton"
__license__ = "GNU GPL v2"


from slugathon.data import creaturedata, recruitdata, battlemapdata
from slugathon.game import Phase


def _terrain_to_hazards():
    """Return a dict of masterboard terrain type to a set of all
    battle hazards (hex and hexside) found there."""
    result = {}
    for mterrain, dic2 in battlemapdata.data.iteritems():
        for hexlabel, (bterrain, elevation, dic3) in dic2.iteritems():
            set1 = result.setdefault(mterrain, set())
            set1.add(bterrain)
            for hexside, border in dic3.iteritems():
                if border:
                    set1.add(border)
    return result

def _terrain_to_creature_names():
    """Return a dict of masterboard terrain type to a set of all
    Creature names that can be recruited there."""
    result = {}
    for terrain, tuples in recruitdata.data.iteritems():
        set1 = set()
        result[terrain] = set1
        for tup in tuples:
            if tup:
                creature_name, count = tup
                if count:
                    set1.add(creature_name)
    return result

def _compute_nativity():
    """Return a dict of creature name to a set of all hazards
    (battle terrain types and border types) to which it is
    native."""
    result = {}
    terrain_to_creature_names = _terrain_to_creature_names()
    terrain_to_hazards = _terrain_to_hazards()
    for terrain, creature_names in terrain_to_creature_names.iteritems():
        hazards = terrain_to_hazards.get(terrain, set())
        for creature_name in creature_names:
            set1 = result.setdefault(creature_name, set())
            for hazard in hazards:
                # Special case: Only Dragon is native to Volcano
                if hazard != "Volcano" or creature_name == "Dragon":
                    set1.add(hazard)
    return result

creature_name_to_native_hazards = _compute_nativity()


def n2c(names):
    """Make a list of Creatures from a list of creature names"""
    return [Creature(name) for name in names]


class Creature(object):
    """One instance of one Creature, Lord, or Demi-Lord."""
    def __init__(self, name):
        self.name = name
        (self.plural_name, self._power, self.skill, rangestrikes, self.flies,
          self.character_type, self.summonable, self.acquirable_every,
          self.max_count, self.color_name) = creaturedata.data[name]
        self.rangestrikes = bool(rangestrikes)
        self.magicmissile = (rangestrikes == 2)
        self.acquirable = bool(self.acquirable_every)
        self.hits = 0
        self.moved = False
        self.struck = False
        self.hexlabel = None
        self.previous_hexlabel = None
        self.legion = None

    @property
    def power(self):
        if self.name == "Titan" and self.legion is not None:
            return self.legion.player.titan_power()
        else:
            return self._power

    @property
    def dead(self):
        return self.hits >= self.power

    def __repr__(self):
        if self.name == "Titan":
            base = "%s(%d)" % (self.name, self.power)
        else:
            base = self.name
        if self.hexlabel is not None:
            return "%s in %s" % (base, self.hexlabel)
        else:
            return base

    @property
    def score(self):
        """Return the point value of this creature."""
        return self.power * self.skill

    @property
    def sort_value(self):
        """Return a rough indication of creature value, for sorting."""
        return (self.score
          + 0.2 * self.acquirable
          + 0.3 * self.flies
          + 0.25 * self.rangestrikes
          + 0.1 * self.magicmissile
          + 0.15 * (self.skill == 2)
          + 0.18 * (self.skill == 4)
          + 100 * (self.name == "Titan"))

    @property
    def is_lord(self):
        return self.character_type == "lord"

    def _hexlabel_to_enemy(self):
        """Return a dict of hexlabel: live enemy Creature"""
        hexlabel_to_enemy = {}
        game = self.legion.player.game
        legion2 = game.other_battle_legion(self.legion)
        for creature in legion2.creatures:
            if not creature.dead and not creature.offboard:
                hexlabel_to_enemy[creature.hexlabel] = creature
        return hexlabel_to_enemy

    def _hexlabel_to_dead_enemy(self):
        """Return a dict of hexlabel: dead enemy Creature"""
        hexlabel_to_enemy = {}
        game = self.legion.player.game
        legion2 = game.other_battle_legion(self.legion)
        for creature in legion2.creatures:
            if creature.dead and not creature.offboard:
                hexlabel_to_enemy[creature.hexlabel] = creature
        return hexlabel_to_enemy

    @property
    def engaged_enemies(self):
        """Return a set of live enemy Creatures this Creature is engaged
        with."""
        enemies = set()
        if self.offboard or self.hexlabel is None:
            return enemies
        game = self.legion.player.game
        hex1 = game.battlemap.hexes[self.hexlabel]
        hexlabel_to_enemy = self._hexlabel_to_enemy()
        for hexside, hex2 in hex1.neighbors.iteritems():
            if hex2.label in hexlabel_to_enemy:
                if (hex1.borders[hexside] != "Cliff" and
                  hex2.borders[(hexside + 3) % 6] != "Cliff"):
                    enemies.add(hexlabel_to_enemy[hex2.label])
        return enemies

    @property
    def dead_adjacent_enemies(self):
        """Return a set of dead enemy Creatures this Creature is engaged
        with."""
        enemies = set()
        if self.offboard or self.hexlabel is None:
            return enemies
        game = self.legion.player.game
        hex1 = game.battlemap.hexes[self.hexlabel]
        hexlabel_to_enemy = self._hexlabel_to_dead_enemy()
        for hexside, hex2 in hex1.neighbors.iteritems():
            if hex2.label in hexlabel_to_enemy:
                if (hex1.borders[hexside] != "Cliff" and
                  hex2.borders[(hexside + 3) % 6] != "Cliff"):
                    enemies.add(hexlabel_to_enemy[hex2.label])
        return enemies


    def has_los_to(self, hexlabel):
        """Return True iff this creature has line of sight to the
        hex with hexlabel."""
        game = self.legion.player.game
        map1 = game.battlemap
        return not map1.is_los_blocked(self.hexlabel, hexlabel, game)

    @property
    def rangestrike_targets(self):
        """Return a set of Creatures that this Creature can rangestrike."""
        game = self.legion.player.game
        enemies = set()
        if (self.offboard or self.hexlabel is None or not self.rangestrikes
          or game.battle_phase != Phase.STRIKE or self.dead_adjacent_enemies):
            return enemies
        hexlabel_to_enemy = self._hexlabel_to_enemy()
        map1 = game.battlemap
        for hexlabel, enemy in hexlabel_to_enemy.iteritems():
            if (map1.range(self.hexlabel, hexlabel) <= self.skill and
              (self.magicmissile or self.has_los_to(hexlabel)) and
              (self.magicmissile or enemy.character_type != "lord")):
                enemies.add(enemy)
        return enemies

    def find_target_hexlabels(self):
        """Return a set of hexlabels containing creatures that this creature
        can strike or rangestrike."""
        hexlabels = set()
        legion = self.legion
        player = legion.player
        game = player.game
        if not self.struck:
            for target in self.engaged_enemies:
                hexlabels.add(target.hexlabel)
            if (not hexlabels and self.rangestrikes and
              game.battle_phase == Phase.STRIKE and not
              self.dead_adjacent_enemies):
                for target in self.rangestrike_targets:
                    hexlabels.add(target.hexlabel)
        return hexlabels

    @property
    def engaged(self):
        """Return True iff this creature is engaged with an adjacent enemy."""
        return bool(self.engaged_enemies)

    @property
    def mobile(self):
        """Return True iff this creature can move."""
        return not self.moved and not self.dead and not self.engaged

    def is_native(self, hazard):
        """Return True iff this creature is native to the named hazard.

        Note that we define nativity even for hazards that don't provide any
        benefit for being native, like Wall and Plain.
        """
        return hazard in creature_name_to_native_hazards.get(self.name, set())

    def move(self, hexlabel):
        """Move this creature to a new battle hex"""
        self.previous_hexlabel = self.hexlabel
        self.hexlabel = hexlabel
        self.moved = True

    def undo_move(self):
        """Undo this creature's last battle move."""
        assert self.moved and self.previous_hexlabel
        self.hexlabel = self.previous_hexlabel
        self.previous_hexlabel = None
        self.moved = False

    @property
    def can_strike(self):
        """Return True iff this creature can strike."""
        return not self.struck and (self.engaged or self.can_rangestrike)

    @property
    def can_rangestrike(self):
        """Return True iff this creature can rangestrike an enemy."""
        return bool(self.rangestrike_targets)

    def number_of_dice(self, target):
        """Return the number of dice to use if striking target."""
        map1 = self.legion.player.game.battlemap
        hex1 = map1.hexes[self.hexlabel]
        hex2 = map1.hexes[target.hexlabel]
        if target in self.engaged_enemies:
            dice = self.power
            if hex1.terrain == "Volcano" and self.is_native(hex1.terrain):
                dice += 2
            hexside = hex1.neighbor_to_hexside(hex2)
            border = hex1.borders[hexside]
            if border == "Slope" and self.is_native(border):
                dice += 1
            elif border == "Dune" and self.is_native(border):
                dice += 2
            border2 = hex1.opposite_border(hexside)
            if border2 == "Dune" and not self.is_native(border2):
                dice -= 1
        elif target in self.rangestrike_targets:
            dice = int(self.power / 2)
            if hex1.terrain == "Volcano" and self.is_native(hex1.terrain):
                dice += 2
        else:
            dice = 0
        return dice

    def strike_number(self, target):
        """Return the strike number to use if striking target."""
        game = self.legion.player.game
        map1 = game.battlemap
        hex1 = map1.hexes[self.hexlabel]
        hex2 = map1.hexes[target.hexlabel]
        skill1 = self.skill
        skill2 = target.skill
        if target in self.engaged_enemies:
            hexside = hex1.neighbor_to_hexside(hex2)
            border = hex1.borders[hexside]
            border2 = hex1.opposite_border(hexside)
            if hex1.terrain == "Bramble" and not self.is_native(hex1.terrain):
                skill1 -= 1
            elif border == "Wall":
                skill1 += 1
            elif border2 == "Slope" and not self.is_native(border2):
                skill1 -= 1
            elif border2 == "Wall":
                skill1 -= 1
        else:
            # Long range rangestrike penalty
            if (not self.magicmissile and map1.range(self.hexlabel,
              target.hexlabel) >= 4):
                skill1 -= 1
            if not self.magicmissile and not self.is_native("Bramble"):
                skill1 -= map1.count_bramble_hexes(self.hexlabel,
                  target.hexlabel, game)
            if not self.magicmissile:
                skill1 -= map1.count_walls(self.hexlabel, target.hexlabel,
                  game)
        strike_number = 4 - skill1 + skill2
        if target in self.engaged_enemies:
            if (hex2.terrain == "Bramble" and not self.is_native(hex2.terrain)
              and target.is_native(hex2.terrain)):
                strike_number += 1
        else:
            if (hex2.terrain == "Bramble" and target.is_native(hex2.terrain)
              and not self.is_native(hex2.terrain)):
                strike_number += 1
            elif (hex2.terrain == "Volcano" and target.is_native(
              hex2.terrain)):
                strike_number += 1
        strike_number = min(strike_number, 6)
        return strike_number

    # TODO Handle special case for natives striking up dune hexside
    def can_carry_to(self, carry_target, original_target, num_dice,
      strike_number):
        """Return whether a strike at original_target using num_dice and
        strike number can carry to carry_target"""
        return (carry_target is not original_target and
          carry_target in self.engaged_enemies and
          self.number_of_dice(carry_target) >= num_dice and
          self.strike_number(carry_target) <= strike_number)

    def max_possible_carries(self, target, num_dice, strike_number):
        """Return the maximum number of useful carries for the given target,
        number of dice, and strike_number.

        It will be zero if there are no other adjacent living enemies.
        """
        max_carries = 0
        for creature in self.engaged_enemies:
            if self.can_carry_to(creature, target, num_dice, strike_number):
                max_carries += creature.power - creature.hits
        return max_carries

    def can_take_strike_penalty(self, target):
        """Return True if it's legal to take a strike penalty when striking
        target."""
        num_dice = self.number_of_dice(target)
        strike_number = self.strike_number(target)
        for creature in self.engaged_enemies:
            if creature is not target:
                num_dice2 = self.number_of_dice(creature)
                strike_number2 = self.strike_number(creature)
                if num_dice2 < num_dice or strike_number2 > strike_number:
                    if num_dice2 > target.power - target.hits:
                        return True
        return False

    @property
    def offboard(self):
        return self.hexlabel == "ATTACKER" or self.hexlabel == "DEFENDER"

    def heal(self):
        self.hits = 0

    def kill(self):
        self.hits = self.power
