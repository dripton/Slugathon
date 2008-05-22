from Observed import Observed

class Battle(Observed):
    def __init__(self, game, attacker_legion, defender_legion):
        Observed.__init__(self)
        self.game = game
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        assert defender_legion.hexlabel == attacker_legion.hexlabel
        self.hexlabel = attacker_legion.hexlabel
        self.masterhex = self.game.board.hexes[self.hexlabel]
        self.entry_side = attacker_legion.entry_side

    def add_observer(self, observer, name=""):
        if observer not in self.observers:
            self.observers[observer] = name

    def remove_observer(self, observer):
        if observer in self.observers:
            del self.observers[observer]

    def notify(self, action, names=None):
        # Create the list so it can't change size while iterating
        for observer, name in self.observers.items():
            if names is None or name in names:
                observer.update(self, action)
