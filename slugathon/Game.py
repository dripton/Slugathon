import time
from twisted.spread import pb
import Player
import MasterBoard
import rules

class Game:
    """Central class holding information about one game."""
    def __init__(self, name, owner, create_time, start_time, min_players,
      max_players):
        self.name = name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
        self.started = False
        self.players = []
        self.add_player(owner)
        self.board = MasterBoard.MasterBoard()

    def __eq__(self, other):
        return isinstance(other, Game) and self.name == other.name

    def get_owner(self):
        return self.players[0].name

    def get_playernames(self):
        return [player.name for player in self.players]

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def to_tuple(self):
        """Return state as a tuple of strings for GUI presentation."""
        return (self.name, self.get_owner(), time.ctime(self.create_time),
          time.ctime(self.start_time), self.min_players, self.max_players,
          ', '.join(self.get_playernames()))

    def remove_player(self, playername):
        assert not self.started, 'remove_player on started game'
        player = self.get_player_by_name(playername)
        assert player, \
          '%s tried to drop from %s but not in game' % (playername, self.name)
        self.players.remove(player)

    def add_player(self, playername):
        """Add a player to this game."""
        assert not self.started, 'add_player on started game'
        assert playername not in self.get_playernames(), \
          'add_player from %s already in game %s' % (playername, self.name)
        assert len(self.players) < self.max_players, \
          '%s tried to join full game %s' % (playername, self.name)
        print 'adding', playername, 'to', self.name
        player = Player.Player(playername)
        self.players.append(player)
        player.add_observer(self)

    def start(self, playername):
        assert playername == self.get_owner(), \
          'start_game called for %s by non-owner %s' % (self.name, playername)
        self.started = True
        towers = rules.assign_towers(self.board.get_tower_labels(), 
          len(self.players))
        for num, player in enumerate(self.players):
            player.assign_starting_tower(towers[num])

    def update(self, observed, *args):
        # TODO
        pass
