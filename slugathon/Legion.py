class Legion(object):
    def __init__(self, player, markername, creatures, hexlabel):
        self.markername = markername
        self.creatures = creatures
        self.hexlabel = hexlabel
        # XXX bidirectional references are bad
        self.player = player

    def height(self):
        return len(self.creatures)

    def __len__(self):
        return len(self.creatures)
