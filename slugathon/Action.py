from twisted.spread import pb

class Action(pb.Copyable, pb.RemoteCopy):
    pass

pb.setUnjellyableForClass(Action, Action)


class AssignTower(Action):
    def __init__(self, playername, tower_num):
        self.playername = playername
        self.tower_num = tower_num

    def __str__(self):
        return "AssignTower %s %d" % (playername, tower_num)

pb.setUnjellyableForClass(AssignTower, AssignTower)
