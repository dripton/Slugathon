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
from slugathon.game import Action, Game


class Client(pb.Referenceable, Observed):

    implements(IObserver)

    def __init__(self, username, password, host="localhost",
      port=config.DEFAULT_PORT):
        Observed.__init__(self)
        self.username = username
        self.playername = username # In case the same user logs in twice
        self.password = password
        self.host = host
        self.port = port
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

    def split(self, unused, game):
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
            entry_side = random.choice([1, 3, 5])
            teleporting_lord = sorted(legion.lord_types)[-1]
        else:
            teleport = False
            teleporting_lord = None
        def1 = self.user.callRemote("move_legion", game.name,
          legion.markername, hexlabel, entry_side, teleport, teleporting_lord)
        def1.addErrback(self.failure)

    def choose_engagement(self, game):
        """Resolve engagements.

        For now only know how to flee or concede.
        """
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

    def resolve_engagement(self, game, hexlabel):
        """Resolve the engagement in hexlabel.

        For now only know how to flee or concede.
        """
        for legion in game.all_legions(hexlabel):
            if legion.player == game.active_player:
                attacker = legion
            else:
                defender = legion
        if defender.player.name == self.playername:
            if defender.can_flee:
                def1 = self.user.callRemote("flee", game.name,
                  defender.markername)
                def1.addErrback(self.failure)
            else:
                def1 = self.user.callRemote("concede", game.name,
                  defender.markername, attacker.markername, hexlabel)
                def1.addErrback(self.failure)
        else:
            def1 = self.user.callRemote("concede", game.name,
              attacker.markername, defender.markername, hexlabel)
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


    def update(self, observed, action):
        """Updates from User will come via remote_update, with
        observed set to None."""
        print "update", action

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
            self.maybe_pick_color(game)
        elif isinstance(action, Action.PickedColor):
            game = self.name_to_game(action.game_name)
            # Do this now rather than waiting for game to be notified.
            game.assign_color(action.playername, action.color)
            self.maybe_pick_color(game)
            self.maybe_pick_first_marker(game, action.playername)
        elif isinstance(action, Action.AssignedAllColors):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                self.split(None, game)
        elif isinstance(action, Action.GameOver):
            if action.winner_names:
                print "Game %s over, won by %s" % (action.game_name,
                  " and ".join(action.winner_names))
            else:
                print "Game %s over, draw" % action.game_name
        elif isinstance(action, Action.DoneRecruiting):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                self.split(None, game)
        elif isinstance(action, Action.CreateStartingLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                self.split(None, game)
        elif isinstance(action, Action.SplitLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                self.split(None, game)
        elif isinstance(action, Action.RollMovement):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                self.move_legions(game)
        elif isinstance(action, Action.MoveLegion):
            game = self.name_to_game(action.game_name)
            if action.playername == self.playername:
                self.move_legions(game)
        elif isinstance(action, Action.DoneMoving):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                if game.engagement_hexlabels:
                    self.choose_engagement(game)
                else:
                    self.recruit(game)
        elif isinstance(action, Action.ResolvingEngagement):
            game = self.name_to_game(action.game_name)
            self.resolve_engagement(game, action.hexlabel)
        elif isinstance(action, Action.Flee):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                if game.engagement_hexlabels:
                    self.choose_engagement(game)
                else:
                    def1 = self.user.callRemote("done_with_engagements",
                      game.name)
                    def1.addErrback(self.failure)
        elif isinstance(action, Action.Concede):
            game = self.name_to_game(action.game_name)
            if game.active_player.name == self.playername:
                if game.engagement_hexlabels:
                    self.choose_engagement(game)
                else:
                    def1 = self.user.callRemote("done_with_engagements",
                      game.name)
                    def1.addErrback(self.failure)
        elif isinstance(action, Action.DoneFighting):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                self.recruit(game)
        elif isinstance(action, Action.RecruitCreature):
            if action.playername == self.playername:
                game = self.name_to_game(action.game_name)
                self.recruit(game)
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
    opts, args = op.parse_args()
    if args:
        op.error("got illegal argument")
    client = Client(opts.playername, opts.password, opts.server, opts.port)
    client.connect()
    reactor.run()

if __name__ == "__main__":
    main()
