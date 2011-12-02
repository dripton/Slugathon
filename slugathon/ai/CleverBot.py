__copyright__ = "Copyright (c) 2010-2011 David Ripton"
__license__ = "GNU GPL v2"


"""An attempt at a smarter AI."""


import random
import copy
import time
from sys import maxint
import itertools
import traceback

from slugathon.ai import DimBot
from slugathon.game import Game, Creature
from slugathon.util.log import log


SQUASH = 0.6
BE_SQUASHED = 1.0


def best7(score_moves):
    """Return a set of the the best (highest score) (up to) 7 moves from
    score_moves, which is a sorted list of (score, move) tuples.

    If there's a tie, pick at random.
    """
    score_moves = score_moves[:]
    best_moves = set()
    while score_moves and len(best_moves) < 7:
        choices = []
        best_score = score_moves[-1][0]
        for (score, move) in reversed(score_moves):
            if score == best_score:
                choices.append((score, move))
            else:
                break
        (score, move) = random.choice(choices)
        score_moves.remove((score, move))
        best_moves.add(move)
    return best_moves


class CleverBot(DimBot.DimBot):
    def __init__(self, playername, time_limit):
        DimBot.DimBot.__init__(self, playername)
        self.time_limit = time_limit
        self.best_moves = []
        self.best_creature_moves = None

    def split(self, game):
        """Split if it's my turn."""
        log("split")
        if game.active_player.name != self.playername:
            log("called split out of turn; exiting")
            return
        player = game.active_player
        legions = player.legions.values()
        caretaker = game.caretaker
        for legion in legions:
            if len(legion) == 8:
                # initial split 4-4, one lord per legion
                new_markerid = self._choose_marker(player)
                lord = random.choice(["Titan", "Angel"])
                creatures = ["Centaur", "Gargoyle", "Ogre"]
                creature1 = random.choice(creatures)
                creature2 = creature1
                creature3 = creature1
                while creature3 == creature1:
                    creature3 = random.choice(creatures)
                new_creatures = [lord, creature1, creature2, creature3]
                old_creatures = legion.creature_names
                for creature in new_creatures:
                    old_creatures.remove(creature)
                def1 = self.user.callRemote("split_legion", game.name,
                  legion.markerid, new_markerid,
                  old_creatures, new_creatures)
                def1.addErrback(self.failure)
                return
            elif len(legion) == 7 and player.markerids:
                good_recruit_rolls = set()
                safe_split_rolls = set()
                lst = legion.sorted_creatures
                for roll in xrange(1, 6 + 1):
                    moves = game.find_all_moves(legion,
                      game.board.hexes[legion.hexlabel], roll)
                    for hexlabel, entry_side in moves:
                        masterhex = game.board.hexes[hexlabel]
                        terrain = masterhex.terrain
                        recruits = legion.available_recruits(terrain,
                          caretaker)
                        if recruits:
                            recruit = Creature.Creature(recruits[-1])
                            if recruit.sort_value > lst[-1].sort_value:
                                good_recruit_rolls.add(roll)
                        enemies = player.enemy_legions(hexlabel)
                        if enemies:
                            enemy = enemies.pop()
                            if (enemy.combat_value < SQUASH *
                              legion.combat_value):
                                safe_split_rolls.add(roll)
                        else:
                            safe_split_rolls.add(roll)
                if good_recruit_rolls and len(safe_split_rolls) == 6:
                    split = lst[-2:]
                    split_names = [creature.name for creature in split]
                    keep = lst[:-2]
                    keep_names = [creature.name for creature in keep]
                    new_markerid = self._choose_marker(player)
                    def1 = self.user.callRemote("split_legion", game.name,
                      legion.markerid, new_markerid, keep_names,
                      split_names)
                    def1.addErrback(self.failure)
                    return

        # No splits, so move on to the next phase.
        def1 = self.user.callRemote("done_with_splits", game.name)
        def1.addErrback(self.failure)

    def move_legions(self, game):
        """Move one or more legions, and then end the Move phase."""
        log("move_legions")
        assert game.active_player.name == self.playername
        player = game.active_player
        legions = player.legions.values()
        if not player.moved_legions:
            # (score, legion, hexlabel, entry_side)
            self.best_moves = []
            for legion in legions:
                moves = game.find_all_moves(legion, game.board.hexes[
                  legion.hexlabel], player.movement_roll)
                for hexlabel, entry_side in moves:
                    try:
                        score = self._score_move(legion, hexlabel, True)
                    except Exception:
                        log(traceback.format_exc())
                        raise
                    self.best_moves.append(
                      (score, legion, hexlabel, entry_side))
            self.best_moves.sort()

            if player.can_take_mulligan:
                legions_with_good_moves = set()
                for (score, legion, _, _) in self.best_moves:
                    if score > 0:
                        legions_with_good_moves.add(legion)
                if len(legions_with_good_moves) < 2:
                    log("taking a mulligan")
                    def1 = self.user.callRemote("take_mulligan", game.name)
                    def1.addErrback(self.failure)
                    return

        log("best moves", self.best_moves)
        while self.best_moves:
            score, legion, hexlabel, entry_side = self.best_moves.pop()
            if (score > 0 or not player.moved_legions or
              len(player.friendly_legions(legion.hexlabel)) >= 2):
                # keeper; remove other moves for this legion, and moves
                # for other legions to this hex, and other teleports if
                # this move was a teleport.
                new_best_moves = [(score2, legion2, hexlabel2, entry_side2)
                  for (score2, legion2, hexlabel2, entry_side2) in
                  self.best_moves
                  if legion2 != legion and hexlabel2 != hexlabel and not
                  (entry_side == entry_side2 == Game.TELEPORT)]
                self.best_moves = new_best_moves
                if entry_side == Game.TELEPORT:
                    teleport = True
                    masterhex = game.board.hexes[hexlabel]
                    terrain = masterhex.terrain
                    if terrain == "Tower":
                        entry_side = 5
                    else:
                        entry_side = random.choice([1, 3, 5])
                    teleporting_lord = sorted(legion.lord_types)[-1]
                else:
                    teleport = False
                    teleporting_lord = None
                def1 = self.user.callRemote("move_legion", game.name,
                  legion.markerid, hexlabel, entry_side, teleport,
                  teleporting_lord)
                def1.addErrback(self.failure)
                return

        # No more legions will move.
        def1 = self.user.callRemote("done_with_moves", game.name)
        def1.addErrback(self.failure)

    def _score_move(self, legion, hexlabel, move):
        """Return a score for legion moving to (or staying in) hexlabel."""
        score = 0
        player = legion.player
        game = player.game
        caretaker = game.caretaker
        board = game.board
        enemies = player.enemy_legions(hexlabel)
        legion_combat_value = legion.combat_value
        legion_sort_value = legion.sort_value

        if enemies:
            assert len(enemies) == 1
            enemy = enemies.pop()
            enemy_combat_value = enemy.combat_value
            log("legion", legion, "hexlabel", hexlabel)
            log("legion_combat_value", legion_combat_value)
            log("enemy_combat_value", enemy_combat_value)
            if enemy_combat_value < SQUASH * legion_combat_value:
                score += enemy.score
            elif enemy_combat_value >= BE_SQUASHED * legion_combat_value:
                score -= legion_sort_value
        if move and (len(legion) < 7 or enemies):
            masterhex = board.hexes[hexlabel]
            terrain = masterhex.terrain
            recruits = legion.available_recruits(terrain, caretaker)
            if recruits:
                recruit_name = recruits[-1]
                recruit = Creature.Creature(recruit_name)
                score += recruit.sort_value
                log("recruit value", legion.markerid, hexlabel,
                  recruit.sort_value)
        try:
            prev_hexlabel = legion.hexlabel
            legion.hexlabel = hexlabel
            for enemy in player.enemy_legions():
                if enemy.combat_value >= BE_SQUASHED * legion_combat_value:
                    for roll in xrange(1, 6 + 1):
                        moves = game.find_normal_moves(enemy,
                          game.board.hexes[enemy.hexlabel], roll).union(
                          game.find_titan_teleport_moves(enemy))
                        hexlabels = set((move[0] for move in moves))
                        if hexlabel in hexlabels:
                            log("scared of %s in %s" % (enemy.markerid,
                              hexlabel))
                            score -= legion_sort_value / 6.0
        finally:
            legion.hexlabel = prev_hexlabel
        return score

    def _gen_legion_moves_inner(self, movesets):
        """Yield tuples of distinct hexlabels, one from each
        moveset, in order, with no duplicates.

        movesets is a list of sets of hexlabels, corresponding
        to the order of remaining creatures in the legion.
        """
        if not movesets:
            yield ()
        elif len(movesets) == 1:
            for move in movesets[0]:
                yield (move,)
        else:
            for move in movesets[0]:
                movesets1 = copy.deepcopy(movesets[1:])
                for moveset in movesets1:
                    moveset.discard(move)
                for moves in self._gen_legion_moves_inner(movesets1):
                    yield (move,) + moves

    def _gen_legion_moves(self, movesets):
        """Yield all possible legion_moves for movesets.

        movesets is a list of sets of hexlabels to which
        each Creature can move (or stay), in the same order as
        Legion.sorted_creatures.
        Like:
        creatures [titan1, ogre1, troll1]
        movesets [{"A1", "A2", "B1"}, {"B1", "B2"}, {"B1", "B3"}]

        A legion_move is a list of hexlabels, in the same order as
        creatures, where each Creature's hexlabel is one from its original
        list, and no two Creatures have the same hexlabel.  Like:
        ["A1", "B1", "B3"]
        """
        log("_gen_legion_moves", movesets)
        for moves in self._gen_legion_moves_inner(movesets):
            if len(moves) == len(movesets):
                yield list(moves)

    def _score_perm(self, game, sort_values, perm):
        """Score one move order permutation."""
        score = 0
        moved_creatures = set()
        try:
            for creature_name, start, move in perm:
                creature = game.creatures_in_battle_hex(start,
                  creature_name).pop()
                if (move == start or move in
                  game.find_battle_moves(creature)):
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = move
                    moved_creatures.add(creature)
                    score += sort_values[creature_name]
            return score
        finally:
            for creature in moved_creatures:
                creature.hexlabel = creature.previous_hexlabel
                creature.previous_hexlabel = None

    def _find_move_order(self, game, creature_moves):
        """Return a new list with creature_moves rearranged so that as
        many of the moves as possible can be legally made.

        creature_moves is a list of (creature_name, start_hexlabel,
        finish_hexlabel) tuples.
        """
        log("_find_move_order")
        max_score = 0
        sort_values = {}
        for creature_name, start, move in creature_moves:
            creature = game.creatures_in_battle_hex(start, creature_name).pop()
            sort_values[creature_name] = creature.sort_value
            max_score += creature.sort_value
        perms = list(itertools.permutations(creature_moves))
        # Scramble the list so we don't get a bunch of similar bad
        # orders jumbled together at the beginning.
        log("_find_move_order %d perms" % len(perms))
        random.shuffle(perms)
        best_score = -maxint
        best_perm = None
        start_time = time.time()
        for perm in perms:
            score = self._score_perm(game, sort_values, perm)
            if score == max_score:
                best_perm = perm
                log("_find_move_order found perfect order")
                break
            elif score > best_score:
                best_perm = perm
                best_score = score
            if time.time() - start_time > self.time_limit:
                break
        log("_find_move_order returning %s" % list(best_perm))
        return list(best_perm)

    def _find_best_creature_moves(self, game):
        """Return a list of up to one (creature_name, start_hexlabel,
        finish_hexlabel) tuple for each Creature in the battle active legion.

        Idea: Find all possible moves for each creature in the legion,
        ignoring mobile allies, and score them in isolation without knowing
        where its allies will end up.  Find the best 7 moves for each creature
        (because with up to 7 creatures in a legion, a creature may have to
        take its 7th-favorite move, and because 7! = 5040, not too big).
        Combine these into legion moves, and score those again, then take
        the best legion move.  Finally, find the order of creature moves
        that lets all the creatures reach their assigned hexes without
        blocking their allies' moves.
        """
        assert game.battle_active_player.name == self.playername
        legion = game.battle_active_legion
        log("_find_best_creature_moves", legion)
        movesets = []  # list of a set of hexlabels for each creature
        creatures = legion.sorted_living_creatures
        for creature in creatures:
            moves = game.find_battle_moves(creature, ignore_mobile_allies=True)
            if moves:
                score_moves = []
                # Not moving is also an option, unless offboard.
                if creature.hexlabel not in ["ATTACKER", "DEFENDER"]:
                    moves.add(creature.hexlabel)
                for move in moves:
                    try:
                        creature.previous_hexlabel = creature.hexlabel
                        creature.hexlabel = move
                        score = self._score_legion_move(game, [creature])
                        score_moves.append((score, move))
                    finally:
                        creature.hexlabel = creature.previous_hexlabel
                score_moves.sort()
                log("score_moves", creature, score_moves)
                moveset = best7(score_moves)
            else:
                moveset = set([creature.hexlabel])
            movesets.append(moveset)
        best_legion_move = None
        now = time.time()
        legion_moves = list(self._gen_legion_moves(movesets))
        log("found %d legion_moves in %fs" % (len(legion_moves), time.time() -
          now))
        best_score = -maxint
        start = time.time()
        # Scramble the moves, in case we don't have time to look at them all.
        random.shuffle(legion_moves)
        log("len(creatures) %d len(legion_moves[0]) %d" % (len(creatures),
          len(legion_moves[0])))
        for legion_move in legion_moves:
            try:
                for ii, creature in enumerate(creatures):
                    move = legion_move[ii]
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = move
                score = self._score_legion_move(game, creatures)
                if score > best_score:
                    best_legion_move = legion_move
                    best_score = score
                now = time.time()
                if now - start > self.time_limit:
                    break
            finally:
                for creature in creatures:
                    creature.hexlabel = creature.previous_hexlabel
        log("found best_legion_move %s in %fs" % (best_legion_move,
          now - start))
        start_hexlabels = [creature.hexlabel for creature in creatures]
        creature_names = [creature.name for creature in creatures]
        creature_moves = zip(creature_names, start_hexlabels, best_legion_move)
        log("creature_moves", creature_moves)
        now = time.time()
        ordered_creature_moves = self._find_move_order(game, creature_moves)
        log("found ordered_creature_moves %s in %fs" % (ordered_creature_moves,
          time.time() - now))
        return ordered_creature_moves

    def move_creatures(self, game):
        """Move all creatures in the legion.

        Idea: Find all possible moves for each creature in the legion,
        ignoring mobile allies, and score them in isolation without knowing
        where its allies will end up.  Find the best 7 moves for each creature
        (because with up to 7 creatures in a legion, a creature may have to
        take its 7th-favorite move, and because 7! = 5040, not too big).
        Combine these into legion moves, and score those again, then take
        the best legion move.  Finally, find the order of creature moves
        that lets all the creatures reach their assigned hexes without
        blocking their allies' moves.
        """
        try:
            log("move creatures")
            if self.best_creature_moves is None:
                self.best_creature_moves = self._find_best_creature_moves(game)
            # Loop in case a non-move is best.
            while self.best_creature_moves:
                (creature_name, start, finish) = \
                  self.best_creature_moves.pop(0)
                log("checking move", creature_name, start, finish)
                creature = game.creatures_in_battle_hex(start,
                  creature_name).pop()
                if finish != start and finish in game.find_battle_moves(
                  creature):
                    log("calling move_creature", creature.name, start, finish)
                    def1 = self.user.callRemote("move_creature", game.name,
                      creature.name, start, finish)
                    def1.addErrback(self.failure)
                    return
        except Exception:
            log(traceback.format_exc())
            raise

        # No moves, so end the maneuver phase.
        log("calling done_with_maneuvers")
        self.best_creature_moves = None
        def1 = self.user.callRemote("done_with_maneuvers", game.name)
        def1.addErrback(self.failure)

    def _score_legion_move(self, game, creatures):
        """Return a score for creatures in their current hexlabels."""
        ATTACKER_AGGRESSION_BONUS = 1.0
        ATTACKER_DISTANCE_PENALTY = -1.0
        HIT_BONUS = 1.0
        KILL_MULTIPLIER = 1.0
        DAMAGE_PENALTY = -1.0
        DEATH_MULTIPLIER = -1.0
        ELEVATION_BONUS = 0.5
        NATIVE_BRAMBLE_BONUS = 0.3
        NON_NATIVE_BRAMBLE_PENALTY = -0.7
        TOWER_BONUS = 1.0
        FRONT_OF_TOWER_BONUS = 0.5
        CENTER_OF_TOWER_BONUS = 1.0
        TITAN_IN_CENTER_OF_TOWER_BONUS = 2.0
        NON_NATIVE_DRIFT_PENALTY = -2.0
        NATIVE_VOLCANO_BONUS = 1.0
        ADJACENT_ALLY_BONUS = 0.5
        RANGESTRIKE_BONUS = 2.0
        TITAN_FORWARD_PENALTY = -1.0
        DEFENDER_FORWARD_PENALTY = -0.5

        score = 0
        battlemap = game.battlemap
        for creature in creatures:
            kill_bonus = 0
            legion = creature.legion
            legion2 = game.other_battle_legion(legion)
            can_rangestrike = False
            engaged = creature.engaged_enemies
            max_mean_hits = 0.0
            total_mean_damage_taken = 0.0
            # melee
            for enemy in engaged:
                # Damage we can do.
                dice = creature.number_of_dice(enemy)
                strike_number = creature.strike_number(enemy)
                mean_hits = dice * (7. - strike_number) / 6
                if mean_hits >= enemy.hits_left:
                    kill_bonus = max(kill_bonus, enemy.sort_value)
                max_mean_hits = max(mean_hits, max_mean_hits)
                # Damage we can take.
                dice = enemy.number_of_dice(creature)
                strike_number = enemy.strike_number(creature)
                mean_hits = dice * (7. - strike_number) / 6
                total_mean_damage_taken += mean_hits
            probable_death = total_mean_damage_taken >= creature.hits_left

            # rangestriking
            if not engaged:
                targets = creature.rangestrike_targets
                for enemy in targets:
                    # Damage we can do
                    dice = creature.number_of_dice(enemy)
                    strike_number = creature.strike_number(enemy)
                    mean_hits = dice * (7. - strike_number) / 6
                    if mean_hits >= enemy.hits_left:
                        kill_bonus = max(kill_bonus, enemy.sort_value)
                    max_mean_hits = max(mean_hits, max_mean_hits)
                    can_rangestrike = True
            if can_rangestrike:
                score += RANGESTRIKE_BONUS
                log(creature, "RANGESTRIKE_BONUS", RANGESTRIKE_BONUS)

            # Don't encourage titans to charge early.
            if (creature.name != "Titan" or game.battle_turn >= 4 or
              len(legion) == 1):
                if max_mean_hits:
                    bonus = HIT_BONUS * max_mean_hits
                    score += bonus
                    log(creature, "HIT_BONUS", bonus)
                if kill_bonus:
                    bonus = KILL_MULTIPLIER * kill_bonus
                    score += bonus
                    log(creature, "KILL_BONUS", bonus)
            if total_mean_damage_taken:
                penalty = DAMAGE_PENALTY * total_mean_damage_taken
                score += penalty
                log(creature, "DAMAGE_PENALTY", penalty)
            if probable_death:
                penalty = (DEATH_MULTIPLIER * probable_death *
                  creature.sort_value)
                score += penalty
                log(creature, "DEATH_PENALTY", penalty)

            # attacker must attack to avoid time loss
            # Don't encourage titans to charge early.
            if legion == game.attacker_legion and (creature.name != "Titan"
              or game.battle_turn >= 4 or len(legion) == 1):
                if engaged or targets:
                    score += ATTACKER_AGGRESSION_BONUS
                    log(creature, "ATTACKER_AGGRESSION_BONUS",
                        ATTACKER_AGGRESSION_BONUS)
                else:
                    enemy_hexlabels = [enemy.hexlabel for enemy in
                      legion2.living_creatures]
                    min_range = min((battlemap.range(creature.hexlabel,
                      enemy_hexlabel) for enemy_hexlabel in enemy_hexlabels))
                    penalty = min_range * ATTACKER_DISTANCE_PENALTY
                    score += penalty
                    log(creature, "ATTACKER_DISTANCE_PENALTY", penalty)

            battlehex = battlemap.hexes[creature.hexlabel]
            terrain = battlehex.terrain

            # Make titans hang back early.
            if (creature.name == "Titan" and game.battle_turn < 4 and
              terrain != "Tower"):
                if legion == game.attacker_legion:
                    entrance = "ATTACKER"
                else:
                    entrance = "DEFENDER"
                distance = battlemap.range(creature.hexlabel, entrance,
                  allow_entrance=True) - 2
                penalty = distance * TITAN_FORWARD_PENALTY
                score += penalty
                log(creature, "TITAN_FORWARD_PENALTY", penalty)

            # Make defenders hang back early.
            if (legion == game.defender_legion and game.battle_turn < 4 and
              terrain != "Tower"):
                entrance = "DEFENDER"
                distance = battlemap.range(creature.hexlabel, entrance,
                  allow_entrance=True) - 2
                penalty = distance * DEFENDER_FORWARD_PENALTY
                score += penalty
                log(creature, "DEFENDER_FORWARD_PENALTY", penalty)

            # terrain
            if battlehex.elevation:
                bonus = battlehex.elevation * ELEVATION_BONUS
                score += bonus
                log(creature, "ELEVATION_BONUS", bonus)
            if terrain == "Bramble":
                if creature.is_native(terrain):
                    score += NATIVE_BRAMBLE_BONUS
                    log(creature, "NATIVE_BRAMBLE_BONUS", NATIVE_BRAMBLE_BONUS)
                else:
                    score += NON_NATIVE_BRAMBLE_PENALTY
                    log(creature, "NON_NATIVE_BRAMBLE_PENALTY",
                      NON_NATIVE_BRAMBLE_PENALTY)
            elif terrain == "Tower":
                log(creature, "TOWER_BONUS")
                score += TOWER_BONUS
                if battlehex.elevation == 2:
                    if creature.name == "Titan":
                        score += TITAN_IN_CENTER_OF_TOWER_BONUS
                        log(creature, "TITAN_IN_CENTER_OF_TOWER_BONUS",
                          TITAN_IN_CENTER_OF_TOWER_BONUS)
                    else:
                        score += CENTER_OF_TOWER_BONUS
                        log(creature, "CENTER_OF_TOWER_BONUS",
                          CENTER_OF_TOWER_BONUS)
                elif (creature.name != "Titan" and battlehex.label in
                  ["C3", "D3"]):
                    score += FRONT_OF_TOWER_BONUS
                    log(creature, "FRONT_OF_TOWER_BONUS",
                      FRONT_OF_TOWER_BONUS)
            elif terrain == "Drift":
                if not creature.is_native(terrain):
                    score += NON_NATIVE_DRIFT_PENALTY
                    log(creature, "NON_NATIVE_DRIFT_PENALTY",
                      NON_NATIVE_DRIFT_PENALTY)
            elif terrain == "Volcano":
                score += NATIVE_VOLCANO_BONUS
                log(creature, "NATIVE_VOLCANO_BONUS", NATIVE_VOLCANO_BONUS)

            # allies
            for neighbor in battlehex.neighbors.itervalues():
                for ally in legion.living_creatures:
                    if ally.hexlabel == neighbor.label:
                        score += ADJACENT_ALLY_BONUS
                        log(creature, "ADJACENT_ALLY_BONUS",
                          ADJACENT_ALLY_BONUS)

        return score
