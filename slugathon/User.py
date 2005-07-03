from twisted.spread import pb
import time
import zope.interface

from Observer import IObserver

class User(pb.Avatar):
    """Perspective for a player or spectator."""

    zope.interface.implements(IObserver)

    def __init__(self, name, server, client):
        self.name = name
        self.server = server
        self.client = client
        self.server.add_observer(self)
        print "called User.__init__", self, name, server, client

    def attached(self, mind):
        print "User attached", mind

    def detached(self, mind):
        print "User detached", mind

    def perspective_get_name(self, arg):
        print "perspective_get_name(", arg, ") called on", self
        return self.name

    def perspective_get_usernames(self):
        print "perspective_get_usernames called on", self
        return self.server.get_usernames()

    def perspective_get_games(self):
        print "perspective_get_games called on", self
        games = self.server.get_games()
        return [game.to_info_tuple() for game in games]

    def perspective_send_chat_message(self, text):
        print "perspective_send_chat_message", text
        self.server.send_chat_message(self.name, None, text)

    def receive_chat_message(self, text):
        print "User.receive_chat_message", text
        def1 = self.client.callRemote("receive_chat_message", text)
        def1.addErrback(self.failure)

    def perspective_form_game(self, game_name, min_players, max_players):
        print "perspective_form_game", game_name, min_players, max_players
        self.server.form_game(self.name, game_name, min_players, max_players)

    def perspective_join_game(self, game_name):
        print "perspective_join_game", game_name
        self.server.join_game(self.name, game_name)

    def perspective_drop_from_game(self, game_name):
        print "perspective_drop_from_game", game_name
        self.server.drop_from_game(self.name, game_name)

    def perspective_start_game(self, game_name):
        print "perspective_start_game", game_name
        self.server.start_game(self.name, game_name)

    def perspective_pick_color(self, game_name, color):
        print "perspective_pick_color", game_name, color
        self.server.pick_color(self.name, game_name, color)

    def perspective_pick_first_marker(self, game_name, markername):
        print "perspective_pick_first_marker", game_name, markername
        self.server.pick_first_marker(self.name, game_name, markername)

    def perspective_split_legion(self, game_name, parent_markername, 
      child_markername, parent_creaturenames, child_creaturenames):
        print "perspective_pick_first_marker", game_name, parent_markername,\
          child_markername, parent_creaturenames, child_creaturenames
        self.server.split_legion(self.name, game_name, parent_markername,
          child_markername, parent_creaturenames, child_creaturenames)

    def __str__(self):
        return "User " + self.name

    def add_observer(self, mind):
        print "called User.add_observer", mind
        def1 = self.client.callRemote("set_name", self.name)
        def1.addCallbacks(self.did_set_name, self.failure)
        def2 = self.client.callRemote("ping", time.time())
        def2.addCallbacks(self.did_ping, self.failure)

    def did_set_name(self, arg):
        print "User.did_set_name", arg

    def success(self, arg):
        pass

    def failure(self, arg):
        print "User.failure", arg

    def did_ping(self, arg):
        print "User.did_ping", arg

    def logout(self):
        print "called logout"
        self.server.remove_observer(self)

    def update(self, observed, action):
        """Defers updates to its client, dropping the observed reference."""
        print "User.update", self, observed, action
        def1 = self.client.callRemote("update", action)
        def1.addErrback(self.failure)
