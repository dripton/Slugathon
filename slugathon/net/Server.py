#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2011 David Ripton"
__license__ = "GNU GPL v2"


import os
import time
import argparse
import tempfile
import sys
import random
import hashlib

from twisted.spread import pb
from twisted.cred.portal import Portal
from twisted.internet import reactor, protocol
from twisted.python import log
from zope.interface import implementer

from slugathon.net import Realm, config
from slugathon.game import Game, Action
from slugathon.util.Observed import Observed
from slugathon.util.Observer import IObserver
from slugathon.net.UniqueFilePasswordDB import UniqueFilePasswordDB
from slugathon.net.UniqueNoPassword import UniqueNoPassword
from slugathon.util import prefs


TEMPDIR = tempfile.gettempdir()


@implementer(IObserver)
class Server(Observed):
    """A Slugathon server, which can host multiple games in parallel."""
    def __init__(self, no_passwd, passwd_path, port, log_path):
        Observed.__init__(self)
        self.no_passwd = no_passwd
        self.passwd_path = passwd_path
        self.port = port
        self.games = []
        self.name_to_user = {}
        # {game_name: set(ainame) we're waiting for
        self.game_to_waiting_ais = {}
        log.startLogging(sys.stdout)
        if log_path:
            log.startLogging(open(log_path, "w"))

    def add_observer(self, user):
        username = user.name
        Observed.add_observer(self, user, username)
        self.name_to_user[username] = user
        action = Action.AddUsername(username)
        self.notify(action)

    def remove_observer(self, user):
        Observed.remove_observer(self, user)
        username = user.name
        if username in self.name_to_user:
            del self.name_to_user[username]
            action = Action.DelUsername(username)
            self.notify(action)

    @property
    def usernames(self):
        return sorted(self.name_to_user.iterkeys())

    def name_to_game(self, game_name):
        for game in self.games:
            if game.name == game_name:
                return game
        return None

    def send_chat_message(self, source, dest, text):
        """Send a chat message from user source to users in dest.

        source is a username.  dest is a set of usernames.
        If dest is None, send to all users
        """
        message = "%s: %s" % (source, text)
        if dest is None:
            dest = self.name_to_user.iterkeys()
        else:
            dest.add(source)
        for username in dest:
            user = self.name_to_user[username]
            user.receive_chat_message(message)

    def form_game(self, username, game_name, min_players, max_players):
        if not game_name:
            raise ValueError("Games must be named")
        if game_name in [game.name for game in self.games]:
            raise ValueError('The game name "%s" is already in use'
              % game_name)
        if min_players > max_players:
            raise ValueError("min_players must be <= max_players")
        now = time.time()
        GAME_START_DELAY = 5 * 60
        game = Game.Game(game_name, username, now, now + GAME_START_DELAY,
          min_players, max_players, master=True)
        self.games.append(game)
        game.add_observer(self)
        action = Action.FormGame(username, game.name, game.create_time,
          game.start_time, game.min_players, game.max_players)
        self.notify(action)

    def join_game(self, username, game_name):
        log.msg("join_game", username, game_name)
        game = self.name_to_game(game_name)
        if game:
            try:
                game.add_player(username)
            except AssertionError, ex:
                log.msg("join_game caught", ex)
            else:
                action = Action.JoinGame(username, game.name)
                self.notify(action)
            set1 = self.game_to_waiting_ais.get(game_name)
            if set1:
                set1.discard(username)
                if not set1:
                    game = self.name_to_game(game_name)
                    reactor.callLater(1, game.start, game.owner.name)

    def drop_from_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            try:
                game.remove_player(username)
            except AssertionError:
                pass
            else:
                if len(game.players) == 0:
                    if game in self.games:
                        self.games.remove(game)
                    action = Action.RemoveGame(game.name)
                    self.notify(action)
                else:
                    action = Action.DropFromGame(username, game.name)
                    self.notify(action)

    def start_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            if username != game.owner.name:
                raise AssertionError("Game.start %s called by non-owner %s"
                  % (self.name, username))
            if game.num_players_joined < game.min_players:
                self._spawn_ais(game)
            else:
                game.start(username)

    def _passwd_for_username(self, username):
        with open(self.passwd_path) as fil:
            for line in fil:
                user, passwd = line.strip().split(":")
                if user == username:
                    return passwd
        return None

    def _next_unused_ainames(self, num):
        ainames = []
        ii = 1
        while True:
            ainame = "ai%d" % ii
            if ainame not in self.usernames:
                ainames.append(ainame)
                if len(ainames) == num:
                    return ainames
            ii += 1

    def _add_username_with_random_password(self, ainame):
        password = hashlib.md5(str(random.random())).hexdigest()
        with open(self.passwd_path, "a") as fil:
            fil.write("%s:%s\n" % (ainame, password))

    def _spawn_ais(self, game):
        num_ais = game.min_players - game.num_players_joined
        ainames = self._next_unused_ainames(num_ais)
        for ainame in ainames:
            if self._passwd_for_username(ainame) is None:
                self._add_username_with_random_password(ainame)
        self.game_to_waiting_ais[game.name] = set()
        # Add all AIs to the wait list first, to avoid a race.
        for ainame in ainames:
            self.game_to_waiting_ais[game.name].add(ainame)
        if hasattr(sys, "frozen"):
            # TODO Find the absolute path.
            executable = "slugathon.exe"
        else:
            executable = sys.executable
        for ainame in ainames:
            log.msg("ainame", ainame)
            pp = AIProcessProtocol(self, game.name, ainame)
            args = [executable]
            if hasattr(sys, "frozen"):
                args.extend(["ai"])
            else:
                args.extend(["-m", "slugathon.ai.AIClient"])
            args.extend([
                "--playername", ainame,
                "--port", str(self.port),
                "--game-name", game.name,
                "--log-path", os.path.join(TEMPDIR, "slugathon-%s-%s.log" %
                  (game.name, ainame)),
            ])
            if not self.no_passwd:
                aipass = self._passwd_for_username(ainame)
                if aipass is None:
                    log.msg("user %s is not in %s; ai will fail to join" % (
                        ainame, self.passwd_path))
                else:
                    args.extend(["--password", aipass])
            reactor.spawnProcess(pp, executable, args=args, env=os.environ)

    def pick_color(self, username, game_name, color):
        game = self.name_to_game(game_name)
        if game:
            game.assign_color(username, color)

    def pick_first_marker(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.assign_first_marker(username, markerid)

    def split_legion(self, username, game_name, parent_markerid,
      child_markerid, parent_creature_names, child_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.split_legion(username, parent_markerid, child_markerid,
              parent_creature_names, child_creature_names)

    def undo_split(self, username, game_name, parent_markerid,
      child_markerid):
        game = self.name_to_game(game_name)
        if game:
            game.undo_split(username, parent_markerid, child_markerid)

    def done_with_splits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_splits(username)

    def take_mulligan(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.take_mulligan(username)

    def move_legion(self, username, game_name, markerid, hexlabel,
      entry_side, teleport, teleporting_lord):
        game = self.name_to_game(game_name)
        if game:
            player = game.get_player_by_name(username)
            legion = player.markerid_to_legion[markerid]
            if not game.can_move_legion(player, legion, hexlabel, entry_side,
              teleport, teleporting_lord):
                raise AssertionError("illegal move attempt", player, legion,
                  hexlabel, entry_side, teleport, teleporting_lord,
                  game.all_legions())
            game.move_legion(username, markerid, hexlabel, entry_side,
              teleport, teleporting_lord)

    def undo_move_legion(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.undo_move_legion(username, markerid)

    def done_with_moves(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_moves(username)

    def resolve_engagement(self, username, game_name, hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.resolve_engagement(username, hexlabel)

    def flee(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.flee(username, markerid)

    def do_not_flee(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.do_not_flee(username, markerid)

    def concede(self, username, game_name, markerid, enemy_markerid,
      hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.concede(username, markerid)

    def make_proposal(self, username, game_name, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.make_proposal(username, attacker_markerid,
              attacker_creature_names, defender_markerid,
              defender_creature_names)

    def accept_proposal(self, username, game_name, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.accept_proposal(username, attacker_markerid,
              attacker_creature_names, defender_markerid,
              defender_creature_names)

    def reject_proposal(self, username, game_name, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.reject_proposal(username, attacker_markerid,
              attacker_creature_names, defender_markerid,
              defender_creature_names)

    def fight(self, username, game_name, attacker_markerid,
      defender_markerid):
        game = self.name_to_game(game_name)
        if game:
            game.fight(username, attacker_markerid, defender_markerid)

    def move_creature(self, username, game_name, creature_name, old_hexlabel,
      new_hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.move_creature(username, creature_name, old_hexlabel,
              new_hexlabel)

    def undo_move_creature(self, username, game_name, creature_name,
      new_hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.undo_move_creature(username, creature_name, new_hexlabel)

    def done_with_reinforcements(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_reinforcements(username)

    def done_with_maneuvers(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_maneuvers(username)

    def strike(self, username, game_name, striker_name, striker_hexlabel,
      target_name, target_hexlabel, num_dice, strike_number):
        game = self.name_to_game(game_name)
        if game:
            game.strike(username, striker_name, striker_hexlabel,
              target_name, target_hexlabel, num_dice, strike_number)

    def done_with_strikes(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_strikes(username)

    def done_with_counterstrikes(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_counterstrikes(username)

    def acquire_angels(self, username, game_name, markerid, angel_names):
        game = self.name_to_game(game_name)
        if game:
            game.acquire_angels(username, markerid, angel_names)

    def do_not_acquire(self, username, game_name, markerid):
        log.msg("do_not_acquire", self, username, game_name, markerid)
        game = self.name_to_game(game_name)
        if game:
            game.do_not_acquire(username, markerid)

    def done_with_engagements(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_engagements(username)

    def recruit_creature(self, username, game_name, markerid, creature_name,
      recruiter_names):
        game = self.name_to_game(game_name)
        if game:
            game.recruit_creature(username, markerid, creature_name,
              recruiter_names)

    def undo_recruit(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.undo_recruit(username, markerid)

    def done_with_recruits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_recruits(username)

    def summon_angel(self, username, game_name, markerid, donor_markerid,
      creature_name):
        game = self.name_to_game(game_name)
        if game:
            game.summon_angel(username, markerid, donor_markerid,
              creature_name)

    def do_not_summon(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.do_not_summon(username, markerid)

    def do_not_reinforce(self, username, game_name, markerid):
        game = self.name_to_game(game_name)
        if game:
            game.do_not_reinforce(username, markerid)

    def carry(self, username, game_name, carry_target_name,
      carry_target_hexlabel, carries):
        log.msg("carry", carry_target_name, carry_target_hexlabel, carries)
        game = self.name_to_game(game_name)
        if game:
            game.carry(username, carry_target_name, carry_target_hexlabel,
              carries)

    def save(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.save(username)

    def withdraw(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.withdraw(username)

    def update(self, observed, action, names):
        log.msg("Server.update", observed, action, names)
        if (isinstance(action, Action.AssignTower) or
          isinstance(action, Action.AssignedAllTowers) or
          isinstance(action, Action.PickedColor) or
          isinstance(action, Action.AssignedAllColors) or
          isinstance(action, Action.CreateStartingLegion) or
          isinstance(action, Action.SplitLegion) or
          isinstance(action, Action.UndoSplit) or
          isinstance(action, Action.MergeLegions) or
          isinstance(action, Action.RollMovement) or
          isinstance(action, Action.MoveLegion) or
          isinstance(action, Action.UndoMoveLegion) or
          isinstance(action, Action.StartSplitPhase) or
          isinstance(action, Action.StartFightPhase) or
          isinstance(action, Action.StartMusterPhase) or
          isinstance(action, Action.RecruitCreature) or
          isinstance(action, Action.DoNotReinforce) or
          isinstance(action, Action.UnReinforce) or
          isinstance(action, Action.UndoRecruit) or
          isinstance(action, Action.RevealLegion) or
          isinstance(action, Action.ResolvingEngagement) or
          isinstance(action, Action.Flee) or
          isinstance(action, Action.DoNotFlee) or
          isinstance(action, Action.Concede) or
          isinstance(action, Action.Fight) or
          isinstance(action, Action.MakeProposal) or
          isinstance(action, Action.AcceptProposal) or
          isinstance(action, Action.RejectProposal) or
          isinstance(action, Action.MoveCreature) or
          isinstance(action, Action.UndoMoveCreature) or
          isinstance(action, Action.StartReinforceBattlePhase) or
          isinstance(action, Action.StartManeuverBattlePhase) or
          isinstance(action, Action.StartStrikeBattlePhase) or
          isinstance(action, Action.StartCounterstrikeBattlePhase) or
          isinstance(action, Action.DriftDamage) or
          isinstance(action, Action.Strike) or
          isinstance(action, Action.Carry) or
          isinstance(action, Action.SummonAngel) or
          isinstance(action, Action.UnSummon) or
          isinstance(action, Action.DoNotSummon) or
          isinstance(action, Action.CanAcquire) or
          isinstance(action, Action.Acquire) or
          isinstance(action, Action.DoNotAcquire) or
          isinstance(action, Action.BattleOver) or
          isinstance(action, Action.EliminatePlayer)):
            game = self.name_to_game(action.game_name)
            self.notify(action, names or game.playernames)
        else:
            self.notify(action, names)


class AIProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, server, game_name, ainame):
        self.server = server
        self.game_name = game_name
        self.ainame = ainame

    def connectionMade(self):
        log.msg("AIProcessProtocol.connectionMade", self.game_name,
          self.ainame)


def add_arguments(parser):
    parser.add_argument("-p", "--port", action="store", type=int,
      default=config.DEFAULT_PORT, help="listening TCP port")
    parser.add_argument("--passwd", "-a", action="store", type=str,
      default=prefs.passwd_path(), help="path to passwd file")
    parser.add_argument("--no-passwd", "-n", action="store_true",
      help="do not check passwords")
    parser.add_argument("--log-path", "-l", action="store", type=str,
      default=os.path.join(TEMPDIR, "slugathon-server.log"),
      help="path to logfile")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    opts, extras = parser.parse_known_args()
    port = opts.port
    server = Server(opts.no_passwd, opts.passwd, opts.port, opts.log_path)
    realm = Realm.Realm(server)
    if opts.no_passwd:
        checker = UniqueNoPassword(None, server=server)
    else:
        checker = UniqueFilePasswordDB(opts.passwd, server=server)
    portal = Portal(realm, [checker])
    pbfact = pb.PBServerFactory(portal, unsafeTracebacks=True)
    reactor.listenTCP(port, pbfact)
    log.msg("main calling reactor.run")
    reactor.run()


if __name__ == "__main__":
    main()
