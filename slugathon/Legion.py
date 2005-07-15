from bag import bag
import types

class Legion(object):
    def __init__(self, player, markername, creatures, hexlabel):
        assert type(hexlabel) == types.IntType
        self.markername = markername
        self.creatures = creatures
        self.hexlabel = hexlabel  # an int not a str
        # XXX bidirectional references are bad
        self.player = player
        self.moved = False
        self.teleported = False
        self.entry_side = None
        self.previous_hexlabel = None

    def __repr__(self):
        return "Legion %s in %s %s" % (self.markername, self.hexlabel,
          self.creatures)

    def __len__(self):
        return len(self.creatures)

    def num_lords(self):
        return sum(creature.character_type == "lord" for creature in 
          self.creatures)

    def first_lord_name(self):
        for creature in self.creatures:
            if creature.character_type == "lord":
                return creature.name
        return None

    def creature_names(self):
        return sorted(creature.name for creature in self.creatures)

    def remove_creature_by_name(self, creaturename):
        for creature in self.creatures:
            if creature.name == creaturename:
                self.creatures.remove(creature)
                return
        raise ValueError, "tried to remove missing creature"

    def can_be_split(self, turn):
        if turn == 1:
            return len(self) == 8
        else:
            return len(self) >= 4

    def is_legal_split(self, child1, child2):
        """Return whether this legion can be split into lgions child1 and
        child2"""
        if len(self) < 4:
            return False
        if len(self) != len(child1) + len(child2):
            return False
        if not bag(self.creature_names()) == bag(child1.creature_names() +
          child2.creature_names()):
            return False
        if len(self) == 8:
            if len(child1) != 4 or len(child2) != 4:
                return False
            if child1.num_lords() != 1 or child2.num_lords() != 1:
                return False
        return True

    def move(self, hexlabel, teleport, entry_side):
        self.moved = True
        self.previous_hexlabel = self.hexlabel
        self.hexlabel = hexlabel
        self.teleported = teleport
        self.entry_side = entry_side

    def undo_move(self):
        if self.moved:
            self.moved = False
            self.hexlabel = self.previous_hexlabel
            self.previous_hexlabel = None
            self.teleported = False
            self.entry_side = None
