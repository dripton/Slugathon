#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"

"""Outward-facing facade for AI."""


import argparse
import random
import tempfile
import os
import sys

from twisted.spread import pb
from twisted.cred import credentials
from twisted.internet import reactor, defer
from twisted.internet.error import ReactorNotRunning
from twisted.python import log
from zope.interface import implementer

from slugathon.net import config
from slugathon.util.Observer import IObserver
from slugathon.util.Observed import Observed
from slugathon.game import Action, Game, Phase, Creature
from slugathon.ai import DimBot, CleverBot, predictsplits
from slugathon.data.creaturedata import starting_creature_names


TEMPDIR = tempfile.gettempdir()


defer.setDebugging(True)


@implementer(IObserver)
class AIClient(pb.Referenceable, Observed):
    def __init__(self, username, password, host, port, delay, aitype,
      game_name, log_path, time_limit, form_game, min_players, max_players):
        Observed.__init__(self)
        self.username = username
        self.playername = username  # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
        self.delay = delay
        self.factory = pb.PBClientFactory()
        self.factory.unsafeTracebacks = True
        self.user = None
        self.usernames = set()
        self.games = []
        if log_path:
            log.startLogging(open(log_path, "w"), setStdout=False)
        log.msg("AIClient", username, password, host, port, delay, aitype,
          game_name, log_path, time_limit, form_game, min_players, max_players)
        if aitype == "CleverBot":
            self.ai = CleverBot.CleverBot(self.playername, time_limit)
        elif aitype == "DimBot":
            self.ai = DimBot.DimBot(self.playername)
        else:
            raise ValueError("invalid aitype %s" % aitype)
        self.game_name = game_name
        self.log_path = log_path
        self.time_limit = time_limit
        self.form_game = form_game
        self.min_players = min_players
        self.max_players = max_players
        self.paused = False
        self.last_actions = []
        log.msg("aps = AllPredictSplits()")
        self.aps = predictsplits.AllPredictSplits()
        log.msg("__init__ done", game_name, username)

    def remote_set_name(self, name):
        self.playername = name

    def remote_ping(self, arg):
        return True

    def __repr__(self):
        return "AIClient " + str(self.username)

    def connect(self):
        user_pass = credentials.UsernamePassword(self.username, self.password)
        reactor.connectTCP(self.host, self.port, self.factory)
        def1 = self.factory.login(user_pass, self)
        def1.addCallback(self.connected)
        def1.addErrback(self.connection_failed)

    def connected(self, user):
        log.msg("connected")
        if user:
            self.user = user
            self.ai.user = user
            def1 = user.callRemote("get_usernames")
            def1.addCallback(self.got_usernames)
            def1.addErrback(self.failure)

    def connection_failed(self, arg):
        log.err(arg)

    def got_usernames(self, usernames):
        """Only called when the client first connects to the server."""
        log.msg("got usernames", usernames)
        self.usernames.clear()
        for username in usernames:
            self.usernames.add(username)
        def1 = self.user.callRemote("get_games")
        def1.addCallback(self.got_games)
        def1.addErrback(self.failure)

    def got_games(self, game_info_tuples):
        """Only called when the client first connects to the server."""
        log.msg("got games", game_info_tuples)
        del self.games[:]
        for game_info_tuple in game_info_tuples:
            self.add_game(game_info_tuple)
        if self.form_game:
            if not self.game_name:
                self.game_name = "Game_%d" % random.randrange(1000000)
            if not self.log_path:
                self.log_path = os.path.join(TEMPDIR, "slugathon-%s-%s.log" %
                  (self.game_name, self.playername))
                log.startLogging(open(self.log_path, "w"), setStdout=False)
                log.startLogging(sys.stdout)
            def1 = self.user.callRemote("form_game", self.game_name,
              self.min_players, self.max_players, self.time_limit)
            def1.addErrback(self.failure)
        else:
            # If game_name is set, AI only tries to join game with that name.
            # If game_name is null, AI tries to join all games.
            for game in self.games:
                if not self.game_name or game.name == self.game_name:
                    log.msg("joining game", game.name)
                    def1 = self.user.callRemote("join_game", game.name)
                    def1.addErrback(self.failure)

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def add_game(self, game_info_tuple):
        log.msg("add_game", game_info_tuple)
        (name, create_time, start_time, min_players, max_players,
          playernames, started) = game_info_tuple
        owner = playernames[0]
        game = Game.Game(name, owner, create_time, start_time, min_players,
          max_players, started)
        self.add_observer(game)
        for playername in playernames[1:]:
            game.add_player(playername)
        self.games.append(game)
        if not self.game_name or game.name == self.game_name:
            def1 = self.user.callRemote("join_game", game.name)
            def1.addErrback(self.failure)

    def remove_game(self, game_name):
        game = self.name_to_game(game_name)
        if game:
            self.remove_observer(game)
            self.games.remove(game)

    # TODO Restrict to one player.
    def update_creatures(self, game):
        """Update creatures in game from self.aps."""
        for legion in game.all_legions():
            markerid = legion.markerid
            node = self.aps.get_leaf(markerid)
            if node.creature_names != legion.creature_names:
                legion.creatures = Creature.n2c(node.creature_names)
                for creature in legion.creatures:
                    creature.legion = legion

    def failure(self, error):
        log.err(error)

    def remote_receive_chat_message(self, text):
        pass

    def remote_update(self, action, names):
        """Near-IObserver on the remote User, except observed is
        not passed remotely.

        Delegates to update to honor the interface.
        """
        observed = None
        self.update(observed, action, names)

    def update(self, observed, action, names):
        """Updates from User will come via remote_update, with
        observed set to None."""
        log.msg("AIClient.update", action)

        if (self.game_name is not None and hasattr(action, "game_name")
          and action.game_name != self.game_name):
            return

        if isinstance(action, Action.ResumeAI):
            self.paused = False
            while self.last_actions:
                action = self.last_actions.pop(0)
                self.update(None, action, None)
            return

        # Make sure that Game knows that the angel is in the donor
        # legion before we send the Action to Game.
        if isinstance(action, Action.SummonAngel):
            game = self.name_to_game(action.game_name)
            self.aps.get_leaf(action.donor_markerid).reveal_creatures(
              [action.creature_name])
            self.update_creatures(game)

        # Update the Game first, then act.
        self.notify(action, names)

        if self.paused:
            self.last_actions.append(action)
            return

        if isinstance(action, Action.AddUsername):
            self.usernames.add(action.username)

        elif isinstance(action, Action.DelUsername):
            self.usernames.remove(action.username)

        elif isinstance(action, Action.FormGame):
            game_info_tuple = (action.game_name, action.create_time,
              action.start_time, action.min_players, action.max_players,
              [action.username], False)
            self.add_game(game_info_tuple)
            if action.username == self.username:
                def1 = self.user.callRemote("start_game", self.game_name)
                def1.addErrback(self.failure)

        elif isinstance(action, Action.RemoveGame):
            self.remove_game(action.game_name)

        elif isinstance(action, Action.AssignedAllTowers):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.maybe_pick_color, game)

        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            self.ai.maybe_pick_color(game)
            reactor.callLater(self.delay, self.ai.maybe_pick_first_marker,
              game, action.playername)

        elif isinstance(action, Action.AssignedAllColors):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)

        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                log.msg("Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names)))
            else:
                log.msg("Game %s over, draw" % action.game_name)
            log.msg("AI exiting")
            try:
                reactor.stop()
            except ReactorNotRunning:
                pass

        elif isinstance(action, Action.StartSplitPhase):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)

        elif isinstance(action, Action.CreateStartingLegion):
            game = self.name_to_game(action.game_name)
            log.msg("ps = PredictSplits('%s', '%s', %s)" %
              (action.playername, action.markerid, starting_creature_names))
            ps = predictsplits.PredictSplits(action.playername,
              action.markerid, starting_creature_names)
            log.msg("aps.append(ps)")
            self.aps.append(ps)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)

        elif isinstance(action, Action.SplitLegion):
            game = self.name_to_game(action.game_name)
            log.msg("aps.get_leaf('%s').split(%d, '%s', %d)" %
              (action.parent_markerid, len(action.child_creature_names),
              action.child_markerid, game.turn))
            self.aps.get_leaf(action.parent_markerid).split(
              len(action.child_creature_names), action.child_markerid,
              game.turn)
            if action.parent_creature_names[0] != "Unknown":
                self.aps.get_leaf(action.parent_markerid).reveal_creatures(
                  list(action.parent_creature_names))
                self.aps.get_leaf(action.child_markerid).reveal_creatures(
                  list(action.child_creature_names))
            self.update_creatures(game)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.split, game)

        elif isinstance(action, Action.UndoSplit):
            game = self.name_to_game(action.game_name)
            log.msg(
              "self.aps.get_leaf('%s').merge(self.aps.get_leaf('%s'), %d)" %
              (action.parent_markerid, action.child_markerid, game.turn))
            self.aps.get_leaf(action.parent_markerid).merge(
              self.aps.get_leaf(action.child_markerid), game.turn)
            self.update_creatures(game)

        elif isinstance(action, Action.RollMovement):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.move_legions, game)

        elif isinstance(action, Action.MoveLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.move_legions, game)

        elif isinstance(action, Action.StartFightPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.ai.choose_engagement, game)

        elif isinstance(action, Action.StartMusterPhase):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                reactor.callLater(self.delay, self.ai.recruit, game)

        elif isinstance(action, Action.ResolvingEngagement):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.resolve_engagement, game,
              action.hexlabel, False)

        elif (isinstance(action, Action.Flee) or
          isinstance(action, Action.Concede)):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)

        elif isinstance(action, Action.DoNotFlee):
            game = self.name_to_game(action.game_name)
            reactor.callLater(self.delay, self.ai.resolve_engagement, game,
              action.hexlabel, True)

        elif isinstance(action, Action.Fight):
            game = self.name_to_game(action.game_name)
            player = game.get_player_by_name(self.playername)
            # XXX We double check the player, in case the last battle didn't
            # get cleaned up.  (We don't call Game._end_battle2 on the client.)
            if (game.defender_legion and game.defender_legion.player.name ==
              self.playername and action.defender_markerid in
              player.markerid_to_legion):
                reactor.callLater(self.delay, self.ai.move_creatures, game)

        elif isinstance(action, Action.MoveCreature):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.move_creatures, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.StartStrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.strike, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.Strike):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if action.carries:
                        reactor.callLater(self.delay, self.ai.carry, game,
                          action.striker_name, action.striker_hexlabel,
                          action.target_name, action.target_hexlabel,
                          action.num_dice, action.strike_number,
                          action.carries)
                    else:
                        reactor.callLater(self.delay, self.ai.strike, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.Carry):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if action.carries_left:
                        reactor.callLater(self.delay, self.ai.carry, game,
                          action.striker_name, action.striker_hexlabel,
                          action.target_name, action.target_hexlabel,
                          action.num_dice, action.strike_number,
                          action.carries_left)
                    else:
                        reactor.callLater(self.delay, self.ai.strike, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.strike, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.StartReinforceBattlePhase):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    if legion == game.defender_legion:
                        reactor.callLater(self.delay, self.ai.reinforce, game)
                    else:
                        reactor.callLater(self.delay, self.ai.summon, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.StartManeuverBattlePhase):
            game = self.name_to_game(action.game_name)
            legion = game.battle_active_legion
            if legion:
                if legion.player.name == self.playername:
                    reactor.callLater(self.delay, self.ai.move_creatures, game)
            else:
                log.msg("game.battle_active_legion not found")

        elif isinstance(action, Action.RecruitCreature):
            game = self.name_to_game(action.game_name)
            self.aps.get_leaf(action.markerid).reveal_creatures(
              list(action.recruiter_names))
            log.msg("aps.get_leaf('%s').add_creature('%s')" %
              (action.markerid, action.creature_name))
            self.aps.get_leaf(action.markerid).add_creature(
              action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.phase == Phase.MUSTER:
                    if game.active_player.name == self.playername:
                        reactor.callLater(self.delay, self.ai.recruit, game)
                elif game.phase == Phase.FIGHT:
                    if game.battle_phase == Phase.REINFORCE:
                        reactor.callLater(self.delay, self.ai.reinforce, game)
                    else:
                        reactor.callLater(self.delay,
                          self.ai.choose_engagement, game)
            else:
                if (game.phase == Phase.FIGHT and
                  game.battle_phase != Phase.REINFORCE and
                  game.active_player.name == self.playername):
                    reactor.callLater(self.delay, self.ai.choose_engagement,
                      game)

        elif isinstance(action, Action.UndoRecruit):
            game = self.name_to_game(action.game_name)
            log.msg("aps.get_leaf('%s').remove_creature('%s')" %
              (action.markerid, action.creature_name))
            self.aps.get_leaf(action.markerid).remove_creature(
              action.creature_name)
            self.update_creatures(game)

        elif isinstance(action, Action.UnReinforce):
            game = self.name_to_game(action.game_name)
            log.msg("aps.get_leaf('%s').remove_creature('%s')" %
              (action.markerid, action.creature_name))
            self.aps.get_leaf(action.markerid).remove_creature(
              action.creature_name)
            self.update_creatures(game)

        elif isinstance(action, Action.DoNotReinforce):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                assert game.phase == Phase.FIGHT
                reactor.callLater(self.delay, self.ai.choose_engagement, game)
            else:
                if (game.phase == Phase.FIGHT and
                  game.active_player.name == self.playername):
                    reactor.callLater(self.delay, self.ai.choose_engagement,
                      game)

        elif isinstance(action, Action.SummonAngel):
            game = self.name_to_game(action.game_name)
            self.aps.get_leaf(action.donor_markerid).reveal_creatures(
              [action.creature_name])
            log.msg("aps.get_leaf('%s').remove_creature('%s')" %
              (action.donor_markerid, action.creature_name))
            self.aps.get_leaf(action.donor_markerid).remove_creature(
              action.creature_name)
            log.msg("aps.get_leaf('%s').add_creature('%s')" %
              (action.markerid, action.creature_name))
            self.aps.get_leaf(action.markerid).add_creature(
              action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon, game)
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement,
                      game)

        elif isinstance(action, Action.UnsummonAngel):
            game = self.name_to_game(action.game_name)
            self.aps.get_leaf(action.markerid).reveal_creatures(
              [action.creature_name])
            log.msg("aps.get_leaf('%s').remove_creature('%s')" %
              (action.markerid, action.creature_name))
            self.aps.get_leaf(action.markerid).remove_creature(
              action.creature_name)
            log.msg("aps.get_leaf('%s').add_creature('%s')" %
              (action.donor_markerid, action.creature_name))
            self.aps.get_leaf(action.donor_markerid).add_creature(
              action.creature_name)
            self.update_creatures(game)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon, game)
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement,
                      game)

        elif isinstance(action, Action.DoNotSummonAngel):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                if game.battle_phase == Phase.REINFORCE:
                    reactor.callLater(self.delay, self.ai.summon, game)
                else:
                    reactor.callLater(self.delay, self.ai.choose_engagement,
                      game)

        elif isinstance(action, Action.BattleOver):
            game = self.name_to_game(action.game_name)
            if action.winner_losses:
                log.msg("aps.get_leaf('%s').remove_creatures(%s)" %
                  (action.winner_markerid, list(action.winner_losses)))
                self.aps.get_leaf(action.winner_markerid).remove_creatures(
                  list(action.winner_losses))
            if action.loser_losses:
                log.msg("aps.get_leaf('%s').remove_creatures(%s)" %
                  (action.loser_markerid, list(action.loser_losses)))
                self.aps.get_leaf(action.loser_markerid).remove_creatures(
                  list(action.loser_losses))
            self.update_creatures(game)
            if game.active_player.name == self.playername:
                if game.attacker_legion:
                    legion = game.attacker_legion
                    if (legion.markerid == action.winner_markerid and
                      legion.can_summon):
                        reactor.callLater(self.delay, self.ai.summon_after,
                          game)
                        return
            else:
                if game.defender_legion:
                    legion = game.defender_legion
                    if legion.player.name == self.playername:
                        if (legion.markerid == action.winner_markerid and
                          legion.can_recruit):
                            reactor.callLater(self.delay,
                              self.ai.reinforce_after, game)
                            return
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)

        elif isinstance(action, Action.CanAcquireAngels):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                reactor.callLater(self.delay, self.ai.acquire_angels, game,
                  action.markerid, action.angels, action.archangels)

        elif isinstance(action, Action.AcquireAngels):
            game = self.name_to_game(action.game_name)
            for angel_name in action.angel_names:
                log.msg("aps.get_leaf('%s').add_creature('%s')" %
                  (action.markerid, angel_name))
                self.aps.get_leaf(action.markerid).add_creature(angel_name)
            self.update_creatures(game)
            log.msg("active player", game.active_player)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)

        elif isinstance(action, Action.DoNotAcquireAngels):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                reactor.callLater(self.delay, self.ai.choose_engagement, game)

        elif isinstance(action, Action.EliminatePlayer):
            game = self.name_to_game(action.game_name)
            if action.loser_playername == self.playername:
                if game.owner.name != self.playername:
                    log.msg("Eliminated; AI exiting")
                    try:
                        reactor.stop()
                    except ReactorNotRunning:
                        return
            # Remove the dead player's PredictSplits from self.aps
            # to avoid problems later if his markers get reused.
            player = game.get_player_by_name(action.loser_playername)
            color_abbrev = player.color_abbrev
            for ps in self.aps:
                for node in ps.get_nodes():
                    if node.markerid.startswith(color_abbrev):
                        self.aps.remove(ps)
                        break

        elif isinstance(action, Action.RevealLegion):
            game = self.name_to_game(action.game_name)
            legion = game.find_legion(action.markerid)
            if legion:
                legion.reveal_creatures(action.creature_names)
                node = self.aps.get_leaf(action.markerid)
                # XXX There are edge cases where the legion still exists
                # but the node is gone.
                if node is not None:
                    node.reveal_creatures(action.creature_names)
                self.update_creatures(game)

        elif isinstance(action, Action.PauseAI):
            self.paused = True

        else:
            log.msg("got unhandled action", action)


