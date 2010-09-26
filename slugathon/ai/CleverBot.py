__copyright__ = "Copyright (c) 2010 David Ripton"
__license__ = "GNU GPL v2"


"""An attempt at a smarter AI."""


import random

from slugathon.ai import DimBot
from slugathon.game import Game, Creature
from slugathon.util.log import log


SQUASH = 0.6
BE_SQUASHED = 1.0


class CleverBot(DimBot.DimBot):

    def split(self, game):
        """Split if it's my turn."""
        assert game.active_player.name == self.playername
        player = game.active_player
        legions = player.legions.values()
        caretaker = game.caretaker
        for legion in legions:
            if len(legion) == 8:
                # initial split 4-4, one lord per legion
                new_markername = self._choose_marker(player)
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
                  legion.markername, new_markername,
                  old_creatures, new_creatures)
                def1.addErrback(self.failure)
                return
            elif len(legion) == 7 and player.markernames:
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
                            if enemy.sort_value < SQUASH * legion.sort_value:
                                safe_split_rolls.add(roll)
                        else:
                            safe_split_rolls.add(roll)
                if good_recruit_rolls and len(safe_split_rolls) == 6:
                    split = lst[-2:]
                    split_names = [creature.name for creature in split]
                    keep = lst[:-2]
                    keep_names = [creature.name for creature in keep]
                    new_markername = self._choose_marker(player)
                    def1 = self.user.callRemote("split_legion", game.name,
                      legion.markername, new_markername, keep_names,
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
                    score = self._score_move(legion, hexlabel, True)
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
                  legion.markername, hexlabel, entry_side, teleport,
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
        if enemies:
            assert len(enemies) == 1
            enemy = enemies.pop()
            enemy_sort_value = enemy.sort_value
            legion_sort_value = legion.sort_value
            if enemy_sort_value < SQUASH * legion_sort_value:
                score += enemy.score
            elif enemy_sort_value >= BE_SQUASHED * legion_sort_value:
                score -= legion_sort_value
        if move and (len(legion) < 7 or enemies):
            masterhex = board.hexes[hexlabel]
            terrain = masterhex.terrain
            recruits = legion.available_recruits(terrain, caretaker)
            if recruits:
                recruit_name = recruits[-1]
                recruit = Creature.Creature(recruit_name)
                score += recruit.sort_value
        return score



    def move_creatures(self, game):
        log("move creatures")
        assert game.battle_active_player.name == self.playername
        legion = game.battle_active_legion
        for creature in legion.sorted_creatures:
            if not creature.dead:
                moves = game.find_battle_moves(creature)
                if moves:
                    score_moves = []
                    # Not moving is also an option.
                    if creature.hexlabel not in ["ATTACKER", "DEFENDER"]:
                        moves.add(creature.hexlabel)
                    for move in moves:
                        score = self._score_battle_hex(game, creature, move)
                        score_moves.append((score, move))
                    score_moves.sort()
                    log("score_moves", score_moves)
                    best_score_move = score_moves.pop()
                    best_move = best_score_move[1]
                    if best_move is not creature.hexlabel:
                        log("calling move_creature", creature.name,
                          creature.hexlabel, best_move)
                        def1 = self.user.callRemote("move_creature", game.name,
                          creature.name, creature.hexlabel, best_move)
                        def1.addErrback(self.failure)
                        return
        # No moves, so end the maneuver phase.
        log("calling done_with_maneuvers")
        def1 = self.user.callRemote("done_with_maneuvers", game.name)
        def1.addErrback(self.failure)

    def _score_battle_hex(self, game, creature, hexlabel):
        """Return a score for creature moving to or staying in hexlabel."""
        ATTACKER_AGGRESSION_BONUS = 1.0
        ATTACKER_DISTANCE_PENALTY = 1.0
        HIT_BONUS = 1.0
        KILL_BONUS = 3.0
        DAMAGE_PENALTY = 1.0
        DEATH_PENALTY = 3.0
        ELEVATION_BONUS = 0.5
        NATIVE_BRAMBLE_BONUS = 0.3
        NON_NATIVE_BRAMBLE_PENALTY = 0.5
        TOWER_BONUS = 0.5
        NON_NATIVE_DRIFT_PENALTY = 2.0
        NATIVE_VOLCANO_BONUS = 1.0
        ADJACENT_ALLY_BONUS = 0.5

        legion = creature.legion
        legion2 = game.other_battle_legion(legion)
        battlemap = game.battlemap
        score = 0
        prev_hexlabel = creature.hexlabel
        try:
            # XXX Modifying game state is probably a bad idea.
            creature.hexlabel = hexlabel
            engaged = creature.engaged_enemies
            probable_kill = False
            max_mean_hits = 0.0
            total_mean_damage_taken = 0.0
            # melee
            for enemy in engaged:
                # Damage we can do.
                dice = creature.number_of_dice(enemy)
                strike_number = creature.strike_number(enemy)
                mean_hits = dice * (7. - strike_number) / 6
                if mean_hits >= enemy.hits_left:
                    probable_kill = True
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
                        probable_kill = True
                    max_mean_hits = max(mean_hits, max_mean_hits)

            # Don't encourage titans to charge early.
            if (creature.name != "Titan" or game.battle_turn >= 4 or
              len(legion) == 1):
                score += HIT_BONUS * max_mean_hits
                score += KILL_BONUS * probable_kill
            score -= DAMAGE_PENALTY * total_mean_damage_taken
            score -= DEATH_PENALTY * probable_death

            # attacker must attack to avoid time loss
            # Don't encourage titans to charge early.
            if legion == game.attacker_legion and (creature.name != "Titan"
              or game.battle_turn >= 4 or len(legion) == 1):
                if engaged or targets:
                    score += ATTACKER_AGGRESSION_BONUS
                else:
                    enemy_hexlabels = [enemy.hexlabel for enemy in
                      legion2.living_creatures]
                    min_range = min((battlemap.range(creature.hexlabel,
                      hexlabel) for hexlabel in enemy_hexlabels))
                    score -= min_range * ATTACKER_DISTANCE_PENALTY

            # terrain
            battlehex = battlemap.hexes[creature.hexlabel]
            terrain = battlehex.terrain
            score += battlehex.elevation * ELEVATION_BONUS
            if terrain == "Bramble":
                if creature.is_native(terrain):
                    score += NATIVE_BRAMBLE_BONUS
                else:
                    score -= NON_NATIVE_BRAMBLE_PENALTY
            elif terrain == "Tower":
                score += TOWER_BONUS
            elif terrain == "Drift":
                if not creature.is_native(terrain):
                    score -= NON_NATIVE_DRIFT_PENALTY
            elif terrain == "Volcano":
                score += NATIVE_VOLCANO_BONUS

            # allies
            for neighbor in battlehex.neighbors:
                for ally in legion.living_creatures:
                    if ally.hexlabel == neighbor:
                        score += ADJACENT_ALLY_BONUS

        finally:
            creature.hexlabel = prev_hexlabel

        return score
