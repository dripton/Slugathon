import sys
import time

from twisted.spread import pb
import zope.interface

import Player
import MasterBoard
from playercolordata import colors
from Observed import Observed
from Observer import IObserver
import Action
import Phase
import Dice


# Movement constants
ARCHES_AND_ARROWS = -1
ARROWS_ONLY = -2

# Entry side
ANY = 1 + 3 + 5

def opposite(direction):
    return (direction + 3) % 6


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
        if owner is None:
            raise AssertionError, "Game has no owner"
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
        if self.started:
            raise AssertionError, "add_player on started game"
        if playername in self.get_playernames():
            raise AssertionError, "add_player from %s already in game %s" % (
              playername, self.name)
        if len(self.players) >= self.max_players:
            raise AssertionError, "%s tried to join full game %s" % (
              playername, self.name)
        print "adding", playername, "to", self.name
        self.num_players_joined += 1
        player = Player.Player(playername, self.name, self.num_players_joined)
        self.players.append(player)
        player.add_observer(self)

    def remove_player(self, playername):
        if self.started:
            raise AssertionError, "remove_player on started game"
        player = self.get_player_by_name(playername)
        player.remove_observer(self)
        self.players.remove(player)

    def assign_towers(self):
        towers = self.board.get_tower_labels()
        Dice.shuffle(towers)
        for num, player in enumerate(self.players):
            player.assign_starting_tower(towers[num])

    def start(self, playername):
        """Called only on server side, and only by game owner."""
        if playername != self.get_owner().name:
            raise AssertionError, "Game.start %s called by non-owner %s" % (
              self.name, playername)
        self.started = True
        self.assign_towers()
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
        self.active_player = self.players[0]

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
        if color not in left:
            raise AssertionError, "tried to take unavailable color"
        player.assign_color(color)

    def done_assigning_first_markers(self):
        for player in self.players:
            if player.selected_markername is None:
                return False
        return True

    def assign_first_marker(self, playername, markername):
        player = self.get_player_by_name(playername)
        if markername not in player.markernames:
            raise AssertionError, "marker not available"
        player.pick_marker(markername)
        if self.done_assigning_first_markers():
            self.create_starting_legions()

    def create_starting_legions(self):
        for player in self.players:
            player.create_starting_legion()

    def gen_all_legions(self):
        for player in self.players:
            for legion in player.legions.itervalues():
                yield legion

    def split_legion(self, playername, parent_markername, child_markername,
      parent_creaturenames, child_creaturenames):
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("splitting out of turn")
        player.split_legion(parent_markername, child_markername, 
          parent_creaturenames, child_creaturenames)

    def done_with_splits(self, playername):
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending split phase out of turn")
        if self.phase == Phase.SPLIT:
            player.done_with_splits()

    def can_take_mulligan(self, player):
        return bool(player is self.active_player and self.turn == 1 
          and self.phase == Phase.MOVE and player.mulligans_left)

    def take_mulligan(self, playername):
        player = self.get_player_by_name(playername)
        if not self.can_take_mulligan(player):
            raise AssertionError("illegal mulligan attempt")
        player.take_mulligan()

    def all_legions(self, hexlabel):
        """Return a list of all legions in the hex with hexlabel"""
        return [legion for legion in self.gen_all_legions() if 
          legion.hexlabel == hexlabel]

    def friendly_legions(self, hexlabel, player):
        """Return a list of player's legions in the hex with hexlabel"""
        return [legion for legion in player.legions.values() if legion.hexlabel
          == hexlabel]

    def enemy_legions(self, hexlabel, player):
        """Return a list of legions belonging to other than player in the 
        hex with hexlabel"""
        return [legion for legion in self.gen_all_legions() if legion.player 
          is not player and legion.hexlabel == hexlabel]

    def find_normal_moves(self, legion, masterhex, roll, block, came_from):
        """Recursively find non-teleport moves for legion from masterhex.

        If block >= 0, go only that way.  
        If block == ARCHES_AND_ARROWS, use arches and arrows.  
        If block == ARROWS_ONLY, use only arrows.  
        Return a set of (hexlabel, entry_side) tuples.
        """
        if block is None:
            block = ARCHES_AND_ARROWS
        moves = set()
        hexlabel = masterhex.label
        player = legion.player
        # If there is an enemy legion and no friendly legion, mark the hex
        # as a legal move, and stop.
        if self.enemy_legions(hexlabel, player): 
            if not self.friendly_legions(hexlabel, player):
                moves.add((hexlabel, masterhex.find_entry_side(came_from)))
        elif roll == 0:
            # Final destination
            # Do not add this hex if already occupied by another friendly
            # legion.
            allies = set(self.friendly_legions(hexlabel, player))
            allies.discard(legion)
            if not allies:
                moves.add((hexlabel, masterhex.find_entry_side(came_from)))
        elif block >= 0:
            print "block", block
            moves.update(self.find_normal_moves(legion, 
              masterhex.neighbors[block], roll - 1, ARROWS_ONLY, 
              opposite(block)))
        elif block == ARCHES_AND_ARROWS:
            for direction, gate in enumerate(masterhex.exits):
                if gate in ("ARCH", "ARROW", "ARROWS") and (direction != 
                  came_from):
                    moves.update(self.find_normal_moves(legion, 
                      masterhex.neighbors[direction], roll - 1, ARROWS_ONLY, 
                      opposite(direction)))
        elif block == ARROWS_ONLY:
            for direction, gate in enumerate(masterhex.exits):
                if gate in ("ARROW", "ARROWS") and (direction != came_from):
                    moves.update(self.find_normal_moves(legion,
                      masterhex.neighbors[direction], roll - 1, ARROWS_ONLY,
                      opposite(direction)))
        return moves

    def find_nearby_empty_hexes(self, legion, masterhex, roll, came_from):
        """Recursively find empty hexes within roll hexes, for tower 
        teleport"""
        hexlabel = masterhex.label
        moves = set()
        if not self.all_legions(hexlabel):
            moves.add((hexlabel, ANY))
        if roll > 0:
            for direction, gate in enumerate(masterhex.exits):
                if direction != came_from: 
                    neighbor = masterhex.neighbors[direction]
                    if neighbor and (gate != "NONE" or 
                      neighbor.exits[opposite(direction)] != "NONE"):
                        moves.update(self.find_nearby_empty_hexes(legion,
                          neighbor, roll - 1, opposite(direction)))
        return moves

    def find_tower_teleport_moves(self, legion, masterhex):
        """Return set of hexlabels describing where legion can tower 
        teleport."""
        moves = set()
        if masterhex.is_tower() and legion.num_lords():
            moves.update(self.find_nearby_empty_hexes(legion, masterhex, 6,
              None))
        for hexlabel in self.board.get_tower_labels():
            if hexlabel != masterhex.label and not self.all_legions(hexlabel):
                moves.add((hexlabel, ANY))
        return moves

    def find_titan_teleport_moves(self, legion):
        """Return set of hexlabels describing where legion can titan 
        teleport."""
        player = legion.player
        moves = set()
        if player.can_titan_teleport() and "Titan" in legion.creature_names():
            for legion in self.gen_all_legions():
                hexlabel = legion.hexlabel
                if not self.friendly_legions(hexlabel, player):
                    moves.add((hexlabel, ANY))
        return moves

    def find_all_teleport_moves(self, legion, masterhex, roll):
        """Return set of hexlabels describing where legion can teleport."""
        player = legion.player
        moves = set()
        if roll != 6 or legion.moved or player.teleported:
            return moves
        moves.update(self.find_tower_teleport_moves(legion, masterhex))
        moves.update(self.find_titan_teleport_moves(legion))
        return moves

    def find_all_moves(self, legion, masterhex, roll):
        """Return set of hexlabels describing where legion can move."""
        moves = self.find_normal_moves(legion, masterhex, roll, 
          masterhex.find_block(), None)
        moves.update(self.find_all_teleport_moves(legion, masterhex, roll))
        return moves


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
            player = self.get_player_by_name(action.playername)
            # Avoid doing twice
            if not player.legions:
                player.pick_marker(action.markername)
                player.create_starting_legion()
        elif isinstance(action, Action.SplitLegion):
            player = self.get_player_by_name(action.playername)
            # Avoid doing the same split twice.
            if not action.child_markername in player.legions:
                self.split_legion(action.playername, action.parent_markername,
                action.child_markername, action.parent_creaturenames, 
                 action.child_creaturenames)
        elif isinstance(action, Action.RollMovement):
            player = self.get_player_by_name(action.playername)
            self.phase = Phase.MOVE
            # Possibly redundant, but harmless
            player.movement_roll = action.movement_roll

        self.notify(action)
