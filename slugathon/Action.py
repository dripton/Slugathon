from twisted.spread import pb

class Action(pb.Copyable, pb.RemoteCopy):
    pass

pb.setUnjellyableForClass(Action, Action)


class AddUsername(Action):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return "AddUsername %s" % (self.username,)

pb.setUnjellyableForClass(AddUsername, AddUsername)


class DelUsername(Action):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return "DelUsername %s" % (self.username,)

pb.setUnjellyableForClass(DelUsername, DelUsername)


class FormGame(Action):
    def __init__(self, username, game_name, create_time, start_time,
      min_players, max_players):
        self.username = username
        self.game_name = game_name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players

    def __str__(self):
        return "FormGame %s %s %s %s %d %d" % (self.username, self.game_name,
          self.create_time, self.start_time, self.min_players, 
          self.max_players)

pb.setUnjellyableForClass(FormGame, FormGame)


class RemoveGame(Action):
    def __init__(self, game_name):
        self.game_name = game_name

    def __str__(self):
        return "RemoveGame %s" % (self.game_name,) 

pb.setUnjellyableForClass(RemoveGame, RemoveGame)


class JoinGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name

    def __str__(self):
        return "JoinGame %s %s" % (self.username, self.game_name) 

pb.setUnjellyableForClass(JoinGame, JoinGame)


class DropFromGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name

    def __str__(self):
        return "DropFromGame %s %s" % (self.username, self.game_name) 

pb.setUnjellyableForClass(DropFromGame, DropFromGame)


class AssignTower(Action):
    def __init__(self, game_name, playername, tower_num):
        self.game_name = game_name
        self.playername = playername
        self.tower_num = tower_num

    def __str__(self):
        return "AssignTower %s %s %d" % (self.game_name, self.playername, 
          self.tower_num)

pb.setUnjellyableForClass(AssignTower, AssignTower)
