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
        self.server.addUser(self)
        print "User.init", self, name, server, client

    def perspective_getName(self, arg):
        print "perspective_getName(", arg, ") called on", self
        return self.name

    def perspective_getUserNames(self):
        print "perspective_getUserNames called on", self
        return self.server.getUserNames()

    def perspective_getGames(self):
        print "perspective_getGames called on", self
        return self.server.getGames()

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

    def notifyFormedGame(self, gamedict):
        print "notifyFormedGame", gamedict
        def1 = self.client.callRemote("notifyFormedGame", gamedict)
        def1.addErrback(self.failure)

    def __str__(self):
        return "User " + self.name

    def attached(self, mind):
        print "called User.attached", mind
        def1 = self.client.callRemote("setName", self.name)
        def1.addCallbacks(self.didSetName, self.failure)
        def2 = self.client.callRemote("ping", time.time())
        def2.addCallbacks(self.didPing, self.failure)

    def didSetName(self, arg):
        print "User.didSetName", arg

    def success(self, arg):
        pass

    def failure(self, arg):
        print "User.failure", arg

    def didPing(self, arg):
        print "User.didPing", arg

    def logout(self):
        print "called logout"
        self.server.delUser(self)

    def notifyAddUsername(self, username):
        def1 = self.client.callRemote("notifyAddUsername", username)
        def1.addErrback(self.failure)

    def notifyDelUsername(self, username):
        def1 = self.client.callRemote("notifyDelUsername", username)
        def1.addErrback(self.failure)
