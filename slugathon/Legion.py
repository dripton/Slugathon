class Legion(object):
    def __init__(self, markername, creatures, hexlabel):
        self.markername = markername
        self.creatures = creatures
        self.hexlabel = hexlabel

    def height(self):
        return len(self.creatures)

    def __len__(self):
        return len(self.creatures)
