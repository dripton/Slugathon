from twisted.spread import pb

class Action(pb.Copyable, pb.RemoteCopy):

    def __str__(self):
        return "%s %s" % (self.__class__.__name__, self.__dict__)
pb.setUnjellyableForClass(Action, Action)


class AddUsername(Action):
    def __init__(self, username):
        self.username = username
pb.setUnjellyableForClass(AddUsername, AddUsername)


class DelUsername(Action):
    def __init__(self, username):
        self.username = username
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
pb.setUnjellyableForClass(FormGame, FormGame)


class RemoveGame(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(RemoveGame, RemoveGame)


class JoinGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name
pb.setUnjellyableForClass(JoinGame, JoinGame)


class DropFromGame(Action):
    def __init__(self, username, game_name):
        self.username = username
        self.game_name = game_name
pb.setUnjellyableForClass(DropFromGame, DropFromGame)


class AssignTower(Action):
    def __init__(self, game_name, playername, tower_num):
        self.game_name = game_name
        self.playername = playername
        self.tower_num = tower_num
pb.setUnjellyableForClass(AssignTower, AssignTower)


class AssignedAllTowers(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(AssignedAllTowers, AssignedAllTowers)


class PickedColor(Action):
    def __init__(self, game_name, playername, color):
        self.game_name = game_name
        self.playername = playername
        self.color = color
pb.setUnjellyableForClass(PickedColor, PickedColor)

class AssignedAllColors(Action):
    def __init__(self, game_name):
        self.game_name = game_name
pb.setUnjellyableForClass(AssignedAllColors, AssignedAllColors)

