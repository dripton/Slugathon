from twisted.spread import pb

class Action(pb.Copyable, pb.RemoteCopy):

    def __repr__(self):
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


class CreateStartingLegion(Action):
    def __init__(self, game_name, playername, markername):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
pb.setUnjellyableForClass(CreateStartingLegion, CreateStartingLegion)


class SplitLegion(Action):
    def __init__(self, game_name, playername, parent_markername, 
      child_markername, parent_creaturenames, child_creaturenames):
        """parent_creaturenames and child_creaturenames are lists of the actual
        creature names if known, or lists of height * None if not known
        """
        self.game_name = game_name
        self.playername = playername
        self.parent_markername = parent_markername
        self.child_markername = child_markername
        self.parent_creaturenames = parent_creaturenames
        self.child_creaturenames = child_creaturenames
pb.setUnjellyableForClass(SplitLegion, SplitLegion)

class RollMovement(Action):
    def __init__(self, game_name, playername, movement_roll):
        """parent_creaturenames and child_creaturenames are lists of the actual
        creature names if known, or lists of height * None if not known
        """
        self.game_name = game_name
        self.playername = playername
        self.movement_roll = movement_roll
pb.setUnjellyableForClass(RollMovement, RollMovement)

class MoveLegion(Action):
    def __init__(self, game_name, playername, markername, hexlabel, teleport,
      entry_side):
        self.game_name = game_name
        self.playername = playername
        self.markername = markername
        self.hexlabel = hexlabel
        self.teleport = teleport
        self.entry_side = entry_side
pb.setUnjellyableForClass(MoveLegion, MoveLegion)
