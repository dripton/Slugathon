__copyright__ = "Copyright (c) 2010-2011 David Ripton"
__license__ = "GNU GPL v2"


"""Fast, stupid AI that makes moves randomly."""


import random

from zope.interface import implementer

from slugathon.game import Game, Phase
from slugathon.util.log import log
from slugathon.ai.Bot import Bot


@implementer(Bot)
class DimBot(object):
    def __init__(self, playername):
        self.playername = playername
        self.user = None

    def maybe_pick_color(self, game):
        log("maybe_pick_color")
        if game.next_playername_to_pick_color == self.playername:
            color = random.choice(game.colors_left)
            def1 = self.user.callRemote("pick_color", game.name, color)
            def1.addErrback(self.failure)

    def maybe_pick_first_marker(self, game, playername):
        log("maybe_pick_first_marker")
        if playername == self.playername:
            player = game.get_player_by_name(playername)
            markerid = self._choose_marker(player)
            self._pick_marker(game, self.playername, markerid)

    def _pick_marker(self, game, playername, markerid):
        log("pick_marker")
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

    def split(self, game):
        """Split if it's my turn."""
        log("split")
        if game.active_player.name == self.playername:
            player = game.active_player
            for legion in player.legions:
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
                elif len(legion) == 7 and player.markerids_left:
                    # Always split 5-2.  (DimBot is dim.)
                    new_markerid = self._choose_marker(player)
                    lst = legion.sorted_creatures
                    keep = lst[:-2]
                    keep_names = [creature.name for creature in keep]
                    split = lst[-2:]
                    split_names = [creature.name for creature in split]
                    def1 = self.user.callRemote("split_legion", game.name,
                      legion.markerid, new_markerid, keep_names,
                      split_names)
                    def1.addErrback(self.failure)
                    return

            # No splits, so move on to the next phase.
            def1 = self.user.callRemote("done_with_splits", game.name)
            def1.addErrback(self.failure)

    def move_legions(self, game):
        """For now, try to move all legions."""
        assert game.active_player.name == self.playername
        player = game.active_player
        move = None
        for legion in player.legions:
            if not legion.moved:
                moves = game.find_all_moves(legion, game.board.hexes[
                  legion.hexlabel], player.movement_roll)
                if moves:
                    move = random.choice(list(moves))
                    break
        if move is None:
            # No more legions can move.
            def1 = self.user.callRemote("done_with_moves", game.name)
            def1.addErrback(self.failure)
            return
        (hexlabel, entry_side) = move
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
          legion.markerid, hexlabel, entry_side, teleport, teleporting_lord)
        def1.addErrback(self.failure)

    def choose_engagement(self, game):
        """Resolve engagements."""
        log("choose_engagement")
        if (game.pending_summon or game.pending_reinforcement or
          game.pending_acquire):
            log("choose_engagement bailing early summon", game.pending_summon,
              "reinforcement", game.pending_reinforcement,
              "acquire", game.pending_acquire)
            return
        hexlabels = game.engagement_hexlabels
        if hexlabels:
            hexlabel = hexlabels.pop()
            log("calling resolve_engagement")
            def1 = self.user.callRemote("resolve_engagement", game.name,
              hexlabel)
            def1.addErrback(self.failure)
        else:
            log("calling done_with_engagements")
            def1 = self.user.callRemote("done_with_engagements", game.name)
            def1.addErrback(self.failure)

    def resolve_engagement(self, game, hexlabel, did_not_flee):
        """Resolve the engagement in hexlabel.

        For now only know how to flee or concede.
        """
        log("resolve_engagement", game, hexlabel, did_not_flee)
        attacker = None
        defender = None
        for legion in game.all_legions(hexlabel):
            if legion.player == game.active_player:
                attacker = legion
            else:
                defender = legion
        if attacker:
            log("attacker", attacker, attacker.player.name)
        if defender:
            log("defender", defender, defender.player.name)
        if not attacker or not defender:
            log("no attacker or defender; bailing")
            return
        if defender.player.name == self.playername:
            if defender.can_flee:
                if defender.score * 1.5 < attacker.score:
                    log("fleeing")
                    def1 = self.user.callRemote("flee", game.name,
                      defender.markerid)
                    def1.addErrback(self.failure)
                else:
                    log("fighting")
                    def1 = self.user.callRemote("fight", game.name,
                      attacker.markerid, defender.markerid)
                    def1.addErrback(self.failure)
            else:
                log("fighting")
                def1 = self.user.callRemote("fight", game.name,
                  attacker.markerid, defender.markerid)
                def1.addErrback(self.failure)
        elif attacker.player.name == self.playername:
            if defender.can_flee and not did_not_flee:
                log("waiting for defender")
                # Wait for the defender to choose before conceding.
                pass
            else:
                log("fighting")
                def1 = self.user.callRemote("fight", game.name,
                  attacker.markerid, defender.markerid)
                def1.addErrback(self.failure)
        else:
            log("not my engagement")

    def move_creatures(self, game):
        log("move creatures")
        assert game.battle_active_player.name == self.playername
        legion = game.battle_active_legion
        for creature in legion.sorted_living_creatures:
            moves = game.find_battle_moves(creature)
            if moves:
                move = random.choice(list(moves))
                log("calling move_creature", creature.name,
                  creature.hexlabel, move)
                def1 = self.user.callRemote("move_creature", game.name,
                  creature.name, creature.hexlabel, move)
                def1.addErrback(self.failure)
                return
        # No moves, so end the maneuver phase.
        log("calling done_with_maneuvers")
        def1 = self.user.callRemote("done_with_maneuvers", game.name)
        def1.addErrback(self.failure)

    def strike(self, game):
        log("strike")
        assert game.battle_active_player.name == self.playername
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
        for striker in legion.sorted_creatures:
            if striker.can_strike:
                hexlabels = striker.find_target_hexlabels()
                hexlabel = random.choice(list(hexlabels))
                target = game.creatures_in_battle_hex(hexlabel).pop()
                num_dice = striker.number_of_dice(target)
                strike_number = striker.strike_number(target)
                def1 = self.user.callRemote("strike", game.name,
                  striker.name, striker.hexlabel, target.name, target.hexlabel,
                  num_dice, strike_number)
                def1.addErrback(self.failure)
                return
        # No strikes, so end the strike phase.
        if game.battle_phase == Phase.STRIKE:
            def1 = self.user.callRemote("done_with_strikes",
              game.name)
            def1.addErrback(self.failure)
        else:
            assert game.battle_phase == Phase.COUNTERSTRIKE
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
        carry_target = random.choice(carry_targets)
        def1 = self.user.callRemote("carry", game.name,
          carry_target.name, carry_target.hexlabel, carries)
        def1.addErrback(self.failure)

    def recruit(self, game):
        log("recruit")
        if game.active_player.name != self.playername:
            log("not my turn")
            return
        player = game.active_player
        for legion in player.legions:
            if legion.moved and legion.can_recruit:
                masterhex = game.board.hexes[legion.hexlabel]
                caretaker = game.caretaker
                mterrain = masterhex.terrain
                lst = legion.available_recruits_and_recruiters(mterrain,
                  caretaker)
                if lst:
                    # For now, just take the last one.
                    tup = lst[-1]
                    recruit = tup[0]
                    recruiters = tup[1:]
                    def1 = self.user.callRemote("recruit_creature", game.name,
                      legion.markerid, recruit, recruiters)
                    def1.addErrback(self.failure)
                    return
        def1 = self.user.callRemote("done_with_recruits", game.name)
        def1.addErrback(self.failure)

    def reinforce(self, game):
        """Reinforce, during the REINFORCE battle phase"""
        assert game.battle_active_player.name == self.playername
        assert game.battle_phase == Phase.REINFORCE
        legion = game.defender_legion
        assert legion.player.name == self.playername
        mterrain = game.battlemap.mterrain
        caretaker = game.caretaker
        if game.battle_turn == 4 and legion.can_recruit:
            lst = legion.available_recruits_and_recruiters(mterrain, caretaker)
            if lst:
                # For now, just take the last one.
                tup = lst[-1]
                recruit = tup[0]
                recruiters = tup[1:]
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markerid, recruit, recruiters)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("done_with_reinforcements", game.name)
        def1.addErrback(self.failure)

    def reinforce_after(self, game):
        """Reinforce, after the battle"""
        legion = game.defender_legion
        assert legion.player.name == self.playername
        mterrain = game.battlemap.mterrain
        caretaker = game.caretaker
        if legion.can_recruit:
            lst = legion.available_recruits_and_recruiters(mterrain, caretaker)
            if lst:
                # For now, just take the last one.
                tup = lst[-1]
                recruit = tup[0]
                recruiters = tup[1:]
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markerid, recruit, recruiters)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_reinforce", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

    def summon(self, game):
        """Summon, during the REINFORCE battle phase"""
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
                def1 = self.user.callRemote("summon_angel", game.name,
                  legion.markerid, donor.markerid, summonable.name)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_summon", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

        def1 = self.user.callRemote("done_with_reinforcements", game.name)
        def1.addErrback(self.failure)

    def summon_after(self, game):
        """Summon, after the battle is over."""
        log("summon_after")
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
                def1 = self.user.callRemote("summon_angel", game.name,
                  legion.markerid, donor.markerid, summonable.name)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_summon", game.name,
          legion.markerid)
        def1.addErrback(self.failure)

    def acquire_angel(self, game, markerid, num_angels, num_archangels):
        log("acquire_angel", markerid, num_angels, num_archangels)
        player = game.get_player_by_name(self.playername)
        legion = player.markerid_to_legion[markerid]
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
            log("calling acquire_angels", markerid, angel_names)
            def1 = self.user.callRemote("acquire_angels", game.name,
              markerid, angel_names)
            def1.addErrback(self.failure)
        else:
            log("calling do_not_acquire", markerid)
            def1 = self.user.callRemote("do_not_acquire", game.name,
              markerid)
            def1.addErrback(self.failure)

    def failure(self, error):
        log("failure", self, error)
