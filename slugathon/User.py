from twisted.spread import pb
import time
from twisted.cred import portal

class User(pb.Avatar):
    """Perspective for a player or observer."""

    def __init__(self, name, server, client):
        self.name = name
        self.server = server
        self.client = client
        # XXX Bidirectional references
        self.server.add_user(self)
        print "User.init", self, name, server, client

    def perspective_getName(self, arg):
        print "perspective_getName(", arg, ") called on", self
        return self.name

    def perspective_get_user_names(self):
        print "perspective_get_user_names called on", self
        return self.server.get_user_names()

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

    def notify_formed_game(self, game):
        print "notify_formed_game", game
        def1 = self.client.callRemote("notify_formed_game", 
          game.to_info_tuple())
        def1.addErrback(self.failure)

    def notify_removed_game(self, game):
        print "notify_removed_game", game
        def1 = self.client.callRemote("notify_removed_game", game.name)
        def1.addErrback(self.failure)

    def notify_dropped_from_game(self, playername, game):
        print "notify_dropped_from_game", playername, game
        def1 = self.client.callRemote("notify_dropped_from_game", playername,
          game.name)
        def1.addErrback(self.failure)

    def notify_joined_game(self, playername, game):
        print "notify_joined_game", playername, game
        def1 = self.client.callRemote("notify_joined_game", playername,
          game.name)
        def1.addErrback(self.failure)

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

    def __str__(self):
        return "User " + self.name

    def attached(self, mind):
        print "called User.attached", mind
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
        self.server.del_user(self)

    def notify_add_username(self, username):
        def1 = self.client.callRemote("notify_add_username", username)
        def1.addErrback(self.failure)

    def notify_del_username(self, username):
        def1 = self.client.callRemote("notify_del_username", username)
        def1.addErrback(self.failure)