def add_arguments(parser):
    parser.add_argument("-n", "--playername", action="store", type=str)
    parser.add_argument("-a", "--password", action="store", type=str)
    parser.add_argument("-s", "--server", action="store", type=str,
      default="localhost")
    parser.add_argument("-p", "--port", action="store", type=int,
      default=config.DEFAULT_PORT)
    parser.add_argument("-d", "--delay", action="store", type=float,
      default=config.DEFAULT_AI_DELAY)
    parser.add_argument("-t", "--aitype", action="store", type=str,
      default="CleverBot")
    parser.add_argument("-g", "--game-name", action="store", type=str)
    parser.add_argument("-l", "--log-path", action="store", type=str)
    parser.add_argument("--time-limit", action="store", type=int,
      default=config.DEFAULT_AI_TIME_LIMIT)
    parser.add_argument("--form-game", action="store_true", default=False)
    parser.add_argument("--min-players", type=int, default=2)
    parser.add_argument("--max-players", type=int, default=6)


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    opts, extras = parser.parse_known_args()
    valid_ai_types = ["CleverBot", "DimBot"]
    if opts.aitype not in valid_ai_types:
        parser.error("Invalid AI type.  Valid types are %s" % valid_ai_types)
    aiclient = AIClient(opts.playername, opts.password, opts.server, opts.port,
      opts.delay, opts.aitype, opts.game_name, opts.log_path, opts.time_limit,
      opts.form_game, opts.min_players, opts.max_players)
    aiclient.connect()
    reactor.run()


if __name__ == "__main__":
    main()
