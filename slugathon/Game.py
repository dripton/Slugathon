import sys
import time

from twisted.spread import pb
import zope.interface

import Player
import MasterBoard
import rules
from playercolordata import colors
from Observed import Observed
from Observer import IObserver
import Action
import Phase


class Game(Observed):
    """Central class holding information about one game."""

    zope.interface.implements(IObserver)

    def __init__(self, name, owner, create_time, start_time, min_players,
      max_players):
        Observed.__init__(self) 
        self.name = name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
        self.started = False
        self.players = []
        self.num_players_joined = 0
        self.add_player(owner)
        self.board = MasterBoard.MasterBoard()
        self.turn = 1
        self.phase = Phase.SPLIT
        self.active_player = None

    def __eq__(self, other):
        return isinstance(other, Game) and self.name == other.name

    def get_owner(self):
        """The owner of the game is the remaining player who joined first."""
        min_join_order = sys.maxint
        owner = None
        for player in self.players:
            if player.join_order < min_join_order:
                owner = player
                min_join_order = player.join_order
        assert owner is not None
        return owner

    def get_playernames(self):
        return [player.name for player in self.players]

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        raise KeyError("No player named %s in players %s" % (
          name, self.players))

    def to_gui_tuple(self):
        """Return state as a tuple of strings for GUI presentation."""
        return (self.name, self.get_owner().name, time.ctime(self.create_time),
          time.ctime(self.start_time), self.min_players, self.max_players,
          ", ".join(self.get_playernames()))

    def to_info_tuple(self):
        """Return state as a tuple of strings for passing to client."""
        return (self.name, self.create_time, self.start_time, 
          self.min_players, self.max_players, self.get_playernames()[:])

    def add_player(self, playername):
        """Add a player to this game."""
        assert not self.started, "add_player on started game"
        assert playername not in self.get_playernames(), \
          "add_player from %s already in game %s" % (playername, self.name)
        assert len(self.players) < self.max_players, \
          "%s tried to join full game %s" % (playername, self.name)
        print "adding", playername, "to", self.name
        self.num_players_joined += 1
        player = Player.Player(playername, self.name, self.num_players_joined)
        self.players.append(player)
        player.add_observer(self)

    def remove_player(self, playername):
        assert not self.started, "remove_player on started game"
        player = self.get_player_by_name(playername)
        player.remove_observer(self)
        self.players.remove(player)

    def start(self, playername):
        """Called only on server side, and only by game owner."""
        assert playername == self.get_owner().name, \
          "Game.start called for %s by non-owner %s" % (self.name, playername)
        self.started = True
        towers = rules.assign_towers(self.board.get_tower_labels(), 
          len(self.players))
        assert len(towers) == len(self.players)
        for num, player in enumerate(self.players):
            player.assign_starting_tower(towers[num])
        self.sort_players()
        action = Action.AssignedAllTowers(self.name)
        self.notify(action)

    def sort_players(self):
        """Sort players into descending order of tower number.
        
        Only call this after towers are assigned.
        """
        def starting_tower_desc(a, b):
            return b.starting_tower - a.starting_tower
        self.players.sort(starting_tower_desc)
        self.active_player = players[0]

    def done_assigning_towers(self):
        for player in self.players:
            if player.starting_tower is None:
                return False
        return True

    def next_playername_to_pick_color(self):
        if not self.done_assigning_towers():
            return None
        rev_players = self.players[:]
        rev_players.reverse()
        for player in rev_players:
            if player.color is None:
                return player.name
        return None

    def colors_left(self):
        left = colors[:]
        for player in self.players:
            if player.color:
                left.remove(player.color)
        return left

    def assign_color(self, playername, color):
        player = self.get_player_by_name(playername)
        # Just abort if we've already done this.  Simplifies timing.
        if player.color == color:
            return
        left = self.colors_left()
        assert color in left
        for p in self.players:
            if p is not player:
                assert p.color != color
        player = self.get_player_by_name(playername)
        player.assign_color(color)

    def done_assigning_first_markers(self):
        for player in self.players:
            if player.selected_markername is None:
                return False
        return True

    def assign_first_marker(self, playername, markername):
        player = self.get_player_by_name(playername)
        assert markername in player.markernames
        player.pick_marker(markername)
        if self.done_assigning_first_markers():
            self.init_starting_legions()

    def init_starting_legions(self):
        for player in self.players:
            player.init_starting_legion()

    def create_starting_legion(self, playername, markername):
        player = self.get_player_by_name(playername)
        player.create_starting_legion(markername)

    def gen_all_legions(self):
        for player in self.players:
            for legion in player.legions.itervalues():
                yield legion

    def update(self, observed, action):
        print "Game.update", observed, action

        if isinstance(action, Action.JoinGame):
            if action.game_name == self.name:
                self.add_player(action.username)
        elif isinstance(action, Action.DropFromGame):
            if action.game_name == self.name:
                self.remove_player(action.username)
        elif isinstance(action, Action.AssignTower):
            self.started = True
            player = self.get_player_by_name(action.playername)
            if player.starting_tower is None:
                player.assign_starting_tower(action.tower_num)
        elif isinstance(action, Action.AssignedAllTowers):
            self.sort_players()
        elif isinstance(action, Action.PickedColor):
            self.assign_color(action.playername, action.color)
        elif isinstance(action, Action.CreateStartingLegion):
            self.create_starting_legion(action.playername, action.markername)

        self.notify(action)
