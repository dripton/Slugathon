#!/usr/bin/env python

__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"


import time
from optparse import OptionParser

from twisted.spread import pb
from twisted.cred.portal import Portal
from twisted.internet import reactor
from zope.interface import implements

from slugathon.net import Realm, config
from slugathon.game import Game, Action
from slugathon.util.Observed import Observed
from slugathon.util.Observer import IObserver
from slugathon.net.UniqueFilePasswordDB import UniqueFilePasswordDB
from slugathon.net.UniqueNoPassword import UniqueNoPassword
from slugathon.util import prefs


class Server(Observed):
    """A Slugathon server, which can host multiple games in parallel."""

    implements(IObserver)

    def __init__(self):
        Observed.__init__(self)
        self.games = []
        self.name_to_user = {}

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

    def get_usernames(self):
        return sorted(self.name_to_user.iterkeys())

    def get_games(self):
        return self.games[:]

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
          min_players, max_players)
        self.games.append(game)
        game.add_observer(self)
        action = Action.FormGame(username, game.name, game.create_time,
          game.start_time, game.min_players, game.max_players)
        self.notify(action)

    def join_game(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            try:
                game.add_player(username)
            except AssertionError:
                pass
            else:
                action = Action.JoinGame(username, game.name)
                self.notify(action)

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
            game.start(username)

    def pick_color(self, username, game_name, color):
        game = self.name_to_game(game_name)
        if game:
            game.assign_color(username, color)

    def pick_first_marker(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.assign_first_marker(username, markername)

    def split_legion(self, username, game_name, parent_markername,
      child_markername, parent_creaturenames, child_creaturenames):
        game = self.name_to_game(game_name)
        if game:
            game.split_legion(username, parent_markername, child_markername,
              parent_creaturenames, child_creaturenames)

    def undo_split(self, username, game_name, parent_markername,
      child_markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_split(username, parent_markername, child_markername)

    def done_with_splits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_splits(username)

    def take_mulligan(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.take_mulligan(username)

    def move_legion(self, username, game_name, markername, hexlabel,
      entry_side, teleport, teleporting_lord):
        game = self.name_to_game(game_name)
        if game:
            game.move_legion(username, markername, hexlabel, entry_side,
              teleport, teleporting_lord)

    def undo_move_legion(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_move_legion(username, markername)

    def done_with_moves(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_moves(username)

    def resolve_engagement(self, username, game_name, hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.resolve_engagement(username, hexlabel)

    def flee(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.flee(username, markername)

    def do_not_flee(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.do_not_flee(username, markername)

    def concede(self, username, game_name, markername, enemy_markername,
      hexlabel):
        game = self.name_to_game(game_name)
        if game:
            game.concede(username, markername)

    def make_proposal(self, username, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.make_proposal(username, attacker_markername,
              attacker_creature_names, defender_markername,
              defender_creature_names)

    def accept_proposal(self, username, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.accept_proposal(username, attacker_markername,
              attacker_creature_names, defender_markername,
              defender_creature_names)

    def reject_proposal(self, username, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        game = self.name_to_game(game_name)
        if game:
            game.reject_proposal(username, attacker_markername,
              attacker_creature_names, defender_markername,
              defender_creature_names)

    def fight(self, username, game_name, attacker_markername,
      defender_markername):
        game = self.name_to_game(game_name)
        if game:
            game.fight(username, attacker_markername, defender_markername)

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

    def acquire_angel(self, username, game_name, markername, angel_name):
        game = self.name_to_game(game_name)
        if game:
            game.acquire_angel(username, markername, angel_name)

    def done_with_engagements(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_engagements(username)

    def recruit_creature(self, username, game_name, markername, creature_name,
      recruiter_names):
        game = self.name_to_game(game_name)
        if game:
            game.recruit_creature(username, markername, creature_name,
              recruiter_names)

    def undo_recruit(self, username, game_name, markername):
        game = self.name_to_game(game_name)
        if game:
            game.undo_recruit(username, markername)

    def done_with_recruits(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.done_with_recruits(username)

    def summon_angel(self, username, game_name, markername, donor_markername,
      creature_name):
        game = self.name_to_game(game_name)
        if game:
            game.summon_angel(username, markername, donor_markername,
              creature_name)

    def carry(self, username, game_name, carry_target_name,
      carry_target_hexlabel, carries):
        print "Server.carry", carry_target_name, carry_target_hexlabel, carries
        game = self.name_to_game(game_name)
        if game:
            game.carry(username, carry_target_name, carry_target_hexlabel,
              carries)

    def save(self, username, game_name):
        game = self.name_to_game(game_name)
        if game:
            game.save(username)


    def update(self, observed, action):
        if isinstance(action, Action.MakeProposal):
            self.notify(action, [action.other_playername])
        else:
            self.notify(action)

def main():
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type="int",
      default=config.DEFAULT_PORT, help="listening TCP port")
    op.add_option("--passwd", "-a", action="store", type="str",
      default=prefs.passwd_path(), help="path to passwd file")
    op.add_option("--no-passwd", "-n", action="store_true",
      help="do not check passwords")
    opts, args = op.parse_args()
    port = opts.port
    server = Server()
    realm = Realm.Realm(server)
    if opts.no_passwd:
        checker = UniqueNoPassword(None, server=server)
    else:
        checker = UniqueFilePasswordDB(opts.passwd, server=server)
    portal = Portal(realm, [checker])
    pbfact = pb.PBServerFactory(portal, unsafeTracebacks=True)
    reactor.listenTCP(port, pbfact)
    reactor.run()


if __name__ == "__main__":
    main()
