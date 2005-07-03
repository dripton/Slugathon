class Legion(object):
    def __init__(self, player, markername, creatures, hexlabel):
        self.markername = markername
        self.creatures = creatures
        self.hexlabel = hexlabel
        # XXX bidirectional references are bad
        self.player = player

    def __str__(self):
        return "Legion %s in %s %s" % (self.markername, self.hexlabel,
          self.creatures)

    def __len__(self):
        return len(self.creatures)

    def num_lords(self):
        return sum(cr.character_type == "lord" for cr in self.creatures)

    def creature_names(self):
        li = [creature.name for creature in self.creatures]
        li.sort()
        return li

    def remove_creature_by_name(self, creaturename):
        for creature in self.creatures:
            if creature.name == creaturename:
                self.creatures.remove(creature)
                return
        raise ValueError, "tried to remove missing creature"
