#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"

"""Outward-facing facade for AI."""


import random
from optparse import OptionParser

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor
from zope.interface import implements

from slugathon.net import config
from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed
from slugathon.game import Action, Game, Phase


class Client(pb.Referenceable, Observed):

    implements(IObserver)

    def __init__(self, username, password, host, port, delay):
        Observed.__init__(self)
        self.username = username
        self.playername = username # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.delay = delay
        self.factory = pb.PBClientFactory()
        self.factory.unsafeTracebacks = True
        self.user = None
        self.anteroom = None
        self.usernames = set()
        self.games = []
        self.guiboards = {}   # Maps game to guiboard
        self.status_screens = {}   # Maps game to status_screen

    def remote_set_name(self, name):
        self.playername = name
        return name

    def remote_ping(self, arg):
        return True

    def __repr__(self):
        return "Client " + str(self.username)

    def connect(self):
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def connected(self, user):
        print "connected"
        if user:
            self.user = user
            def1 = user.callRemote("get_usernames")
            def1.addCallback(self.got_usernames)
            def1.addErrback(self.failure)

    def connection_failed(self, arg):
        print "connection failed"

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        print "got usernames", usernames
        self.usernames.clear()
        for username in usernames:
            self.usernames.add(username)
        def1 = self.user.callRemote("get_games")
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        print "got games", game_info_tuples
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        # For now, AI joins all games.
        for game in self.games:
            print "joining game", game.name
            def1 = self.user.callRemote("join_game", game.name)
            def1.addErrback(self.failure)

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def add_game(self, game_info_tuple):
        print "add_game", game_info_tuple
        (name, create_time, start_time, min_players, max_players,
          playernames) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players)
        self.add_observer(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        self.games.append(game)
        # For now, AI joins all games.
        def1 = self.user.callRemote("join_game", game.name)
        def1.addErrback(self.failure)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    def failure(self, error):
        print "Client.failure", self, error

    def remote_receive_chat_message(self, text):
        pass

    def remote_update(self, action):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action)

    def maybe_pick_color(self, game):
        print "maybe_pick_color"
        if game.next_playername_to_pick_color() == self.username:
            color = random.choice(game.colors_left())
            def1 = self.user.callRemote("pick_color", game.name, color)
            def1.addErrback(self.failure)

    def maybe_pick_first_marker(self, game, playername):
        print "maybe_pick_first_marker"
        if playername == self.username:
            player = game.get_player_by_name(playername)
            markername = random.choice(list(player.markernames))
            self.pick_marker(game.name, self.username, markername)

    def pick_marker(self, game_name, username, markername):
        print "pick_marker"
        game = self.name_to_game(game_name)
        player = game.get_player_by_name(username)
        if markername is None:
            if not player.legions:
                self.maybe_pick_first_marker(game, username)
        else:
            player.pick_marker(markername)
            if not player.legions:
                def1 = self.user.callRemote("pick_first_marker", game_name,
                  markername)
                def1.addErrback(self.failure)

    def split(self, game):
        """Split if it's my turn."""
        print "split"
        if game.active_player.name == self.playername:
            player = game.active_player
            for legion in player.legions.itervalues():
                if len(legion) == 8:
                    # initial split 4-4, one lord per legion
                    new_markername = random.choice(list(player.markernames))
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
                    # split 5-2.  For now, always split.
                    # TODO consider safety and what can be attacked
                    # or recruited
                    new_markername = random.choice(list(player.markernames))
                    lst = legion.sorted_creatures
                    keep = lst[:-2]
                    keep_names = [creature.name for creature in keep]
                    split = lst[-2:]
                    split_names = [creature.name for creature in split]
                    def1 = self.user.callRemote("split_legion", game.name,
                      legion.markername, new_markername, keep_names,
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
        legions = player.legions.values()
        move = None
        for legion in legions:
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
            # XXX Need to special-case tower?
            entry_side = random.choice([1, 3, 5])
            teleporting_lord = sorted(legion.lord_types)[-1]
        else:
            teleport = False
            teleporting_lord = None
        def1 = self.user.callRemote("move_legion", game.name,
          legion.markername, hexlabel, entry_side, teleport, teleporting_lord)
        def1.addErrback(self.failure)

    def choose_engagement(self, game):
        """Resolve engagements."""
        print "choose_engagement"
        hexlabels = game.engagement_hexlabels
        if hexlabels:
            hexlabel = hexlabels.pop()
            def1 = self.user.callRemote("resolve_engagement", game.name,
              hexlabel)
            def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("done_with_engagements", game.name)
            def1.addErrback(self.failure)

    def resolve_engagement(self, game, hexlabel, did_not_flee):
        """Resolve the engagement in hexlabel.

        For now only know how to flee or concede.
        """
        attacker = None
        defender = None
        for legion in game.all_legions(hexlabel):
            if legion.player == game.active_player:
                attacker = legion
            else:
                defender = legion
        if not attacker or not defender:
            return
        if defender.player.name == self.playername:
            if defender.can_flee:
                if defender.score * 1.5 < attacker.score:
                    def1 = self.user.callRemote("flee", game.name,
                      defender.markername)
                    def1.addErrback(self.failure)
                else:
                    def1 = self.user.callRemote("fight", game.name,
                      attacker.markername, defender.markername)
                    def1.addErrback(self.failure)
        else:
            if defender.can_flee and not did_not_flee:
                # Wait for the defender to choose before conceding.
                pass
            else:
                def1 = self.user.callRemote("fight", game.name,
                  attacker.markername, defender.markername)
                def1.addErrback(self.failure)

    def move_creatures(self, game):
        print "move creatures"
        assert game.battle_active_player.name == self.playername
        legion = game.battle_active_legion
        for creature in legion.sorted_creatures:
            moves = game.find_battle_moves(creature)
            if moves:
                move = random.choice(list(moves))
                print "calling move_creature", creature.name, \
                  creature.hexlabel, move
                def1 = self.user.callRemote("move_creature", game.name,
                  creature.name, creature.hexlabel, move)
                def1.addErrback(self.failure)
                return
        # No moves, so end the maneuver phase.
        print "calling done_with_maneuvers"
        def1 = self.user.callRemote("done_with_maneuvers", game.name)
        def1.addErrback(self.failure)

    def strike(self, game):
        print "strike"
        assert game.battle_active_player.name == self.playername
        legion = game.battle_active_legion
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
        print "recruit"
        assert game.active_player.name == self.playername
        player = game.active_player
        for legion in player.legions.itervalues():
            if legion.moved and not legion.recruited:
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
                      legion.markername, recruit, recruiters)
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
        if (game.battle_turn == 4 and
          len(legion.living_creature_names) < 7 and
          not legion.recruited and legion.can_recruit(mterrain, caretaker)):
            lst = legion.available_recruits_and_recruiters(mterrain, caretaker)
            if lst:
                # For now, just take the last one.
                tup = lst[-1]
                recruit = tup[0]
                recruiters = tup[1:]
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markername, recruit, recruiters)
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
        if (len(legion.living_creature_names) < 7 and
          not legion.recruited and legion.can_recruit(mterrain, caretaker)):
            lst = legion.available_recruits_and_recruiters(mterrain, caretaker)
            if lst:
                # For now, just take the last one.
                tup = lst[-1]
                recruit = tup[0]
                recruiters = tup[1:]
                def1 = self.user.callRemote("recruit_creature", game.name,
                  legion.markername, recruit, recruiters)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_reinforce", game.name,
          legion.markername)
        def1.addErrback(self.failure)


    def summon(self, game):
        """Summon, during the REINFORCE battle phase"""
        assert game.active_player.name == self.playername
        assert game.battle_phase == Phase.REINFORCE
        legion = game.attacker_legion
        assert legion.player.name == self.playername
        summonables = []
        if (len(legion.living_creature_names) < 7 and
          legion.can_summon and game.first_attacker_kill in
          [game.battle_turn - 1, game.battle_turn]):
            for legion2 in legion.player.legions.itervalues():
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
                  legion.markername, donor.markername, summonable.name)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_summon", game.name,
          legion.markername)
        def1.addErrback(self.failure)

        def1 = self.user.callRemote("done_with_reinforcements", game.name)
        def1.addErrback(self.failure)


    def summon_after(self, game):
        """Summon, after the battle is over."""
        assert game.active_player.name == self.playername
        legion = game.attacker_legion
        assert legion.player.name == self.playername
        summonables = []
        if (len(legion.living_creature_names) < 7 and
          legion.can_summon and game.first_attacker_kill in
          [game.battle_turn - 1, game.battle_turn]):
            for legion2 in legion.player.legions.itervalues():
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
                  legion.markername, donor.markername, summonable.name)
                def1.addErrback(self.failure)
                return

        def1 = self.user.callRemote("do_not_summon", game.name,
          legion.markername)
        def1.addErrback(self.failure)

    def acquire_angel(self, game, markername, angels, archangels):
        player = game.get_player_by_name(self.playername)
        legion = player.legions[markername]
        starting_height = len(legion)
        acquires = 0
        while starting_height + acquires < 7 and (angels or archangels):
            if archangels:
                def1 = self.user.callRemote("acquire_angel", game.name,
                  markername, "Archangel")
                def1.addErrback(self.failure)
                archangels -= 1
                acquires += 1
            elif angels:
                def1 = self.user.callRemote("acquire_angel", game.name,
                  markername, "Angel")
                def1.addErrback(self.failure)
                angels -= 1
                acquires += 1
        if player == game.active_player:
            self.choose_engagement(game)


    def update(self, observed, action):
        """Updates from User will come via remote_update, with
        observed set to None."""
        print "AIClient.update", action

        # Update the Game first, then act.
        self.notify(action)

        if isinstance(action, Action.AddUsername):
            self.usernames.add(action.username)

        elif isinstance(action, Action.DelUsername):
            self.usernames.remove(action.username)

        elif isinstance(action, Action.FormGame):
            game_info_tuple = (action.game_name, action.create_time,
              action.start_time, action.min_players, action.max_players,
              [action.username])
            self.add_game(game_info_tuple)

        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)

        elif isinstance(action, Action.AssignedAllTowers):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.maybe_pick_color, game)

        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            game.assign_color(action.playername, action.color)
            reactor.callLater(self.delay, self.maybe_pick_color, game)
            reactor.callLater(self.delay, self.maybe_pick_first_marker, game,
              action.playername)

        elif isinstance(action, Action.AssignedAllColors):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.split, game)

        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                print "Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names))
            else:
                print "Game %s over, draw" % action.game_name

        elif isinstance(action, Action.StartSplitPhase):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.split, game)

        elif isinstance(action, Action.CreateStartingLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.split, game)

        elif isinstance(action, Action.SplitLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.split, game)

        elif isinstance(action, Action.RollMovement):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.move_legions, game)

        elif isinstance(action, Action.MoveLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.move_legions, game)

        elif isinstance(action, Action.StartFightPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.choose_engagement, game)

        elif isinstance(action, Action.StartMusterPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.recruit, game)

        elif isinstance(action, Action.ResolvingEngagement):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.resolve_engagement, game,
              action.hexlabel, False)

        elif (isinstance(action, Action.Flee) or
          isinstance(action, Action.Concede)):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                if game.engagement_hexlabels:
                    reactor.callLater(self.delay, self.choose_engagement, game)
                else:
                    def1 = self.user.callRemote("done_with_engagements",
                      game.name)
                    def1.addErrback(self.failure)

        elif isinstance(action, Action.DoNotFlee):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.resolve_engagement, game,
              action.hexlabel, True)

        elif isinstance(action, Action.Fight):
            game = self.name_to_game(action.game_name)
            if game.defender_legion.player.name == self.playername:
                reactor.callLater(self.delay, self.move_creatures, game)

        elif isinstance(action, Action.MoveCreature):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                reactor.callLater(self.delay, self.move_creatures, game)

        elif isinstance(action, Action.StartStrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                reactor.callLater(self.delay, self.strike, game)

        elif isinstance(action, Action.Strike):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                if action.carries:
                    reactor.callLater(self.delay, self.carry, game,
                      action.striker_name, action.striker_hexlabel,
                      action.target_name, action.target_hexlabel,
                      action.num_dice, action.strike_number, action.carries)
                else:
                    reactor.callLater(self.delay, self.strike, game)

        elif isinstance(action, Action.Carry):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                if action.carries_left:
                    reactor.callLater(self.delay, self.carry, game,
                      action.striker_name, action.striker_hexlabel,
                      action.target_name, action.target_hexlabel,
                      action.num_dice, action.strike_number,
                      action.carries_left)
                else:
                    reactor.callLater(self.delay, self.strike, game)

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                reactor.callLater(self.delay, self.strike, game)

        elif isinstance(action, Action.StartReinforceBattlePhase):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                legion = game.battle_active_legion
                if legion == game.defender_legion:
                    reactor.callLater(self.delay, self.reinforce, game)
                else:
                    reactor.callLater(self.delay, self.summon, game)

        elif isinstance(action, Action.StartManeuverBattlePhase):
            game = self.name_to_game(action.game_name)
            if game.battle_active_legion.player.name == self.playername:
                reactor.callLater(self.delay, self.move_creatures, game)

        elif isinstance(action, Action.RecruitCreature):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                if game.phase == Phase.MUSTER:
                    if game.active_player.name == self.playername:
                        reactor.callLater(self.delay, self.recruit, game)
                elif game.phase == Phase.FIGHT:
                    if game.battle_phase == Phase.REINFORCE:
                        reactor.callLater(self.delay, self.reinforce, game)
                    else:
                        reactor.callLater(self.delay, self.choose_engagement,
                          game)
            else:
                if (game.phase == Phase.FIGHT and
                  game.battle_phase != Phase.REINFORCE and
                  game.active_player.name == self.playername):
                    reactor.callLater(self.delay, self.choose_engagement, game)


        elif isinstance(action, Action.DoNotReinforce):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                assert game.phase == Phase.FIGHT
                reactor.callLater(self.delay, self.choose_engagement, game)
            else:
                if (game.phase == Phase.FIGHT and
                  game.active_player.name == self.playername):
                    reactor.callLater(self.delay, self.choose_engagement, game)

        elif isinstance(action, Action.SummonAngel):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.summon, game)
                else:
                    reactor.callLater(self.delay, self.choose_engagement, game)

        elif isinstance(action, Action.DoNotSummon):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.summon, game)
                else:
                    reactor.callLater(self.delay, self.choose_engagement, game)

        elif isinstance(action, Action.BattleOver):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                if game.attacker_legion:
                    legion = game.attacker_legion
                    if legion.can_summon:
                        reactor.callLater(self.delay, self.summon_after, game)
                        return
            else:
                if game.defender_legion:
                    legion = game.defender_legion
                    if legion.player.name == self.playername:
                        mterrain = game.board.hexes[legion.hexlabel].terrain
                        if not legion.recruited and legion.can_recruit(
                          mterrain, game.caretaker):
                            reactor.callLater(self.delay, self.reinforce_after,
                              game)
                            return
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.choose_engagement, game)

        elif isinstance(action, Action.AcquireAngels):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.acquire_angel, game,
                  action.markername, action.angels, action.archangels)

        else:
            print "got unhandled action", action



def main():
    op = OptionParser()
    op.add_option("-n", "--playername", action="store", type="str")
    op.add_option("-a", "--password", action="store", type="str")
    op.add_option("-s", "--server", action="store", type="str",
      default="localhost")
    op.add_option("-p", "--port", action="store", type="int",
      default=config.DEFAULT_PORT)
    op.add_option("-d", "--delay", action="store", type="float",
      default=config.DEFAULT_AI_DELAY)
    opts, args = op.parse_args()
    if args:
        op.error("got illegal argument")
    client = Client(opts.playername, opts.password, opts.server, opts.port,
      opts.delay)
    client.connect()
    reactor.run()

if __name__ == "__main__":
    main()
