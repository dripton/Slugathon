__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


from sys import maxint
import os
import time

from zope.interface import implements

import Player
import MasterBoard
from playercolordata import colors
from Observed import Observed
from Observer import IObserver
import Action
import Phase
import Dice
import Caretaker
import Creature
import History
from bag import bag
import BattleMap
import prefs


# Movement constants
ARCHES_AND_ARROWS = -1
ARROWS_ONLY = -2

# Entry side constants
TELEPORT = "TELEPORT"

def opposite(direction):
    return (direction + 3) % 6


class Game(Observed):
    """Central class holding information about one game"""

    implements(IObserver)

    def __init__(self, name, owner, create_time, start_time, min_players,
      max_players):
        Observed.__init__(self)
        self.name = name
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players
        self.started = False
        self.over = False
        self.players = []
        self.players_left = []  # Used to track co-winners in a draw
        self.num_players_joined = 0
        self.add_player(owner)
        self.board = MasterBoard.MasterBoard()
        self.turn = 1
        self.phase = Phase.SPLIT
        self.active_player = None
        self.caretaker = Caretaker.Caretaker()
        self.history = History.History()
        self.add_observer(self.history)
        self.current_engagement_hexlabel = None
        self.attacker_legion = None
        self.defender_legion = None
        self.battle_masterhex = None
        self.battle_entry_side = None
        self.battlemap = None
        self.battle_turn = None
        self.battle_phase = None
        self.battle_active_legion = None


    @property
    def battle_legions(self):
        """Return a list of the legions involved in battle, or []."""
        if self.defender_legion is not None:
            return [self.defender_legion, self.attacker_legion]
        else:
            return []

    @property
    def battle_active_player(self):
        """Return the active player in the current battle, or None."""
        try:
            return self.battle_active_legion.player
        except AttributeError:
            return None

    def _init_battle(self, attacker_legion, defender_legion):
        self.attacker_legion = attacker_legion
        self.defender_legion = defender_legion
        assert defender_legion.hexlabel == attacker_legion.hexlabel
        self.battle_masterhex = self.board.hexes[attacker_legion.hexlabel]
        self.battle_entry_side = attacker_legion.entry_side
        self.battlemap = BattleMap.BattleMap(self.battle_masterhex.terrain,
          self.battle_entry_side)
        self.battle_turn = 1
        self.battle_phase = Phase.MANEUVER
        self.battle_active_legion = self.defender_legion
        self.defender_legion.enter_battle("DEFENDER")
        self.attacker_legion.enter_battle("ATTACKER")

    def _cleanup_battle(self):
        self.attacker_legion = None
        self.defender_legion = None
        self.battle_masterhex = None
        self.battle_entry_side = None
        self.battlemap = None
        self.battle_turn = None
        self.battle_phase = None
        self.battle_active_legion = None

    def __eq__(self, other):
        return isinstance(other, Game) and self.name == other.name

    def __repr__(self):
        return "Game %s" % self.name

    def get_owner(self):
        """The owner of the game is the remaining player who joined first."""
        min_join_order = maxint
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
        self.num_players_joined += 1
        player = Player.Player(playername, self, self.num_players_joined)
        self.players.append(player)
        player.add_observer(self)

    def remove_player(self, playername):
        """Remove a player from this game.

        Not allowed after the game has started.
        """
        if self.started:
            raise AssertionError, "remove_player on started game"
        try:
            player = self.get_player_by_name(playername)
        except KeyError:
            # already removed, okay
            pass
        else:
            player.remove_observer(self)
            self.players.remove(player)

    @property
    def living_players(self):
        """Return a list of Players still in the game."""
        return [player for player in self.players if not player.dead]

    def assign_towers(self):
        """Randomly assign a tower to each player."""
        towers = self.board.get_tower_labels()
        Dice.shuffle(towers)
        for num, player in enumerate(self.players):
            player.assign_starting_tower(towers[num])

    def start(self, playername):
        """Begin the game.

        Called only on server side, and only by game owner."""
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
        """Return True iff we're done assigning towers to all players."""
        for player in self.players:
            if player.starting_tower is None:
                return False
        return True

    def next_playername_to_pick_color(self):
        """Return the name of the player whose turn it is to pick a color."""
        if not self.done_assigning_towers():
            return None
        leader = None
        for player in self.players:
            if player.color is None and (leader is None or
              player.starting_tower < leader.starting_tower):
                leader = player
        if leader is not None:
            return leader.name
        else:
            return None

    def colors_left(self):
        """Return a list of player colors that aren't taken yet."""
        left = colors[:]
        for player in self.players:
            if player.color:
                left.remove(player.color)
        return left

    def assign_color(self, playername, color):
        """Assign color to playername."""
        player = self.get_player_by_name(playername)
        # Just abort if we've already done this.  Simplifies timing.
        if player.color == color:
            return
        left = self.colors_left()
        if color not in left:
            raise AssertionError, "tried to take unavailable color"
        player.assign_color(color)

    def done_assigning_first_markers(self):
        """Return True iff each player has picked his first marker."""
        for player in self.players:
            if player.selected_markername is None:
                return False
        return True

    def assign_first_marker(self, playername, markername):
        """Use markername for playername's first legion marker.

        Once all players have done this, create the starting legions.
        """
        player = self.get_player_by_name(playername)
        if markername not in player.markernames:
            raise AssertionError, "marker not available"
        player.pick_marker(markername)
        if self.done_assigning_first_markers():
            for player in self.players:
                player.create_starting_legion()

    def all_legions(self, hexlabel=None):
        """Return a set of all legions in hexlabel, or in the whole
        game if hexlabel is None"""
        legions = set()
        for player in self.players:
            for legion in player.legions.itervalues():
                if hexlabel in (None, legion.hexlabel):
                    legions.add(legion)
        return legions

    def find_legion(self, markername):
        """Return the legion called markername, or None."""
        for player in self.players:
            if markername in player.legions:
                return player.legions[markername]
        return None

    def split_legion(self, playername, parent_markername, child_markername,
      parent_creature_names, child_creature_names):
        """Split legion child_markername containing child_creature_names off
        of legion parent_markername, leaving parent_creature_names."""
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("splitting out of turn")
        player.split_legion(parent_markername, child_markername,
          parent_creature_names, child_creature_names)

    def undo_split(self, playername, parent_markername, child_markername):
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("splitting out of turn")
        player.undo_split(parent_markername, child_markername)

    def done_with_splits(self, playername):
        """Try to end playername's split phase.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending split phase out of turn")
        if self.phase == Phase.SPLIT:
            player.done_with_splits()

    def take_mulligan(self, playername):
        """playername tries to take a mulligan."""
        player = self.get_player_by_name(playername)
        if not player.can_take_mulligan():
            raise AssertionError("illegal mulligan attempt")
        player.take_mulligan()

    def find_normal_moves(self, legion, masterhex, roll, block=None,
      came_from=None):
        """Recursively find non-teleport moves for legion from masterhex.

        If block >= 0, go only that way.
        If block == ARCHES_AND_ARROWS, use arches and arrows.
        If block == ARROWS_ONLY, use only arrows.
        Return a set of (hexlabel, entry_side) tuples.
        """
        if block is None:
            block = masterhex.find_block()
            if block is None:
                block = ARCHES_AND_ARROWS
        moves = set()
        hexlabel = masterhex.label
        player = legion.player
        # If there is an enemy legion and no friendly legion, mark the hex
        # as a legal move, and stop.
        if player.enemy_legions(self, hexlabel):
            if not player.friendly_legions(hexlabel):
                moves.add((hexlabel, masterhex.find_entry_side(came_from)))
        elif roll == 0:
            # Final destination
            # Do not add this hex if already occupied by another friendly
            # legion.
            allies = set(player.friendly_legions(hexlabel))
            allies.discard(legion)
            if not allies:
                moves.add((hexlabel, masterhex.find_entry_side(came_from)))
        elif block >= 0:
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
            moves.add((hexlabel, TELEPORT))
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
        if masterhex.tower and legion.num_lords():
            moves.update(self.find_nearby_empty_hexes(legion, masterhex, 6,
              None))
            for hexlabel in self.board.get_tower_labels():
                if hexlabel != masterhex.label and not self.all_legions(
                  hexlabel):
                    moves.add((hexlabel, TELEPORT))
        return moves

    def find_titan_teleport_moves(self, legion):
        """Return set of hexlabels describing where legion can titan
        teleport."""
        player = legion.player
        moves = set()
        if player.can_titan_teleport() and "Titan" in legion.creature_names:
            for legion in player.enemy_legions():
                hexlabel = legion.hexlabel
                if not player.friendly_legions(hexlabel):
                    moves.add((hexlabel, TELEPORT))
        return moves

    def find_all_teleport_moves(self, legion, masterhex, roll):
        """Return set of hexlabels describing where legion can teleport."""
        player = legion.player
        moves = set()
        if roll != 6 or player.teleported:
            return moves
        moves.update(self.find_tower_teleport_moves(legion, masterhex))
        moves.update(self.find_titan_teleport_moves(legion))
        return moves

    def find_all_moves(self, legion, masterhex, roll):
        """Return set of hexlabels describing where legion can move."""
        moves = self.find_normal_moves(legion, masterhex, roll)
        moves.update(self.find_all_teleport_moves(legion, masterhex, roll))
        return moves

    def can_move_legion(self, player, legion, hexlabel, entry_side, teleport,
      teleporting_lord):
        """Return True iff player can legally move this legion."""
        if player is not self.active_player or player is not legion.player:
            return False
        if legion.moved:
            return False
        masterhex = self.board.hexes[legion.hexlabel]
        if teleport:
            if (player.teleported or teleporting_lord not in
              legion.creature_names):
                return False
            moves = self.find_all_teleport_moves(legion, masterhex,
              player.movement_roll)
            if (hexlabel, TELEPORT) not in moves:
                return False
            if entry_side not in (1, 3, 5):
                return False
        else:
            moves = self.find_normal_moves(legion, masterhex,
              player.movement_roll)
            if (hexlabel, entry_side) not in moves:
                return False
        return True

    def move_legion(self, playername, markername, hexlabel, entry_side,
      teleport, teleporting_lord):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        if not self.can_move_legion(player, legion, hexlabel, entry_side,
          teleport, teleporting_lord):
            raise AssertionError("illegal move attempt")
        # TODO reveal teleporting lord
        legion.move(hexlabel, teleport, teleporting_lord, entry_side)
        if teleport:
            player.teleported = True
        action = Action.MoveLegion(self.name, playername, markername,
          hexlabel, entry_side, teleport, teleporting_lord)
        self.notify(action)

    def undo_move_legion(self, playername, markername):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        action = Action.UndoMoveLegion(self.name, playername, markername,
          legion.hexlabel, legion.entry_side, legion.teleported,
          legion.teleporting_lord)
        legion.undo_move()
        self.notify(action)

    def done_with_moves(self, playername):
        """Try to end playername's move phase."""
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending move phase out of turn")
        if self.phase == Phase.MOVE:
            player.done_with_moves()

    def resolve_engagement(self, playername, hexlabel):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("resolving engagement out of turn")
        if hexlabel not in self.engagement_hexlabels():
            raise AssertionError("no engagement to resolve in %s" % hexlabel)
        legions = self.all_legions(hexlabel)
        assert len(legions) == 2
        for legion in legions:
            if legion.player.name == playername:
                attacker = legion
            else:
                defender = legion
        player.reset_angels_pending()
        # Reveal attacker only to defender
        action = Action.RevealLegion(self.name, attacker.markername,
          attacker.creature_names)
        self.notify(action, defender.player.name)
        # Reveal defender only to attacker
        action = Action.RevealLegion(self.name, defender.markername,
          defender.creature_names)
        self.notify(action, attacker.player.name)
        self.current_engagement_hexlabel = hexlabel
        # Notify everyone that we're currently resolving this engagement
        action = Action.ResolvingEngagement(self.name, hexlabel)
        self.notify(action)
        # Let clients DTRT: flee, concede, negotiate, fight

    def _flee(self, playername, markername):
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        assert legion.can_flee()
        hexlabel = legion.hexlabel
        for legion2 in self.all_legions(hexlabel):
            if legion2 != legion:
                break
        assert legion2 != legion
        assert legion2.player != player
        legion.die(legion2, True, False)
        assert markername not in player.legions
        for legion in self.all_legions():
            assert legion.markername != markername

    def _concede(self, playername, markername):
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        hexlabel = legion.hexlabel
        for legion2 in self.all_legions(hexlabel):
            if legion2 != legion:
                break
        assert legion2 != legion
        assert legion2.player != player
        legion.die(legion2, False, False)
        assert markername not in player.legions
        for legion in self.all_legions():
            assert legion.markername != markername

    def _accept_proposal_helper(self, winning_legion, losing_legion,
      survivors):
        for creature_name in winning_legion.creature_names:
            if creature_name in survivors:
                survivors.remove(creature_name)
            else:
                winning_legion.remove_creature_by_name(creature_name)
                self.caretaker.kill_one(creature_name)
        losing_legion.die(winning_legion, False, False)

    def _accept_proposal(self, attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names):
        if not attacker_creature_names and not defender_creature_names:
            for legion in [attacker_legion, defender_legion]:
                legion.die(None, False, False)
        elif attacker_creature_names:
            assert not defender_creature_names
            winning_legion = attacker_legion
            losing_legion = defender_legion
            survivors = bag(attacker_creature_names)
            self._accept_proposal_helper(winning_legion, losing_legion,
              survivors)
        elif defender_creature_names:
            assert not attacker_creature_names
            winning_legion = defender_legion
            losing_legion = attacker_legion
            survivors = bag(defender_creature_names)
            self._accept_proposal_helper(winning_legion, losing_legion,
              survivors)


    def flee(self, playername, markername):
        """Called from Server"""
        legion = self.find_legion(markername)
        hexlabel = legion.hexlabel
        for enemy_legion in self.all_legions(hexlabel):
            if enemy_legion != legion:
                break
        assert enemy_legion != legion
        enemy_markername = enemy_legion.markername
        action = Action.Flee(self.name, markername, enemy_markername, hexlabel)
        self.notify(action)
        self._flee(playername, markername)

    def do_not_flee(self, playername, markername):
        """Called from Server"""
        legion = self.find_legion(markername)
        hexlabel = legion.hexlabel
        for enemy_legion in self.all_legions(hexlabel):
            if enemy_legion != legion:
                break
        enemy_markername = enemy_legion.markername
        action = Action.DoNotFlee(self.name, markername, enemy_markername,
          hexlabel)
        self.notify(action)

    def concede(self, playername, markername):
        """Called from Server"""
        legion = self.find_legion(markername)
        hexlabel = legion.hexlabel
        for enemy_legion in self.all_legions(hexlabel):
            if enemy_legion != legion:
                break
        enemy_markername = enemy_legion.markername
        self._concede(playername, markername)
        action = Action.Concede(self.name, markername, enemy_markername,
          hexlabel)
        self.notify(action)

    def make_proposal(self, playername, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        """Called from Server"""
        attacker_legion = self.find_legion(attacker_markername)
        defender_legion = self.find_legion(defender_markername)
        if attacker_legion is None or defender_legion is None:
            return
        attacker_player = attacker_legion.player
        if attacker_player.name == playername:
            other_player = defender_legion.player
        else:
            other_player = attacker_legion.player
        action = Action.MakeProposal(self.name, playername, other_player.name,
          attacker_markername, attacker_creature_names,
          defender_markername, defender_creature_names)
        self.notify(action)

    def accept_proposal(self, playername, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        """Called from Server"""
        attacker_legion = self.find_legion(attacker_markername)
        defender_legion = self.find_legion(defender_markername)
        if attacker_legion is None or defender_legion is None:
            return
        attacker_player = attacker_legion.player
        if attacker_player.name == playername:
            other_player = defender_legion.player
        else:
            other_player = attacker_legion.player
        self._accept_proposal(attacker_legion, attacker_creature_names,
          defender_legion, defender_creature_names)
        action = Action.AcceptProposal(self.name, playername,
          other_player.name, attacker_markername, attacker_creature_names,
          defender_markername, defender_creature_names,
          attacker_legion.hexlabel)
        self.notify(action)

    def reject_proposal(self, playername, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        """Called from Server"""
        attacker_legion = self.find_legion(attacker_markername)
        defender_legion = self.find_legion(defender_markername)
        if attacker_legion is None or defender_legion is None:
            return
        attacker_player = attacker_legion.player
        if attacker_player.name == playername:
            other_player = defender_legion.player
        else:
            other_player = attacker_legion.player
        action = Action.RejectProposal(self.name, playername,
          other_player.name, attacker_markername, attacker_creature_names,
          defender_markername, defender_creature_names)
        self.notify(action)

    # XXX Need playername?
    def fight(self, playername, attacker_markername, defender_markername):
        """Called from Server"""
        attacker_legion = self.find_legion(attacker_markername)
        defender_legion = self.find_legion(defender_markername)
        hexlabel = attacker_legion.hexlabel
        assert defender_legion.hexlabel == hexlabel
        action = Action.RevealLegion(self.name, attacker_markername,
          attacker_legion.creature_names)
        self.notify(action)
        action = Action.RevealLegion(self.name, defender_markername,
          defender_legion.creature_names)
        self.notify(action)
        self._init_battle(attacker_legion, defender_legion)
        action = Action.Fight(self.name, attacker_markername,
          defender_markername, hexlabel)
        self.notify(action)

    def acquire_angel(self, playername, markername, angel_name):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        angel = Creature.Creature(angel_name)
        legion.acquire(angel)

    def done_with_engagements(self, playername):
        """Try to end playername's fight phase."""
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending fight phase out of turn")
        if self.phase == Phase.FIGHT:
            player.done_with_engagements()

    def recruit_creature(self, playername, markername, creature_name):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        if player not in [self.active_player, self.battle_active_player]:
            raise AssertionError("recruiting out of turn")
        # Avoid double recruit
        if not legion.recruited:
            creature = Creature.Creature(creature_name)
            legion.recruit(creature)
            if self.phase == Phase.FIGHT:
                creature.hexlabel = "DEFENDER"

    def undo_recruit(self, playername, markername):
        player = self.get_player_by_name(playername)
        legion = player.legions[markername]
        if player is not self.active_player:
            raise AssertionError("recruiting out of turn")
        legion.undo_recruit()

    def done_with_recruits(self, playername):
        """Try to end playername's muster phase."""
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending muster phase out of turn")
        if self.phase == Phase.MUSTER:
            player.done_with_recruits()

    def engagement_hexlabels(self):
        """Return a set of all hexlabels with engagements"""
        hexlabels_to_legion_colors = {}
        for legion in self.all_legions():
            hexlabel = legion.hexlabel
            color = legion.player.color
            if hexlabel in hexlabels_to_legion_colors:
                hexlabels_to_legion_colors[hexlabel].add(color)
            else:
                hexlabels_to_legion_colors[hexlabel] = set([color])
        results = set()
        for hexlabel, colorset in hexlabels_to_legion_colors.iteritems():
            if len(colorset) >= 2:
                results.add(hexlabel)
        return results

    # XXX Need playername?
    def save(self, playername):
        """Save this game to a file on the local disk.

        Called from Server
        """
        if not os.path.exists(prefs.SAVE_DIR):
            os.makedirs(prefs.SAVE_DIR)
        basename = "%s_%d.save" % (self.name, time.time())
        save_path = os.path.join(prefs.SAVE_DIR, basename)
        save_file = open(save_path, "w")
        self.history.save(save_file)
        save_file.close()

    def check_for_victory(self):
        living = self.living_players
        if len(living) >= 2:
            # game still going
            self.players_left = living[:]
            return
        elif len(living) == 1:
            # sole winner
            self.players_left = living[:]
            winner_names = [living[0].name]
        else:
            # draw
            winner_names = [player.name for player in self.players_left]
        print "game over", winner_names
        action = Action.GameOver(self.name, winner_names)
        self.notify(action)


    # Battle methods

    def other_battle_legion(self, legion):
        """Return the other legion in the battle."""
        for legion2 in self.battle_legions:
            if legion2 != legion:
                return legion2

    def creatures_in_battle_hex(self, hexlabel):
        """Return a set of all creatures in the battlehex with hexlabel."""
        creatures = set()
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if creature.hexlabel == hexlabel:
                    creatures.add(creature)
        return creatures

    def is_battle_hex_occupied(self, hexlabel):
        """Return True iff there's a creature in the hex with hexlabel."""
        return bool(self.creatures_in_battle_hex(hexlabel))

    def battle_hex_entry_cost(self, creature, terrain, border):
        """Return the cost for creature to enter a battle hex with terrain,
        crossing border.  For fliers, this means landing in the hex, not
        just flying over it.

        If the creature cannot enter the hex, return maxint.

        This does not take other creatures in the hex into account.
        """
        cost = 1
        # terrains
        if terrain in ["Tree"]:
            return maxint
        elif terrain in ["Bog", "Volcano"]:
            if not creature.is_native(terrain):
                return maxint
        elif terrain in ["Bramble", "Drift", "Sand"]:
            if not creature.is_native(terrain):
                cost += 1
        # borders
        if border in ["Slope"]:
            if not creature.is_native(border) and not creature.flies:
                cost += 1
        elif border in ["Wall"]:
            if not creature.flies:
                cost += 1
        elif border in ["Cliff"]:
            if not creature.flies:
                return maxint
        return cost

    def battle_hex_flyover_cost(self, creature, terrain):
        """Return the cost for creature to fly over the hex with terrain.
        This does not include landing in the hex.

        If the creature cannot fly over the hex, return maxint.
        """
        if not creature.flies:
            return maxint
        if terrain in ["Volcano"]:
            if not creature.is_native(terrain):
                return maxint
        return 1

    def _find_battle_moves_inner(self, creature, hexlabel, movement_left):
        """Return a set of all hexlabels to which creature can move,
        starting from hexlabel, with movement_left.

        Do not include hexlabel itself.
        """
        result = set()
        if movement_left <= 0:
            return result
        hex1 = self.battlemap.hexes[hexlabel]
        for hexside, hex2 in hex1.neighbors.iteritems():
            if creature.flies or not self.is_battle_hex_occupied(hex2.label):
                if hex1.entrance:
                    # Ignore hexside penalties from entrances.  There aren't
                    # any on the standard boards, and this avoids having to
                    # properly compute the real hexside.
                    border = None
                else:
                    border = hex1.opposite_border(hexside)
                cost = self.battle_hex_entry_cost(creature, hex2.terrain,
                  border)
                if cost <= movement_left:
                    if not self.is_battle_hex_occupied(hex2.label):
                        result.add(hex2.label)
                if creature.flies:
                    flyover_cost = self.battle_hex_flyover_cost(creature,
                      hex2.terrain)
                else:
                    flyover_cost = maxint
                min_cost = min(cost, flyover_cost)
                if min_cost < movement_left:
                    result.update(self._find_battle_moves_inner(creature,
                      hex2.label, movement_left - min_cost))
        result.discard(hexlabel)
        return result

    def find_battle_moves(self, creature):
        """Return a set of all hexlabels to which creature can move,
        excluding its current hex"""
        result = set()
        if creature.moved or creature.engaged:
            return result
        if (self.battle_turn == 1 and creature.legion == self.defender_legion
          and self.battlemap.startlist):
            for hexlabel2 in self.battlemap.startlist:
                if not self.is_battle_hex_occupied(hexlabel2):
                    result.add(hexlabel2)
            return result
        return self._find_battle_moves_inner(creature, creature.hexlabel,
          creature.skill)

    def move_creature(self, playername, creature_name, old_hexlabel,
      new_hexlabel):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        if player != self.battle_active_player:
            raise AssertionError("wrong player tried to move")
        for creature in self.battle_active_legion.creatures:
            if (creature.name == creature_name and creature.hexlabel ==
              old_hexlabel):
                break
        else:
            raise AssertionError("no %s in %s" % (creature_name, old_hexlabel))
        creature.move(new_hexlabel)
        action = Action.MoveCreature(self.name, playername, creature_name,
          old_hexlabel, new_hexlabel)
        self.notify(action)

    def undo_move_creature(self, playername, creature_name, new_hexlabel):
        """Called from Server"""
        player = self.get_player_by_name(playername)
        for legion in self.battle_legions:
            if legion.player == player:
                break
        else:
            legion = None
        for creature in legion.creatures:
            if (creature.name == creature_name and creature.hexlabel ==
              new_hexlabel):
                break
        else:
            creature = None
        action = Action.UndoMoveCreature(self.name, playername, creature_name,
          creature.previous_hexlabel, new_hexlabel)
        creature.undo_move()
        self.notify(action)

    def done_with_reinforcements(self, playername):
        """Try to end playername's reinforce battle phase.

        Called from Server
        """
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending maneuver phase out of turn")
        if self.battle_phase == Phase.REINFORCE:
            player.done_with_reinforcements()

    def done_with_maneuvers(self, playername):
        """Try to end playername's maneuver battle phase.

        Called from Server
        """
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending maneuver phase out of turn")
        if self.battle_phase == Phase.MANEUVER:
            player.done_with_maneuvers()

    def apply_drift_damage(self):
        """Apply drift damage to any non-natives in drift."""
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if not creature.dead:
                    hex1 = self.battlemap.hexes[creature.hexlabel]
                    if hex1.terrain == "Drift" and not creature.is_native(
                      hex1.terrain):
                        creature.hits += 1

    def strike(self, playername, striker_name, striker_hexlabel, target_name,
      target_hexlabel, num_dice, strike_number):
        """Called from Server"""
        print "Game.strike"
        player = self.get_player_by_name(playername)
        assert player == self.battle_active_player, "striking out of turn"
        assert self.battle_phase in [Phase.STRIKE, Phase.COUNTERSTRIKE], \
          "striking out of phase"
        strikers = self.creatures_in_battle_hex(striker_hexlabel)
        assert len(strikers) == 1
        striker = strikers.pop()
        print "striker", striker
        assert striker.name == striker_name
        targets = self.creatures_in_battle_hex(target_hexlabel)
        assert len(targets) == 1
        target = targets.pop()
        assert target.name == target_name
        print "target", target
        assert num_dice == striker.number_of_dice(target)
        print "num_dice", num_dice
        assert strike_number == striker.strike_number(target)
        print "strike_number", strike_number
        rolls = Dice.roll(num_dice)
        print "rolls", rolls
        hits = 0
        for roll in rolls:
            if roll >= strike_number:
                hits += 1
        print "hits", hits
        target.hits += hits
        target.hits = min(target.hits, target.power)
        # TODO carries
        carries = 0
        striker.struck = True
        action = Action.Strike(self.name, playername, striker_name,
          striker_hexlabel, target_name, target_hexlabel, num_dice,
          strike_number, rolls, hits, carries)
        print "action", action
        self.notify(action)

    def done_with_strikes(self, playername):
        """Try to end playername's strike battle phase.

        Called from Server
        """
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending strike phase out of turn")
        if self.battle_phase == Phase.STRIKE:
            player.done_with_strikes()

    def is_battle_over(self):
        """Return True iff the battle is over."""
        for legion in self.battle_legions:
            if legion.dead:
                return True
        if self.battle_turn > 7:
            return True
        return False

    def _end_battle(self):
        if self.battle_turn > 7:
            self.attacker_legion.die(self.defender_legion, False, True)
        elif self.attacker_legion.dead and self.defender_legion.dead:
            self.attacker_legion.die(self.defender_legion, False, True)
            self.defender_legion.die(self.attacker_legion, False, True)
        elif self.attacker_legion.dead:
            self.attacker_legion.die(self.defender_legion, False, False)
        elif self.defender_legion.dead:
            self.defender_legion.die(self.attacker_legion, False, False)
        else:
            assert False, "bug in Game._end_battle"
        for legion in self.battle_legions:
            if not legion.dead:
                creature_names_to_remove = []
                # Avoid modifying list while iterating over it.
                for creature in legion.creatures:
                    if creature.dead:
                        creature_names_to_remove.append(creature.name)
                    creature.heal()
                for creature_name in creature_names_to_remove:
                    legion.remove_creature_by_name(creature_name)
                    self.caretaker.kill_one(creature_name)

        self.current_engagement_hexlabel = None
        self._cleanup_battle()


    def done_with_counterstrikes(self, playername):
        """Try to end playername's counterstrike battle phase.

        Called from Server
        """
        print "Game.done_with_counterstrikes", playername
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending counterstrike phase out of turn")
        if self.battle_phase != Phase.COUNTERSTRIKE:
            return
        if (playername == self.defender_legion.player.name and not
          self.is_battle_over()):
            self.battle_turn += 1
            print "bumped battle_turn to", self.battle_turn
        if self.is_battle_over():
            print "battle over"
            time_loss = self.battle_turn > 7
            print "time_loss is", time_loss
            # If it's a draw, arbitrarily call the defender the "winner"
            if time_loss or self.attacker_legion.dead:
                winner = self.defender_legion
            else:
                winner = self.attacker_legion
            loser = self.other_battle_legion(winner)
            print "winner", winner, "loser", loser
            action = Action.BattleOver(self.name, winner.markername,
              winner.living_creature_names, winner.dead_creature_names,
              loser.markername, loser.living_creature_names,
              loser.dead_creature_names, time_loss,
              self.current_engagement_hexlabel)
            self.notify(action)
            self._end_battle()
        else:
            player.done_with_counterstrikes()

    def clear_battle_flags(self):
        """Reset all per-turn battle creature flags, for a battle turn."""
        for legion in self.battle_legions:
            for creature in legion.creatures:
                creature.moved = False
                creature.previous_hexlabel = None
                creature.struck = False

    def cleanup_offboard_creatures(self):
        for legion in self.battle_legions:
            if legion != self.battle_active_legion:
                for creature in legion.creatures:
                    if not creature.dead:
                        hex1 = self.battlemap.hexes[creature.hexlabel]
                        if hex1.entrance:
                            # TODO Unsummon / unrecruit instead if needed
                            creature.kill()

    def cleanup_dead_creatures(self):
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if creature.dead:
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = None
                    # TODO Move to graveyard instead

    def update(self, observed, action):
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
            if action.child_markername not in player.legions:
                self.split_legion(action.playername, action.parent_markername,
                  action.child_markername, action.parent_creature_names,
                  action.child_creature_names)

        elif isinstance(action, Action.UndoSplit):
            player = self.get_player_by_name(action.playername)
            # Avoid doing the same split twice.
            if action.child_markername in player.legions:
                self.undo_split(action.playername, action.parent_markername,
                  action.child_markername)

        elif isinstance(action, Action.RollMovement):
            player = self.get_player_by_name(action.playername)
            self.phase = Phase.MOVE
            # Possibly redundant, but harmless
            player.movement_roll = action.movement_roll

        elif isinstance(action, Action.MoveLegion):
            player = self.get_player_by_name(action.playername)
            markername = action.markername
            legion = player.legions[markername]
            hexlabel = action.hexlabel
            # Avoid double move
            if not (legion.moved and legion.hexlabel == hexlabel):
                self.move_legion(action.playername, markername,
                  action.hexlabel, action.entry_side, action.teleport,
                  action.teleporting_lord)

        elif isinstance(action, Action.UndoMoveLegion):
            player = self.get_player_by_name(action.playername)
            markername = action.markername
            legion = player.legions[markername]
            # Avoid double undo
            if legion.moved:
                self.undo_move_legion(action.playername, markername)

        elif isinstance(action, Action.DoneMoving):
            player = self.get_player_by_name(action.playername)
            if self.engagement_hexlabels():
                self.phase = Phase.FIGHT
            else:
                self.phase = Phase.MUSTER

        elif isinstance(action, Action.ResolvingEngagement):
            for player in self.players:
                player.reset_angels_pending()

        elif isinstance(action, Action.Flee):
            legion = self.find_legion(action.markername)
            playername = legion.player.name
            self._flee(playername, action.markername)

        elif isinstance(action, Action.Concede):
            legion = self.find_legion(action.markername)
            playername = legion.player.name
            self._concede(playername, action.markername)

        elif isinstance(action, Action.AcceptProposal):
            attacker_legion = self.find_legion(action.attacker_markername)
            defender_legion = self.find_legion(action.defender_markername)
            self._accept_proposal(attacker_legion,
              action.attacker_creature_names, defender_legion,
              action.defender_creature_names)

        elif isinstance(action, Action.AcquireAngel):
            self.acquire_angel(action.playername, action.markername,
              action.angel_name)

        elif isinstance(action, Action.DoneFighting):
            self.phase = Phase.MUSTER
            for player in self.players:
                player.reset_angels_pending()

        elif isinstance(action, Action.RecruitCreature):
            self.recruit_creature(action.playername, action.markername,
              action.creature_name)

        elif isinstance(action, Action.UndoRecruit):
            self.undo_recruit(action.playername, action.markername)

        elif isinstance(action, Action.DoneRecruiting):
            player = self.get_player_by_name(action.playername)
            self.phase = Phase.SPLIT
            player_num = self.players.index(player)
            # TODO Skip dead players
            new_player_num = (player_num + 1) % len(self.players)
            if new_player_num == 0:
                self.turn += 1
            self.active_player = self.players[new_player_num]
            for player in self.players:
                player.new_turn()

        elif isinstance(action, Action.Fight):
            attacker_markername = action.attacker_markername
            defender_markername = action.defender_markername
            self.fight(None, attacker_markername, defender_markername)

        elif isinstance(action, Action.MoveCreature):
            for creature in self.battle_active_legion.creatures:
                if (creature.name == action.creature_name and
                  creature.hexlabel == action.old_hexlabel):
                    break
            else:
                raise AssertionError("no %s in %s" % (action.creature_name,
                  action.old_hexlabel))
            creature.move(action.new_hexlabel)

        elif isinstance(action, Action.UndoMoveCreature):
            for creature in self.battle_active_legion.creatures:
                if (creature.name == action.creature_name and
                  creature.hexlabel == action.new_hexlabel):
                    break
            else:
                raise AssertionError("no %s in %s" % (action.creature_name,
                  action.old_hexlabel))
            # XXX Avoid double undo
            if creature.moved:
                creature.undo_move()

        elif isinstance(action, Action.DoneReinforcing):
            self.battle_phase = Phase.MANEUVER

        elif isinstance(action, Action.DoneManeuvering):
            self.battle_phase = Phase.DRIFTDAMAGE
            self.apply_drift_damage()
            self.battle_phase = Phase.STRIKE

        # TODO carries
        elif isinstance(action, Action.Strike):
            target = self.creatures_in_battle_hex(action.target_hexlabel).pop()
            target.hits += action.hits
            target.hits = min(target.hits, target.power)
            striker = self.creatures_in_battle_hex(
              action.striker_hexlabel).pop()
            striker.struck = True

        elif isinstance(action, Action.DoneStriking):
            self.battle_phase = Phase.COUNTERSTRIKE
            # Switch active players before the counterstrike phase.
            if action.playername == self.defender_legion.player.name:
                self.battle_active_legion = self.attacker_legion
            else:
                self.battle_active_legion = self.defender_legion

        elif isinstance(action, Action.DoneStrikingBack):
            self.clear_battle_flags()
            self.cleanup_offboard_creatures()
            self.cleanup_dead_creatures()
            self.battle_turn = action.battle_turn
            if self.battle_turn > 7:
                raise Exception("should have ended on time loss")
            self.battle_phase = Phase.REINFORCE

        elif isinstance(action, Action.BattleOver):
            if action.time_loss:
                self.battle_turn = 8
            self._end_battle()

        self.notify(action)
