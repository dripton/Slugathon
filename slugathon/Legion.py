class Legion(object):
    def __init__(self, marker, creatures, hex):
        self.marker = marker
        self.creatures = creatures
        self.hex = hex

    def height(self):
        return len(self.creatures)

    def __len__(self):
        return len(self.creatures)
