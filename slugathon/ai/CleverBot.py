__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"


"""An attempt at a smarter AI."""


import random
import copy
import time
from sys import maxint
import itertools
import collections
import logging

from twisted.python import log
from zope.interface import implementer

from slugathon.ai.Bot import Bot
from slugathon.ai import BotParams
from slugathon.game import Game, Creature, Phase


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


@implementer(Bot)
class CleverBot(object):
    def __init__(self, playername, ai_time_limit, bot_params=None):
        logging.info("CleverBot %s %s", playername, ai_time_limit)
        self.playername = playername
        self.user = None
        self.ai_time_limit = ai_time_limit
        self.best_creature_moves = None
        if bot_params is None:
            self.bp = BotParams.default_bot_params
        else:
            self.bp = bot_params

    @property
    def player_info(self):
        """Return a string with information for result-tracking purposes."""
        return str(self.bp)

    def maybe_pick_color(self, game):
        logging.info("maybe_pick_color")
        if game.next_playername_to_pick_color == self.playername:
            color = random.choice(game.colors_left)
            def1 = self.user.callRemote("pick_color", game.name, color)
            def1.addErrback(self.failure)

    def maybe_pick_first_marker(self, game, playername):
        logging.info("maybe_pick_first_marker")
        if playername == self.playername:
            player = game.get_player_by_name(playername)
            markerid = self._choose_marker(player)
            self._pick_marker(game, self.playername, markerid)

    def _pick_marker(self, game, playername, markerid):
        logging.info("pick_marker")
        player = game.get_player_by_name(playername)
        if markerid is None:
            if not player.markerid_to_legion:
                self.maybe_pick_first_marker(game, playername)
        else:
            player.pick_marker(markerid)
            if not player.markerid_to_legion:
                def1 = self.user.callRemote("pick_first_marker", game.name,
                  markerid)
                def1.addErrback(self.failure)

    def _choose_marker(self, player):
        """Pick a legion marker randomly, except prefer my own markers
        to captured ones to be less annoying."""
        own_markerids_left = [name for name in player.markerids_left if
          name[:2] == player.color_abbrev]
        if own_markerids_left:
            return random.choice(own_markerids_left)
        else:
            return random.choice(list(player.markerids_left))

    # TODO Avoid hitting 100-point multiples with 7-high legions.
    def choose_engagement(self, game):
        """Resolve engagements.

        Fight with legions that have angels first (so we can summon them),
        then with the most important legion.
        """
        logging.info("choose_engagement")
        if (game.pending_summon or game.pending_reinforcement or
          game.pending_acquire):
            logging.info("choose_engagement bailing early %s %s %s",
              game.pending_summon, game.pending_reinforcement,
              game.pending_acquire)
            return
        hexlabels = list(game.engagement_hexlabels)
        if hexlabels:
            if len(hexlabels) >= 2:
                player = game.get_player_by_name(self.playername)
                value_to_hexlabel = []
                for hexlabel in hexlabels:
                    legion = player.friendly_legions(hexlabel=hexlabel).pop()
                    value = legion.sort_value
                    if not player.summoned and legion.any_summonable:
                        value += 1000
                    value_to_hexlabel.append((value, hexlabel))
                value_to_hexlabel.sort()
                (value, hexlabel) = value_to_hexlabel[-1]
            else:
                hexlabel = hexlabels[0]
            logging.info("calling resolve_engagement")
            def1 = self.user.callRemote("resolve_engagement", game.name,
              hexlabel)
            def1.addErrback(self.failure)
        else:
            logging.info("CleverBot calling done_with_engagements")
            def1 = self.user.callRemote("done_with_engagements", game.name)
            def1.addErrback(self.failure)

    # TODO concede, negotiate
    def resolve_engagement(self, game, hexlabel):
        """Resolve the engagement in hexlabel."""
        logging.info("resolve_engagement %s %s", game, hexlabel)
        attacker = None
        defender = None
        for legion in game.all_legions(hexlabel):
            if legion.player == game.active_player:
                attacker = legion
            else:
                defender = legion
        if attacker:
            logging.info("attacker %s %s", attacker, attacker.player.name)
        if defender:
            logging.info("defender %s %s", defender, defender.player.name)
        if not attacker or not defender:
            logging.info("no attacker or defender; bailing")
            return
        if defender.player.name == self.playername:
            if game.defender_chose_not_to_flee:
                logging.info("defender already chose not to flee")
            else:
                logging.info("defender hasn't chosen whether to flee yet")
                if defender.can_flee:
                    logging.info("can flee")
                    if (defender.terrain_combat_value * self.bp.FLEE_RATIO <
                      attacker.terrain_combat_value):
                        logging.info("fleeing")
                        def1 = self.user.callRemote("flee", game.name,
                          defender.markerid)
                        def1.addErrback(self.failure)
                    else:
                        logging.info("not fleeing")
                        def1 = self.user.callRemote("do_not_flee", game.name,
                          defender.markerid)
                        def1.addErrback(self.failure)
                else:
                    logging.info("can't flee")
                    def1 = self.user.callRemote("do_not_flee", game.name,
                      defender.markerid)
                    def1.addErrback(self.failure)
        elif attacker.player.name == self.playername:
            if not game.defender_chose_not_to_flee:
                # Wait for the defender to choose whether to flee.
                logging.info("waiting for defender")
            else:
                logging.info("attacker fighting")
                def1 = self.user.callRemote("fight", game.name,
                  attacker.markerid, defender.markerid)
                def1.addErrback(self.failure)
        else:
            logging.info("not my engagement")

    # TODO Look at what we can recruit on each movement roll, to see if we
    # should take a third creature of a kind.  We also need to be able to
    # split off better creatures to enable recruiting for this to be
    # useful for 6-high legions.
    def _pick_recruit_and_recruiters(self, legion):
        """Return a tuple of (recruit, recruiters), or (None, None)."""
        player = legion.player
        game = player.game
        caretaker = game.caretaker
        masterhex = game.board.hexes[legion.hexlabel]
        mterrain = masterhex.terrain
        lst = legion.available_recruits_and_recruiters(mterrain,
          caretaker)
        if lst:
            # For now, just take the last recruit.
            tup = lst[-1]
            recruit = tup[0]
            # And pick randomly among its recruiters.
            possible_recruiters = set()
            for tup in lst:
                if tup[0] == recruit:
                    recruiters = tup[1:]
                    possible_recruiters.add(recruiters)
            recruiters = random.choice(list(possible_recruiters))
            return (recruit, recruiters)
        return (None, None)

    def recruit(self, game):
        logging.info("CleverBot.recruit")
        if game.active_player.name != self.playername:
            logging.info("not my turn")
            return
        player = game.active_player
        for legion in player.legions:
            if legion.moved and legion.can_recruit:
                recruit, recruiters = self._pick_recruit_and_recruiters(legion)
                if recruit is not None:
                    logging.info("CleverBot calling recruit_creature %s %s %s",
                      legion.markerid, recruit, recruiters)
                    def1 = self.user.callRemote("recruit_creature", game.name,
                      legion.markerid, recruit, recruiters)
                    def1.addErrback(self.failure)
                    return
        logging.info("CleverBot calling done_with_recruits")
        def1 = self.user.callRemote("done_with_recruits", game.name)
        def1.addErrback(self.failure)

    def reinforce_during(self, game):
        """Reinforce, during the REINFORCE battle phase"""
        logging.info("")
        assert game.battle_active_player.name == self.playername
        assert game.battle_phase == Phase.REINFORCE
        legion = game.defender_legion
        assert legion.player.name == self.playername
        if game.battle_turn == 4 and legion.can_recruit:
            recruit, recruiters = self._pick_recruit_and_recruiters(legion)
            if recruit is not None:
                logging.info("CleverBot calling recruit_creature %s", recruit)
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markerid, recruit, recruiters)
                def1.addErrback(self.failure)
                return
        logging.info("CleverBot calling done_with_reinforcements")
        def1 = self.user.callRemote("done_with_reinforcements", game.name)
        def1.addErrback(self.failure)

    def reinforce_after(self, game):
        """Reinforce, after the battle"""
        logging.info("")
        legion = game.defender_legion
        assert legion.player.name == self.playername
        if legion.can_recruit:
            recruit, recruiters = self._pick_recruit_and_recruiters(legion)
            if recruit is not None:
                logging.info("CleverBot calling recruit_creature %s", recruit)
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markerid, recruit, recruiters)
                def1.addErrback(self.failure)
                return
        logging.info("CleverBot calling do_not_reinforce %s", recruit)
        def1 = self.user.callRemote("do_not_reinforce", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

    def summon_angel_during(self, game):
        """Summon, during the REINFORCE battle phase"""
        logging.info("CleverBot.summon_angel_during")
        assert game.active_player.name == self.playername
        if game.battle_phase != Phase.REINFORCE:
            return
        legion = game.attacker_legion
        assert legion.player.name == self.playername
        summonables = []
        if (legion.can_summon and game.first_attacker_kill in
          [game.battle_turn - 1, game.battle_turn]):
            for legion2 in legion.player.legions:
                if not legion2.engaged:
                    for creature in legion2.creatures:
                        if creature.summonable:
                            summonables.append(creature)
            if summonables:
                tuples = sorted(((creature.sort_value, creature)
                  for creature in summonables), reverse=True)
                summonable = tuples[0][1]
                donor = summonable.legion
                logging.info("CleverBot calling _summon_angel %s %s %s",
                  legion.markerid, donor.markerid, summonable.name)
                def1 = self.user.callRemote("summon_angel", game.name,
                  legion.markerid, donor.markerid, summonable.name)
                def1.addErrback(self.failure)
                return

        logging.info("CleverBot calling do_not_summon_angel %s",
          legion.markerid)
        def1 = self.user.callRemote("do_not_summon_angel", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

        logging.info("CleverBot calling done_with_reinforcements")
        def1 = self.user.callRemote("done_with_reinforcements", game.name)
        def1.addErrback(self.failure)

    # TODO Do not summon if 6 high and we could recruit better.
    def summon_angel_after(self, game):
        """Summon, after the battle is over."""
        logging.info("CleverBot.summon_angel_after")
        assert game.active_player.name == self.playername
        legion = game.attacker_legion
        assert legion.player.name == self.playername
        summonables = []
        if (legion.can_summon and game.first_attacker_kill in
          [game.battle_turn - 1, game.battle_turn]):
            for legion2 in legion.player.legions:
                if not legion2.engaged:
                    for creature in legion2.creatures:
                        if creature.summonable:
                            summonables.append(creature)
            if summonables:
                tuples = sorted(((creature.sort_value, creature)
                  for creature in summonables), reverse=True)
                summonable = tuples[0][1]
                donor = summonable.legion
                logging.info("CleverBot calling _summon_angel %s %s %s",
                  legion.markerid, donor.markerid, summonable.name)
                def1 = self.user.callRemote("summon_angel", game.name,
                  legion.markerid, donor.markerid, summonable.name)
                def1.addErrback(self.failure)
                return

        logging.info("CleverBot calling do_not_summon_angel %s",
          legion.markerid)
        def1 = self.user.callRemote("do_not_summon_angel", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

    # TODO Do not take an angel if we are 6 high and can recruit better.
    def acquire_angels(self, game, markerid, num_angels, num_archangels):
        logging.info("CleverBot.acquire_angels %s %s %s", markerid, num_angels,
          num_archangels)
        player = game.get_player_by_name(self.playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        starting_height = len(legion)
        acquires = 0
        angel_names = []
        while starting_height + acquires < 7 and num_archangels:
            angel_names.append("Archangel")
            num_archangels -= 1
            acquires += 1
        while starting_height + acquires < 7 and num_angels:
            angel_names.append("Angel")
            num_angels -= 1
            acquires += 1
        if angel_names:
            logging.info("CleverBot calling acquire_angels %s %s", markerid,
              angel_names)
            def1 = self.user.callRemote("acquire_angels", game.name,
              markerid, angel_names)
            def1.addErrback(self.failure)
        else:
            logging.info("CleverBot calling do_not_acquire_angels %s",
              markerid)
            def1 = self.user.callRemote("do_not_acquire_angels", game.name,
              markerid)
            def1.addErrback(self.failure)

    # TODO Sometimes split off a better creature to enable better recruiting.
    def split(self, game):
        """Split a legion, or end split phase."""
        logging.info("split")
        if game.active_player.name != self.playername:
            logging.info("called split out of turn; exiting")
            return
        player = game.active_player
        caretaker = game.caretaker
        for legion in player.legions:
            if len(legion) == 8:
                if game.turn != 1:
                    raise AssertionError("8-high legion", legion)
                # initial split 4-4, one lord per legion
                logging.info("initial split")
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
                logging.info("new_creatures %s old_creatures %s",
                  new_creatures, old_creatures)
                def1 = self.user.callRemote("split_legion", game.name,
                  legion.markerid, new_markerid, old_creatures, new_creatures)
                def1.addErrback(self.failure)
                return
            elif len(legion) == 7 and player.markerids_left:
                logging.info("7-high")
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
                            if (enemy.terrain_combat_value < self.bp.SQUASH *
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
                      legion.markerid, new_markerid, keep_names, split_names)
                    def1.addErrback(self.failure)
                    return

        # No splits, so move on to the next phase.
        def1 = self.user.callRemote("done_with_splits", game.name)
        def1.addErrback(self.failure)

    def move_legions(self, game):
        """Move one or more legions, and then end the Move phase."""
        logging.info("move_legions")
        if game.active_player.name != self.playername:
            logging.info("not active player; aborting")
            return
        player = game.active_player
        non_moves = {}  # markerid: score
        while True:
            # Score moves
            # (score, legion, hexlabel, entry_side)
            best_moves = []
            for legion in player.unmoved_legions:
                moves = game.find_all_moves(legion, game.board.hexes[
                  legion.hexlabel], player.movement_roll)
                for hexlabel, entry_side in moves:
                    score = self._score_move(legion, hexlabel, True)
                    best_moves.append(
                      (score, legion, hexlabel, entry_side))
            best_moves.sort()
            logging.info("best moves %s", best_moves)

            if player.can_take_mulligan:
                legions_with_good_moves = set()
                for (score, legion, _, _) in best_moves:
                    if score > 0:
                        legions_with_good_moves.add(legion)
                if len(legions_with_good_moves) < 2:
                    logging.info("taking a mulligan")
                    def1 = self.user.callRemote("take_mulligan", game.name)
                    def1.addErrback(self.failure)
                    return

            # Score non-moves
            # (score, legion, hexlabel, None)
            # Entry side None means not a move.
            for legion in player.unmoved_legions:
                score = self._score_move(legion, legion.hexlabel, False)
                non_moves[legion.markerid] = score
            logging.info("non_moves %s", non_moves)

            while best_moves:
                score, legion, hexlabel, entry_side = best_moves.pop()
                non_move_score = non_moves[legion.markerid]
                if (score > non_move_score or not player.moved_legions or
                  len(player.friendly_legions(legion.hexlabel)) >= 2):
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
            return

    def _score_move(self, legion, hexlabel, moved):
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
            enemy_combat_value = enemy.terrain_combat_value
            logging.info("legion %s hexlabel %s", legion, hexlabel)
            logging.info("legion_combat_value %s", legion_combat_value)
            logging.info("enemy_combat_value %s", enemy_combat_value)
            if enemy_combat_value < self.bp.SQUASH * legion_combat_value:
                score += enemy.score
            elif (enemy_combat_value >= self.bp.BE_SQUASHED *
              legion_combat_value):
                score -= legion_sort_value
        if moved and (len(legion) < 7 or enemies):
            masterhex = board.hexes[hexlabel]
            terrain = masterhex.terrain
            recruits = legion.available_recruits(terrain, caretaker)
            if recruits:
                recruit_name = recruits[-1]
                recruit = Creature.Creature(recruit_name)
                # Only give credit for recruiting if we're likely to live.
                if not enemies or enemy_combat_value < legion_combat_value:
                    recruit_value = recruit.sort_value
                elif (enemy_combat_value < self.bp.BE_SQUASHED *
                  legion_combat_value):
                    recruit_value = 0.5 * recruit.sort_value
                logging.info("recruit value %s %s %s", legion.markerid,
                  hexlabel, recruit_value)
                score += recruit_value
        if game.turn > 1:
            # Do not fear enemy legions on turn 1.  8-high legions will be
            # forced to split, and hanging around in the tower to avoid getting
            # attacked 5-on-4 is too passive.
            try:
                previous_hexlabel = legion.hexlabel
                legion.hexlabel = hexlabel
                for enemy in player.enemy_legions():
                    if (enemy.terrain_combat_value >= self.bp.BE_SQUASHED *
                      legion_combat_value):
                        for roll in xrange(1, 6 + 1):
                            moves = game.find_normal_moves(enemy,
                              game.board.hexes[enemy.hexlabel], roll).union(
                              game.find_titan_teleport_moves(enemy))
                            hexlabels = set((move[0] for move in moves))
                            if hexlabel in hexlabels:
                                score -= legion_sort_value / 6.0
            finally:
                legion.hexlabel = previous_hexlabel
        return score

    def _gen_legion_moves_inner(self, movesets):
        """Yield tuples of distinct hexlabels, one from each moveset, in order,
        with no duplicates.

        movesets is a list of sets of hexlabels, corresponding to the order of
        remaining creatures in the legion.
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

        movesets is a list of sets of hexlabels to which each Creature can move
        (or stay), in the same order as Legion.sorted_creatures.  Like:
        creatures [titan1, ogre1, troll1]
        movesets [{"A1", "A2", "B1"}, {"B1", "B2"}, {"B1", "B3"}]

        A legion_move is a list of hexlabels, in the same order as creatures,
        where each Creature's hexlabel is one from its original list, and no
        two Creatures have the same hexlabel.  Like:
        ["A1", "B1", "B3"]
        """
        logging.info("_gen_legion_moves %s", movesets)
        for moves in self._gen_legion_moves_inner(movesets):
            if len(moves) == len(movesets):
                yield list(moves)

    def _gen_fallback_legion_moves(self, movesets):
        """Yield all possible legion_moves for movesets, possibly including
        some missing moves in the case where not all creatures can get onboard.

        movesets is a list of sets of hexlabels to which each Creature can move
        (or stay), in the same order as Legion.sorted_creatures.  Like:
        creatures [titan1, ogre1, troll1]
        movesets [{"A1", "A2", "B1"}, {"B1", "B2"}, {"B1", "B3"}]

        A legion_move is a list of hexlabels, in the same order as creatures,
        where each Creature's hexlabel is one from its original list, and no
        two Creatures have the same hexlabel.  Like:
        ["A1", "B1", "B3"]
        """
        logging.info("_gen_legion_moves %s", movesets)
        for moves in self._gen_legion_moves_inner(movesets):
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
        max_score = 0
        sort_values = {}
        for creature_name, start, move in creature_moves:
            creature = game.creatures_in_battle_hex(start, creature_name).pop()
            sort_values[creature_name] = creature.sort_value
            max_score += creature.sort_value
        perms = list(itertools.permutations(creature_moves))
        logging.info("_find_move_order %d perms" % len(perms))
        # Scramble the list so we don't get a bunch of similar bad
        # orders jumbled together at the beginning.
        random.shuffle(perms)
        best_score = -maxint
        best_perm = None
        start_time = time.time()
        for perm in perms:
            score = self._score_perm(game, sort_values, perm)
            if score == max_score:
                best_perm = perm
                logging.info("_find_move_order found perfect order")
                break
            elif score > best_score:
                best_perm = perm
                best_score = score
            if time.time() - start_time > self.ai_time_limit:
                logging.info("_find_move_order time limit")
                break
        logging.info("_find_move_order returning %s" % list(best_perm))
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
        if (game.battle_active_player is None or game.battle_active_player.name
          != self.playername):
            return None
        legion = game.battle_active_legion
        creatures = legion.sorted_living_creatures
        logging.info("_find_best_creature_moves %s %s", legion, creatures)
        if not creatures:
            return None
        movesets = []  # list of a set of hexlabels for each creature
        previous_creature = None
        moveset = None
        for creature in creatures:
            if (previous_creature and creature.name == previous_creature.name
              and creature.hexlabel == previous_creature.hexlabel):
                # Reuse previous moveset
                moveset = copy.deepcopy(moveset)
            else:
                moves = game.find_battle_moves(creature,
                  ignore_mobile_allies=True)
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
                    logging.info("score_moves %s %s", creature, score_moves)
                    moveset = best7(score_moves)
                else:
                    moveset = set([creature.hexlabel])
            movesets.append(moveset)
            previous_creature = creature
        best_legion_move = None
        now = time.time()
        legion_moves = list(self._gen_legion_moves(movesets))
        logging.info("found %d legion_moves in %fs" % (len(legion_moves),
          time.time() - now))
        if not legion_moves:
            legion_moves = list(self._gen_fallback_legion_moves(movesets))
            if not legion_moves:
                return None
        best_score = -maxint
        start = time.time()
        # Scramble the moves, in case we don't have time to look at them all.
        random.shuffle(legion_moves)
        logging.info("len(creatures) %d len(legion_moves[0]) %d" % (
          len(creatures), len(legion_moves[0])))
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
                if now - start > self.ai_time_limit:
                    logging.info("_find_best_creature_moves time limit")
                    break
            finally:
                for creature in creatures:
                    creature.hexlabel = creature.previous_hexlabel
        logging.info("found best_legion_move %s in %fs" % (best_legion_move,
          now - start))
        start_hexlabels = [creature.hexlabel for creature in creatures]
        creature_names = [creature.name for creature in creatures]
        creature_moves = zip(creature_names, start_hexlabels, best_legion_move)
        logging.info("creature_moves %s", creature_moves)
        now = time.time()
        ordered_creature_moves = self._find_move_order(game, creature_moves)
        logging.info("found ordered_creature_moves %s in %fs" % (
          ordered_creature_moves, time.time() - now))
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
        logging.info("CleverBot.move_creatures")
        if self.best_creature_moves is None:
            self.best_creature_moves = self._find_best_creature_moves(game)
        # Loop in case a non-move is best.
        while self.best_creature_moves:
            (creature_name, start, finish) = \
              self.best_creature_moves.pop(0)
            logging.info("checking move %s %s %s", creature_name, start,
              finish)
            creatures = game.creatures_in_battle_hex(start, creature_name)
            if creatures:
                creature = creatures.pop()
            else:
                logging.info("best_creature_moves was broken")
                self.best_creature_moves = self._find_best_creature_moves(game)
                continue
            if finish != start and finish in game.find_battle_moves(
              creature):
                logging.info("calling move_creature %s %s %s", creature.name,
                  start, finish)
                def1 = self.user.callRemote("move_creature", game.name,
                  creature.name, start, finish)
                def1.addErrback(self.failure)
                return

        # No moves, so end the maneuver phase.
        logging.info("calling done_with_maneuvers")
        self.best_creature_moves = None
        def1 = self.user.callRemote("done_with_maneuvers", game.name)
        def1.addErrback(self.failure)

    def _score_legion_move(self, game, creatures):
        """Return a score for creatures in their current hexlabels."""
        score = 0
        battlemap = game.battlemap
        legion = creatures[0].legion
        legion2 = game.other_battle_legion(legion)

        # For each enemy, figure out the average damage we could do to it if
        # everyone concentrated on hitting it, and if that's enough to kill it,
        # give every creature a kill bonus.
        # (This is not quite right because each creature can only hit one enemy
        # (modulo carries), but it's a start.)
        kill_bonus = 0
        for enemy in legion2.creatures:
            total_mean_hits = 0
            for creature in creatures:
                if (enemy in creature.engaged_enemies or
                  (not creature.engaged and enemy in
                  creature.rangestrike_targets)):
                    dice = creature.number_of_dice(enemy)
                    strike_number = creature.strike_number(enemy)
                    mean_hits = dice * (7. - strike_number) / 6
                    total_mean_hits += mean_hits
            if total_mean_hits >= enemy.hits_left:
                kill_bonus += enemy.sort_value

        for creature in creatures:
            can_rangestrike = False
            engaged = creature.engaged_enemies
            max_mean_hits = 0.0
            total_mean_damage_taken = 0.0
            engaged_with_rangestriker = False
            # melee
            for enemy in engaged:
                # Damage we can do.
                dice = creature.number_of_dice(enemy)
                strike_number = creature.strike_number(enemy)
                mean_hits = dice * (7. - strike_number) / 6
                max_mean_hits = max(mean_hits, max_mean_hits)
                # Damage we can take.
                dice = enemy.number_of_dice(creature)
                strike_number = enemy.strike_number(creature)
                mean_hits = dice * (7. - strike_number) / 6
                total_mean_damage_taken += mean_hits
                if enemy.rangestrikes:
                    engaged_with_rangestriker = True
            # inbound rangestriking
            for enemy in legion2.creatures:
                if enemy not in engaged:
                    if creature in enemy.potential_rangestrike_targets:
                        dice = enemy.number_of_dice(creature)
                        strike_number = enemy.strike_number(creature)
                        mean_hits = dice * (7. - strike_number) / 6
                        total_mean_damage_taken += mean_hits
            probable_death = total_mean_damage_taken >= creature.hits_left

            if engaged_with_rangestriker and not creature.rangestrikes:
                score += self.bp.ENGAGE_RANGESTRIKER_BONUS
                logging.info(creature, "ENGAGE_RANGESTRIKER_BONUS %s",
                  self.bp.ENGAGE_RANGESTRIKER_BONUS)

            # rangestriking
            if not engaged:
                targets = creature.rangestrike_targets
                for enemy in targets:
                    # Damage we can do
                    dice = creature.number_of_dice(enemy)
                    strike_number = creature.strike_number(enemy)
                    mean_hits = dice * (7. - strike_number) / 6
                    max_mean_hits = max(mean_hits, max_mean_hits)
                    can_rangestrike = True
            if can_rangestrike:
                score += self.bp.RANGESTRIKE_BONUS
                logging.info(creature, "RANGESTRIKE_BONUS %s",
                  self.bp.RANGESTRIKE_BONUS)

            # Don't encourage titans to charge early.
            if (creature.name != "Titan" or game.battle_turn >= 4 or
              len(legion) == 1):
                if max_mean_hits:
                    bonus = self.bp.HIT_BONUS * max_mean_hits
                    score += bonus
                    logging.info(creature, "HIT_BONUS %s", bonus)
                if kill_bonus:
                    bonus = self.bp.KILL_MULTIPLIER * kill_bonus
                    score += bonus
                    logging.info(creature, "KILL_BONUS %s", bonus)
            if total_mean_damage_taken:
                penalty = self.bp.DAMAGE_PENALTY * total_mean_damage_taken
                score += penalty
                logging.info(creature, "DAMAGE_PENALTY %s", penalty)
            if probable_death:
                penalty = (self.bp.DEATH_MULTIPLIER * probable_death *
                  creature.sort_value)
                score += penalty
                logging.info(creature, "DEATH_PENALTY %s", penalty)

            # attacker must attack to avoid time loss
            # Don't encourage titans to charge early.
            if legion == game.attacker_legion and (creature.name != "Titan"
              or game.battle_turn >= 4 or len(legion) == 1):
                if engaged or targets:
                    score += self.bp.ATTACKER_AGGRESSION_BONUS
                    logging.info(creature, "ATTACKER_AGGRESSION_BONUS %s",
                        self.bp.ATTACKER_AGGRESSION_BONUS)
                else:
                    enemy_hexlabels = [enemy.hexlabel for enemy in
                      legion2.living_creatures]
                    if enemy_hexlabels:
                        min_range = min((battlemap.range(creature.hexlabel,
                          enemy_hexlabel) for enemy_hexlabel in
                          enemy_hexlabels))
                        penalty = min_range * self.bp.ATTACKER_DISTANCE_PENALTY
                        score += penalty
                        logging.info(creature, "ATTACKER_DISTANCE_PENALTY %s",
                          penalty)

            battlehex = battlemap.hexes[creature.hexlabel]
            terrain = battlehex.terrain

            # Make titans hang back early.
            if (creature.is_titan and game.battle_turn < 4 and
              terrain != "Tower"):
                if legion == game.attacker_legion:
                    entrance = "ATTACKER"
                else:
                    entrance = "DEFENDER"
                distance = battlemap.range(creature.hexlabel, entrance,
                  allow_entrance=True) - 2
                penalty = distance * self.bp.TITAN_FORWARD_PENALTY
                if penalty:
                    score += penalty
                    logging.info(creature, "TITAN_FORWARD_PENALTY %s", penalty)

            # Make defenders hang back early.
            if (legion == game.defender_legion and game.battle_turn < 4 and
              terrain != "Tower"):
                entrance = "DEFENDER"
                distance = battlemap.range(creature.hexlabel, entrance,
                  allow_entrance=True) - 2
                penalty = distance * self.bp.DEFENDER_FORWARD_PENALTY
                if penalty:
                    score += penalty
                    logging.info(creature, "DEFENDER_FORWARD_PENALTY %s",
                      penalty)

            # terrain
            if battlehex.elevation:
                bonus = battlehex.elevation * self.bp.ELEVATION_BONUS
                score += bonus
                logging.info(creature, "ELEVATION_BONUS %s", bonus)
            if terrain == "Bramble":
                if creature.is_native(terrain):
                    score += self.bp.NATIVE_BRAMBLE_BONUS
                    logging.info(creature, "NATIVE_BRAMBLE_BONUS %s",
                      self.bp.NATIVE_BRAMBLE_BONUS)
                else:
                    score += self.bp.NON_NATIVE_BRAMBLE_PENALTY
                    logging.info(creature, "NON_NATIVE_BRAMBLE_PENALTY %s",
                      self.bp.NON_NATIVE_BRAMBLE_PENALTY)
            elif terrain == "Tower":
                # XXX Hardcoded to default Tower map
                logging.info("%s TOWER_BONUS", creature)
                score += self.bp.TOWER_BONUS
                if battlehex.elevation == 2:
                    if creature.is_titan:
                        score += self.bp.TITAN_IN_CENTER_OF_TOWER_BONUS
                        logging.info("%s TITAN_IN_CENTER_OF_TOWER_BONUS %s",
                          creature, self.bp.TITAN_IN_CENTER_OF_TOWER_BONUS)
                    else:
                        score += self.bp.CENTER_OF_TOWER_BONUS
                        logging.info("%s CENTER_OF_TOWER_BONUS %s",
                          creature, self.bp.CENTER_OF_TOWER_BONUS)
                elif (legion == game.defender_legion and
                  creature.name != "Titan" and battlehex.label in
                  ["C3", "D3"]):
                    score += self.bp.FRONT_OF_TOWER_BONUS
                    logging.info("%s FRONT_OF_TOWER_BONUS %s",
                      creature, self.bp.FRONT_OF_TOWER_BONUS)
                elif (legion == game.defender_legion and
                  creature.name != "Titan" and battlehex.label in
                  ["C4", "E3"]):
                    score += self.bp.MIDDLE_OF_TOWER_BONUS
                    logging.info("%s MIDDLE_OF_TOWER_BONUS %s",
                      creature, self.bp.MIDDLE_OF_TOWER_BONUS)
            elif terrain == "Drift":
                if not creature.is_native(terrain):
                    score += self.bp.NON_NATIVE_DRIFT_PENALTY
                    logging.info("%s NON_NATIVE_DRIFT_PENALTY %s",
                      creature, self.bp.NON_NATIVE_DRIFT_PENALTY)
            elif terrain == "Volcano":
                score += self.bp.NATIVE_VOLCANO_BONUS
                logging.info("%s NATIVE_VOLCANO_BONUS %s",
                  creature, self.bp.NATIVE_VOLCANO_BONUS)

            if "Slope" in battlehex.borders:
                if creature.is_native("Slope"):
                    score += self.bp.NATIVE_SLOPE_BONUS
                    logging.info("%s NATIVE_SLOPE_BONUS %s",
                      creature, self.bp.NATIVE_SLOPE_BONUS)
                else:
                    score += self.bp.NON_NATIVE_SLOPE_PENALTY
                    logging.info("%s NON_NATIVE_SLOPE_PENALTY %s",
                      creature, self.bp.NON_NATIVE_SLOPE_PENALTY)
            if "Dune" in battlehex.borders:
                if creature.is_native("Dune"):
                    score += self.bp.NATIVE_DUNE_BONUS
                    logging.info("%s NATIVE_DUNE_BONUS %s",
                      creature, self.bp.NATIVE_DUNE_BONUS)
                else:
                    score += self.bp.NON_NATIVE_DUNE_PENALTY
                    logging.info("%s NON_NATIVE_DUNE_PENALTY %s",
                      creature, self.bp.NON_NATIVE_DUNE_PENALTY)

            # allies
            num_adjacent_allies = 0
            for neighbor in battlehex.neighbors.itervalues():
                for ally in legion.living_creatures:
                    if ally.hexlabel == neighbor.label:
                        num_adjacent_allies += 1
            adjacent_allies_bonus = (num_adjacent_allies *
              self.bp.ADJACENT_ALLY_BONUS)
            if adjacent_allies_bonus:
                score += adjacent_allies_bonus
                logging.info("%s ADJACENT_ALLY_BONUS %s",
                  creature, adjacent_allies_bonus)

        return score

    def strike(self, game):
        logging.info("strike")
        if not game.battle_active_player:
            logging.info("called strike with no battle")
            return
        if game.battle_active_player.name != self.playername:
            logging.info("called strike for wrong player")
            return
        legion = game.battle_active_legion
        # First do the strikers with only one target.
        for striker in legion.sorted_creatures:
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                if len(hexlabels) == 1:
                    hexlabel = hexlabels.pop()
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    num_dice = striker.number_of_dice(target)
                    strike_number = striker.strike_number(target)
                    def1 = self.user.callRemote("strike", game.name,
                      striker.name, striker.hexlabel, target.name,
                      target.hexlabel, num_dice, strike_number)
                    def1.addErrback(self.failure)
                    return

        # Then do the ones that have to choose a target.
        target_to_total_mean_hits = collections.defaultdict(float)
        best_target = None
        for striker in legion.sorted_creatures:
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                for hexlabel in hexlabels:
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    num_dice = striker.number_of_dice(target)
                    strike_number = striker.strike_number(target)
                    mean_hits = num_dice * (7. - strike_number) / 6
                    target_to_total_mean_hits[target] += mean_hits
        # First find the best target we can kill.
        for target, total_mean_hits in target_to_total_mean_hits.iteritems():
            if total_mean_hits >= target.hits_left:
                if (best_target is None or target.sort_value >
                  best_target.sort_value):
                    best_target = target
        # If we can't kill anything, go after the target we can hurt most.
        if best_target is None:
            max_total_mean_hits = 0
            for target, total_mean_hits in \
              target_to_total_mean_hits.iteritems():
                if total_mean_hits >= max_total_mean_hits:
                    best_target = target
                    max_total_mean_hits = total_mean_hits
        # Find the least valuable striker who can hit best_target.
        for striker in reversed(legion.sorted_creatures):
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                for hexlabel in hexlabels:
                    target = game.creatures_in_battle_hex(hexlabel).pop()
                    if target is best_target:
                        num_dice = striker.number_of_dice(target)
                        strike_number = striker.strike_number(target)
                        def1 = self.user.callRemote("strike", game.name,
                          striker.name, striker.hexlabel, target.name,
                          target.hexlabel, num_dice, strike_number)
                        def1.addErrback(self.failure)
                        return
        # No strikes, so end the strike phase.
        if game.battle_phase == Phase.STRIKE:
            def1 = self.user.callRemote("done_with_strikes",
              game.name)
            def1.addErrback(self.failure)
        else:
            if game.battle_phase != Phase.COUNTERSTRIKE:
                logging.info("wrong phase")
            def1 = self.user.callRemote("done_with_counterstrikes",
              game.name)
            def1.addErrback(self.failure)

    def carry(self, game, striker_name, striker_hexlabel, target_name,
      target_hexlabel, num_dice, strike_number, carries):
        striker = game.creatures_in_battle_hex(striker_hexlabel).pop()
        target = game.creatures_in_battle_hex(target_hexlabel).pop()
        carry_targets = []
        for creature in striker.engaged_enemies:
            if striker.can_carry_to(creature, target, num_dice, strike_number):
                carry_targets.append(creature)
        best_target = None
        # If there's only one carry target, it's easy.
        if len(carry_targets) == 1:
            best_target = carry_targets[0]
        # First find the best target we can kill.
        if best_target is None:
            for carry_target in carry_targets:
                if carries >= target.hits_left:
                    if (best_target is None or carry_target.sort_value >
                      best_target.sort_value):
                        best_target = carry_target
        # If we can't kill anything then go after the hardest target to hit.
        if best_target is None:
            best_num_dice = None
            best_strike_number = None
            for carry_target in carry_targets:
                num_dice2 = striker.number_of_dice(carry_target)
                strike_number2 = striker.strike_number(carry_target)
                if (best_target is None or num_dice2 < best_num_dice
                  or strike_number2 > best_strike_number):
                    best_target = carry_target
                    best_num_dice = num_dice2
                    best_strike_number = strike_number2
        def1 = self.user.callRemote("carry", game.name,
          best_target.name, best_target.hexlabel, carries)
        def1.addErrback(self.failure)

    def failure(self, error):
        log.err(error)
