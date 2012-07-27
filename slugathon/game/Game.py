__copyright__ = "Copyright (c) 2005-2012 David Ripton"
__license__ = "GNU GPL v2"


from sys import maxint
import os
import time
from collections import defaultdict
import logging

from twisted.internet import reactor
from zope.interface import implementer

from slugathon.game import (Player, MasterBoard, Action, Phase, Caretaker,
  Creature, History, BattleMap)
from slugathon.data import playercolordata
from slugathon.util.Observed import Observed
from slugathon.util.Observer import IObserver
from slugathon.util import prefs, Dice
from slugathon.util.bag import bag
from slugathon.net import config


# Movement constants
ARCHES_AND_ARROWS = -1
ARROWS_ONLY = -2

# Entry side constants
TELEPORT = "TELEPORT"


def opposite(direction):
    return (direction + 3) % 6


@implementer(IObserver)
class Game(Observed):
    """Central class holding information about one game"""
    def __init__(self, name, owner, create_time, start_time, min_players,
      max_players, started=False, master=False,
      ai_time_limit=config.DEFAULT_AI_TIME_LIMIT,
      player_time_limit=config.DEFAULT_PLAYER_TIME_LIMIT, player_class="Human",
      player_info="", finish_time=None):
        Observed.__init__(self)
        self.name = name
        self.create_time = create_time
        self.start_time = start_time
        self.finish_time = finish_time
        self.min_players = min_players
        self.max_players = max_players
        self.started = started
        self.players = []
        self.add_player(owner, player_class, player_info)
        self.board = MasterBoard.MasterBoard()
        self.turn = 1
        self.phase = Phase.SPLIT
        self.active_player = None
        self.caretaker = Caretaker.Caretaker()
        self.history = History.History()
        self.add_observer(self.history)
        self.current_engagement_hexlabel = None
        self.defender_chose_not_to_flee = False
        self.attacker_legion = None
        self.defender_legion = None
        self.battle_masterhex = None
        self.battle_entry_side = None
        self.battlemap = None
        self.battle_turn = None
        self.battle_phase = None
        self.battle_active_legion = None
        self.first_attacker_kill = None
        self.attacker_entered = False
        self.pending_carry = None
        self.pending_summon = False
        self.pending_reinforcement = False
        self.master = master
        self.ai_time_limit = ai_time_limit
        self.player_time_limit = player_time_limit
        # list of tuples of Player like [(winner,), (tied1, tied2), (loser,)]
        self.finish_order = []

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
        self.first_attacker_kill = None
        self.attacker_entered = False
        self.pending_carry = None
        self.defender_chose_not_to_flee = False
        self.clear_battle_flags()

    def _cleanup_battle(self):
        logging.info("")
        self.current_engagement_hexlabel = None
        self.defender_chose_not_to_flee = False
        self.attacker_legion = None
        self.defender_legion = None
        self.battle_masterhex = None
        self.battle_entry_side = None
        self.battlemap = None
        self.battle_turn = None
        self.battle_phase = None
        self.battle_active_legion = None
        self.first_attacker_kill = None
        self.attacker_entered = False
        self.pending_carry = None
        self.pending_summon = False
        self.pending_reinforcement = False

    def __eq__(self, other):
        return isinstance(other, Game) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Game %s" % self.name

    @property
    def owner(self):
        """The owner of the game is the remaining player who joined first."""
        min_join_order = maxint
        owner = None
        for player in self.players:
            if player.join_order < min_join_order:
                owner = player
                min_join_order = player.join_order
        if owner is None:
            raise AssertionError("Game has no owner")
        return owner

    @property
    def playernames(self):
        return [player.name for player in self.players]

    @property
    def num_players(self):
        return len(self.players)

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    @property
    def info_tuple(self):
        """Return state as a tuple of strings for passing to client."""
        return (self.name, self.create_time, self.start_time,
          self.min_players, self.max_players, self.playernames, self.started,
          self.finish_time, self.winner_names, self.loser_names)

    def add_player(self, playername, player_class="Human", player_info=""):
        """Add a player to this game."""
        logging.info("%s %s %s", playername, player_class, player_info)
        if playername in self.playernames:
            logging.info("add_player from %s already in game %s" % (
              playername, self.name))
            return
        if len(self.players) >= self.max_players:
            raise AssertionError("%s tried to join full game %s" % (playername,
              self.name))
        if player_class == "Human":
            player_info = playername
        player = Player.Player(playername, self, self.num_players,
          player_class, player_info)
        self.players.append(player)
        player.add_observer(self)

    def remove_player(self, playername):
        """Remove a player from this game.

        Not allowed after the game has started.
        """
        if self.started:
            raise AssertionError("remove_player on started game")
        player = self.get_player_by_name(playername)
        if player is None:
            # already removed, okay
            pass
        else:
            player.remove_observer(self)
            self.players.remove(player)

    @property
    def living_players(self):
        """Return a list of Players still in the game."""
        return [player for player in self.players if not player.dead]

    @property
    def living_playernames(self):
        """Return a list of playernames for Players still in the game."""
        return [player.name for player in self.living_players]

    @property
    def dead_playernames(self):
        """Return a list of playernames for Players out of the game."""
        return [player.name for player in self.players if player.dead]

    @property
    def over(self):
        """Return True iff the game is over."""
        return self.finish_time or len(self.living_players) <= 1

    @property
    def next_player_and_turn(self):
        """Return the next player and what game turn it will be when
        his turn starts."""
        if self.over:
            return None, self.turn
        player = self.active_player
        player_num = self.players.index(player)
        turn = self.turn
        dead = True
        while dead:
            player_num = (player_num + 1) % len(self.players)
            if player_num == 0:
                turn += 1
            player = self.players[player_num]
            dead = player.dead
        return player, turn

    @property
    def winner_names(self):
        # Hack to easily override the property for old games on the client.
        if hasattr(self, "_winner_names"):
            return self._winner_names
        if self.over and self.finish_order:
            winner_players = self.finish_order[0]
            return [player.name for player in winner_players]
        return []

    @property
    def loser_names(self):
        # Hack to easily override the property for old games on the client.
        if hasattr(self, "_loser_names"):
            return self._loser_names
        losers = []
        if self.over:
            start_index = 1
        else:
            start_index = 0
        for players in self.finish_order[start_index:]:
            losers.extend(players)
        return [player.name for player in losers]

    def assign_towers(self):
        """Randomly assign a tower to each player."""
        towers = self.board.get_tower_labels()
        Dice.shuffle(towers)
        for num, player in enumerate(self.players):
            player.assign_starting_tower(towers[num])

    def start(self, playername):
        """Begin the game.

        Called from Server, only by game owner.
        """
        if playername != self.owner.name:
            raise AssertionError("Game.start %s called by non-owner %s" % (
              self.name, playername))
        self.started = True
        self.start_time = time.time()
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

    @property
    def done_assigning_towers(self):
        """Return True iff we're done assigning towers to all players."""
        for player in self.players:
            if player.starting_tower is None:
                return False
        return True

    @property
    def next_playername_to_pick_color(self):
        """Return the name of the player whose turn it is to pick a color."""
        if not self.done_assigning_towers:
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

    @property
    def colors_left(self):
        """Return a list of player colors that aren't taken yet."""
        left = playercolordata.colors[:]
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
        if playername != self.next_playername_to_pick_color:
            raise AssertionError("illegal assign_color attempt %s %s" %
              (playername, color))
        if color not in self.colors_left:
            raise AssertionError("tried to take unavailable color")
        player.assign_color(color)

    @property
    def done_assigning_first_markers(self):
        """Return True iff each player has picked his first marker."""
        for player in self.players:
            if player.selected_markerid is None:
                return False
        return True

    def assign_first_marker(self, playername, markerid):
        """Use markerid for playername's first legion marker.

        Once all players have done this, create the starting legions.
        """
        player = self.get_player_by_name(playername)
        logging.info(player.markerids_left)
        if markerid not in player.markerids_left:
            raise AssertionError("marker not available")
        player.pick_marker(markerid)
        if self.done_assigning_first_markers:
            for player in self.players:
                player.create_starting_legion()

    def all_legions(self, hexlabel=None):
        """Return a set of all legions in hexlabel, or in the whole
        game if hexlabel is None"""
        legions = set()
        for player in self.players:
            for legion in player.legions:
                if hexlabel in (None, legion.hexlabel) and len(legion):
                    legions.add(legion)
        return legions

    def find_legion(self, markerid):
        """Return the legion called markerid, or None."""
        for player in self.players:
            if markerid in player.markerid_to_legion:
                return player.markerid_to_legion[markerid]
        return None

    def split_legion(self, playername, parent_markerid, child_markerid,
      parent_creature_names, child_creature_names):
        """Split legion child_markerid containing child_creature_names off
        of legion parent_markerid, leaving parent_creature_names.

        Called from Server and update.
        """
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("splitting out of turn")
        if self.phase != Phase.SPLIT:
            raise AssertionError("splitting out of phase")
        player.split_legion(parent_markerid, child_markerid,
          parent_creature_names, child_creature_names)

    def undo_split(self, playername, parent_markerid, child_markerid):
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("splitting out of turn")
        player.undo_split(parent_markerid, child_markerid)

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
        """playername tries to take a mulligan.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if not player.can_take_mulligan:
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
        if player.enemy_legions(hexlabel):
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
        """Return set of (hexlabel, TELEPORT) describing where legion can tower
        teleport."""
        moves = set()
        if masterhex.tower and legion.num_lords:
            moves.update(self.find_nearby_empty_hexes(legion, masterhex, 6,
              None))
            for hexlabel in self.board.get_tower_labels():
                if hexlabel != masterhex.label and not self.all_legions(
                  hexlabel):
                    moves.add((hexlabel, TELEPORT))
        return moves

    def find_titan_teleport_moves(self, legion):
        """Return set of (hexlabel, TELEPORT) describing where legion can titan
        teleport."""
        player = legion.player
        moves = set()
        if player.can_titan_teleport and "Titan" in legion.creature_names:
            for legion in player.enemy_legions():
                hexlabel = legion.hexlabel
                if not player.friendly_legions(hexlabel):
                    moves.add((hexlabel, TELEPORT))
        return moves

    def find_all_teleport_moves(self, legion, masterhex, roll):
        """Return set of (hexlabel, TELEPORT) tuples describing where legion
        can teleport."""
        player = legion.player
        moves = set()
        if roll != 6 or player.teleported:
            return moves
        moves.update(self.find_tower_teleport_moves(legion, masterhex))
        moves.update(self.find_titan_teleport_moves(legion))
        return moves

    def find_all_moves(self, legion, masterhex, roll):
        """Return set of (hexlabel, entry_side) tuples describing where legion
        can move."""
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
            terrain = self.board.hexes[hexlabel].terrain
            if terrain == "Tower" and entry_side != 5:
                return False
        else:
            moves = self.find_normal_moves(legion, masterhex,
              player.movement_roll)
            if (hexlabel, entry_side) not in moves:
                return False
        return True

    def move_legion(self, playername, markerid, hexlabel, entry_side,
      teleport, teleporting_lord):
        """Called from Server and update."""
        logging.info("%s %s %s %s %s %s", playername, markerid,
          hexlabel, entry_side, teleport, teleporting_lord)
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        previous_hexlabel = legion.hexlabel
        legion.move(hexlabel, teleport, teleporting_lord, entry_side)
        action = Action.MoveLegion(self.name, playername, markerid,
          hexlabel, entry_side, teleport, teleporting_lord, previous_hexlabel)
        self.notify(action)

    def undo_move_legion(self, playername, markerid):
        """Called from Server and update."""
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        action = Action.UndoMoveLegion(self.name, playername, markerid,
          legion.hexlabel, legion.entry_side, legion.teleported,
          legion.teleporting_lord, legion.previous_hexlabel)
        legion.undo_move()
        self.notify(action)

    def done_with_moves(self, playername):
        """Try to end playername's move phase.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            raise AssertionError("ending move phase out of turn")
        if self.phase == Phase.MOVE:
            player.done_with_moves()

    def resolve_engagement(self, playername, hexlabel):
        """Called from Server."""
        logging.info("")
        if (self.pending_summon or self.pending_reinforcement or
          self.pending_acquire):
            logging.info("cannot move on to next engagement yet")
            return
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            logging.info("resolving engagement out of turn")
            return
        if hexlabel not in self.engagement_hexlabels:
            logging.info("no engagement to resolve in %s" % hexlabel)
            return
        legions = self.all_legions(hexlabel)
        assert len(legions) == 2
        for legion in legions:
            if legion.player.name == playername:
                attacker = legion
            else:
                defender = legion
        # Reveal attacker only to defender
        action = Action.RevealLegion(self.name, attacker.markerid,
          attacker.creature_names)
        self.notify(action, [defender.player.name])
        # Reveal defender only to attacker
        action = Action.RevealLegion(self.name, defender.markerid,
          defender.creature_names)
        self.notify(action, [attacker.player.name])
        self.current_engagement_hexlabel = hexlabel
        # Notify everyone that we're currently resolving this engagement
        action = Action.ResolvingEngagement(self.name, hexlabel)
        self.notify(action)
        # Let clients DTRT: flee, concede, negotiate, fight

    def _flee(self, playername, markerid):
        player = self.get_player_by_name(playername)
        if player == self.active_player:
            logging.info("attacker tried to flee")
            return
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        if legion.player != player:
            logging.info("wrong player tried to flee")
            return
        if not legion.can_flee:
            logging.info("illegal flee attempt")
            return
        hexlabel = legion.hexlabel
        for legion2 in self.all_legions(hexlabel):
            if legion2 != legion:
                break
        # Abort if the enemy managed to concede.
        if legion2 == legion or legion2.player == player:
            return
        legion.die(legion2, True, False, kill_all_creatures=True)
        assert markerid not in player.markerid_to_legion
        for legion in self.all_legions():
            assert legion.markerid != markerid

    def _concede(self, playername, markerid):
        logging.info("%s %s", playername, markerid)
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            logging.info("")
            return
        hexlabel = legion.hexlabel
        for legion2 in self.all_legions(hexlabel):
            if legion2 != legion:
                break
        if legion2 == legion or legion2.player == player:
            # Can't concede because other legion already did.
            logging.info("")
            return
        if legion in self.battle_legions:
            # conceding during battle
            for creature in legion.creatures:
                creature.kill()
            player = legion.player
            if player == self.battle_active_player:
                logging.info("")
                player.done_with_battle_phase()
        else:
            # conceding before battle
            legion.die(legion2, False, False, kill_all_creatures=True)
            assert markerid not in player.markerid_to_legion
            for legion in self.all_legions():
                assert legion.markerid != markerid

    def _accept_proposal_helper(self, winning_legion, losing_legion,
      survivors):
        for creature_name in winning_legion.creature_names:
            if creature_name in survivors:
                survivors.remove(creature_name)
            else:
                winning_legion.remove_creature_by_name(creature_name)
                self.caretaker.kill_one(creature_name)
        losing_legion.die(winning_legion, False, False,
          kill_all_creatures=True)

    def _accept_proposal(self, attacker_legion, attacker_creature_names,
      defender_legion, defender_creature_names):
        if not attacker_creature_names and not defender_creature_names:
            for legion in [attacker_legion, defender_legion]:
                action = Action.RevealLegion(self.name, legion.markerid,
                  legion.creature_names)
                self.notify(action)
            for legion in [attacker_legion, defender_legion]:
                legion.die(None, False, True, kill_all_creatures=True)
        elif attacker_creature_names:
            assert not defender_creature_names
            winning_legion = attacker_legion
            losing_legion = defender_legion
            action = Action.RevealLegion(self.name, losing_legion.markerid,
              losing_legion.creature_names)
            self.notify(action)
            survivors = bag(attacker_creature_names)
            self._accept_proposal_helper(winning_legion, losing_legion,
              survivors)
        elif defender_creature_names:
            assert not attacker_creature_names
            winning_legion = defender_legion
            losing_legion = attacker_legion
            action = Action.RevealLegion(self.name, losing_legion.markerid,
              losing_legion.creature_names)
            self.notify(action)
            survivors = bag(defender_creature_names)
            self._accept_proposal_helper(winning_legion, losing_legion,
              survivors)

    def _do_not_flee(self, playername, markerid):
        """Called from update."""
        self.defender_chose_not_to_flee = True

    def concede(self, playername, markerid):
        """Called from Server."""
        legion = self.find_legion(markerid)
        if legion is None:
            # Player is already out of the game.
            return
        hexlabel = legion.hexlabel
        for enemy_legion in self.all_legions(hexlabel):
            if enemy_legion != legion:
                break
        if enemy_legion == legion:
            return
        action = Action.RevealLegion(self.name, markerid,
          legion.creature_names)
        self.notify(action)
        enemy_markerid = enemy_legion.markerid
        self._concede(playername, markerid)
        action = Action.Concede(self.name, markerid, enemy_markerid,
          hexlabel)
        self.notify(action)

    def make_proposal(self, playername, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        """Called from Server."""
        attacker_legion = self.find_legion(attacker_markerid)
        defender_legion = self.find_legion(defender_markerid)
        if attacker_legion is None or defender_legion is None:
            return
        attacker_player = attacker_legion.player
        if attacker_player.name == playername:
            other_player = defender_legion.player
        else:
            other_player = attacker_legion.player
        action = Action.MakeProposal(self.name, playername, other_player.name,
          attacker_markerid, attacker_creature_names,
          defender_markerid, defender_creature_names)
        self.notify(action)

    def accept_proposal(self, playername, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        """Called from Server."""
        attacker_legion = self.find_legion(attacker_markerid)
        defender_legion = self.find_legion(defender_markerid)
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
          other_player.name, attacker_markerid, attacker_creature_names,
          defender_markerid, defender_creature_names,
          attacker_legion.hexlabel)
        self.notify(action)

    def reject_proposal(self, playername, attacker_markerid,
      attacker_creature_names, defender_markerid, defender_creature_names):
        """Called from Server."""
        attacker_legion = self.find_legion(attacker_markerid)
        defender_legion = self.find_legion(defender_markerid)
        if attacker_legion is None or defender_legion is None:
            return
        attacker_player = attacker_legion.player
        if attacker_player.name == playername:
            other_player = defender_legion.player
        else:
            other_player = attacker_legion.player
        action = Action.RejectProposal(self.name, playername,
          other_player.name, attacker_markerid, attacker_creature_names,
          defender_markerid, defender_creature_names)
        self.notify(action)

    def no_more_proposals(self, playername, attacker_markerid,
      defender_markerid):
        """Called from Server."""
        action = Action.NoMoreProposals(self.name, playername,
          attacker_markerid, defender_markerid)
        self.notify(action)

    def _fight(self, playername, attacker_markerid, defender_markerid):
        """Called from update."""
        logging.info("%s %s %s %s", playername, attacker_markerid,
          defender_markerid, self.battle_turn)
        attacker_legion = self.find_legion(attacker_markerid)
        defender_legion = self.find_legion(defender_markerid)
        logging.info("attacker %s", attacker_legion)
        logging.info("defender %s", defender_legion)
        if (not attacker_legion or not defender_legion or playername not in
          [attacker_legion.player.name, defender_legion.player.name]):
            logging.info("illegal fight call from %s", playername)
            return
        if defender_legion.can_flee and not self.defender_chose_not_to_flee:
            logging.info("illegal fight call while defender can still flee")
            return
        hexlabel = attacker_legion.hexlabel
        assert defender_legion.hexlabel == hexlabel
        if attacker_legion.all_known:
            action = Action.RevealLegion(self.name, attacker_markerid,
              attacker_legion.creature_names)
            self.notify(action)
        if defender_legion.all_known:
            action = Action.RevealLegion(self.name, defender_markerid,
              defender_legion.creature_names)
            self.notify(action)
        self._init_battle(attacker_legion, defender_legion)

    def acquire_angels(self, playername, markerid, angel_names):
        """Called from Server."""
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        angels = [Creature.Creature(name) for name in angel_names]
        legion.acquire_angels(angels)
        angel_names = [angel.name for angel in angels]
        action = Action.AcquireAngels(self.name, player.name, markerid,
          angel_names)
        self.notify(action)
        if (self.is_battle_over and not self.pending_summon and not
          self.pending_reinforcement):
            self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def do_not_acquire_angels(self, playername, markerid):
        """Called from Server."""
        logging.info("do_not_acquire_angels %s %s", playername, markerid)
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        legion.do_not_acquire_angels()
        if (self.is_battle_over and not self.pending_summon and not
          self.pending_reinforcement):
            self._cleanup_battle()

    def done_with_engagements(self, playername):
        """Try to end playername's fight phase.

        Called from Server.
        """
        logging.info("")
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            logging.info("%s ending fight phase out of turn" % playername)
            return
        if (self.pending_summon or self.pending_reinforcement or
          self.pending_acquire):
            raise AssertionError("cannot end engagements yet",
              "summon", self.pending_summon, "reinforcement",
              self.pending_reinforcement, "acquire", self.pending_acquire)
        if self.phase == Phase.FIGHT:
            player.done_with_engagements()

    def recruit_creature(self, playername, markerid, creature_name,
      recruiter_names):
        """Called from update."""
        logging.info("%s %s %s %s", playername, markerid, creature_name,
          recruiter_names)
        player = self.get_player_by_name(playername)
        if player:
            legion = player.markerid_to_legion.get(markerid)
        # Avoid double recruit
        if legion and not legion.recruited:
            creature = Creature.Creature(creature_name)
            legion.recruit_creature(creature, recruiter_names)
            if self.phase == Phase.FIGHT:
                creature.hexlabel = "DEFENDER"
        if self.pending_reinforcement:
            self.pending_reinforcement = False
            if self.is_battle_over and not self.pending_acquire:
                self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def undo_recruit(self, playername, markerid):
        """Called from Server and update."""
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        legion.undo_recruit()

    def done_with_recruits(self, playername):
        """Try to end playername's muster phase.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is not self.active_player:
            return
        if self.phase == Phase.MUSTER:
            player.done_with_recruits()

    def summon_angel(self, playername, markerid, donor_markerid,
      creature_name):
        """Called from Server and update."""
        logging.info("summon_angel %s %s %s %s", playername, markerid,
          donor_markerid, creature_name)
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        donor = player.markerid_to_legion.get(donor_markerid)
        if legion is None or donor is None:
            return
        logging.info("donor %s legion %s", donor, legion)
        # Avoid double summon
        if not player.summoned:
            player.summon_angel(legion, donor, creature_name)
            if self.phase == Phase.FIGHT:
                creature = legion.creatures[-1]
                creature.hexlabel = "ATTACKER"
            action = Action.SummonAngel(self.name, player.name, markerid,
              donor_markerid, creature_name)
            self.notify(action)
        self.pending_summon = False
        if self.is_battle_over and not self.pending_acquire:
            self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def do_not_summon_angel(self, playername, markerid):
        """Called from Server."""
        logging.info("")
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        player.do_not_summon_angel(legion)
        reactor.callLater(1, self._end_dead_player_turn)

    def _do_not_summon_angel(self, playername, markerid):
        """Called from update."""
        logging.info("")
        self.pending_summon = False
        if self.is_battle_over and not self.pending_acquire:
            self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def do_not_reinforce(self, playername, markerid):
        """Called from Server."""
        logging.info("")
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        player.do_not_reinforce(legion)
        reactor.callLater(1, self._end_dead_player_turn)

    def _do_not_reinforce(self, playername, markerid):
        """Called from update."""
        logging.info("")
        if self.pending_reinforcement:
            self.pending_reinforcement = False
            if self.is_battle_over and not self.pending_acquire:
                self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def _unreinforce(self, playername, markerid):
        """Called from update."""
        player = self.get_player_by_name(playername)
        legion = player.markerid_to_legion.get(markerid)
        if legion is None:
            return
        legion.unreinforce()

    def carry(self, playername, carry_target_name, carry_target_hexlabel,
      carries):
        """Called from Server."""
        logging.info("carry %s %s %s %s", playername, carry_target_name,
          carry_target_hexlabel, carries)
        if not self.pending_carry:
            logging.info("no carry pending; continuing to avoid confusing AI")
            carries = carries_left = 0
            action2 = Action.Carry(self.name, playername, "", "", "", "",
              carry_target_name, carry_target_hexlabel, 0, 0,
              carries, carries_left)
        else:
            action = self.pending_carry
            self.pending_carry = None
            if carries > action.carries:
                carries = action.carries
            striker = self.creatures_in_battle_hex(
              action.striker_hexlabel).pop()
            target = self.creatures_in_battle_hex(action.target_hexlabel).pop()
            carry_target = self.creatures_in_battle_hex(
              carry_target_hexlabel).pop()
            assert carry_target in striker.engaged_enemies
            assert striker.number_of_dice(carry_target) >= action.num_dice
            assert striker.strike_number(carry_target) <= action.strike_number
            carry_target.hits += carries
            if carry_target.hits > carry_target.power:
                carries_left = carry_target.hits - carry_target.power
                carry_target.hits -= carries_left
            else:
                carries_left = 0
            action2 = Action.Carry(self.name, playername, striker.name,
              striker.hexlabel, target.name, target.hexlabel,
              carry_target.name, carry_target.hexlabel, action.num_dice,
              action.strike_number,
              carries, carries_left)
        self.notify(action2)

    @property
    def engagement_hexlabels(self):
        """Return a set of all hexlabels with engagements"""
        hexlabels_to_legion_colors = defaultdict(set)
        for legion in self.all_legions():
            hexlabel = legion.hexlabel
            color = legion.player.color
            hexlabels_to_legion_colors[hexlabel].add(color)
        results = set()
        for hexlabel, colorset in hexlabels_to_legion_colors.iteritems():
            if len(colorset) >= 2:
                results.add(hexlabel)
        return results

    @property
    def pending_acquire(self):
        """True iff we're waiting for any player to acquire angels."""
        for player in self.players:
            if player.pending_acquire:
                return True
        return False

    def save(self, playername):
        """Save this game to a file on the local disk.

        Called from Server.
        """
        if not os.path.exists(prefs.SAVE_DIR):
            os.makedirs(prefs.SAVE_DIR)
        basename = "%s_%d.save" % (self.name, time.time())
        save_path = os.path.join(prefs.SAVE_DIR, basename)
        with open(save_path, "w") as save_file:
            self.history.save(save_file)

    def check_for_victory(self):
        """Called from update."""
        if self.over:
            self.finish_time = time.time()
            logging.info("game over %s", self.winner_names)
            action = Action.GameOver(self.name, self.winner_names,
              self.finish_time)
            self.notify(action)

    # Battle methods
    def other_battle_legion(self, legion):
        """Return the other legion in the battle."""
        for legion2 in self.battle_legions:
            if legion2 != legion:
                return legion2

    def creatures_in_battle_hex(self, hexlabel, name=None):
        """Return a set of all creatures in the battlehex with hexlabel.

        If name is not None, then return only creatures with that name.
        """
        creatures = set()
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if creature.hexlabel == hexlabel:
                    if name is None or creature.name == name:
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
        elif terrain in ["Bramble", "Drift"]:
            if not creature.is_native(terrain):
                cost += 1
        elif terrain in ["Sand"]:
            if not creature.is_native(terrain) and not creature.flies:
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

    def _find_battle_moves_inner(self, creature, hexlabel, movement_left,
      ignore_mobile_allies=False):
        """Return a set of all hexlabels to which creature can move,
        starting from hexlabel, with movement_left.

        Do not include hexlabel itself.
        """
        result = set()
        if movement_left <= 0:
            return result
        hex1 = self.battlemap.hexes[hexlabel]
        for hexside, hex2 in hex1.neighbors.iteritems():
            try:
                creature2 = self.creatures_in_battle_hex(hex2.label).pop()
            except KeyError:
                creature2 = None
            if (creature.flies or not creature2 or (ignore_mobile_allies and
              creature2.legion == creature.legion and creature2.mobile)):
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
                    try:
                        creature2 = self.creatures_in_battle_hex(
                          hex2.label).pop()
                    except KeyError:
                        creature2 = None
                    if (not creature2 or (ignore_mobile_allies and
                      creature2.legion == creature.legion and
                      creature2.mobile)):
                        result.add(hex2.label)
                if creature.flies:
                    flyover_cost = self.battle_hex_flyover_cost(creature,
                      hex2.terrain)
                else:
                    flyover_cost = maxint
                min_cost = min(cost, flyover_cost)
                if min_cost < movement_left:
                    result.update(self._find_battle_moves_inner(creature,
                      hex2.label, movement_left - min_cost,
                      ignore_mobile_allies))
        result.discard(hexlabel)
        return result

    def find_battle_moves(self, creature, ignore_mobile_allies=False):
        """Return a set of all hexlabels to which creature can move,
        excluding its current hex."""
        result = set()
        if creature.hexlabel is None:
            logging.info("find_battle_moves %s has hexlabel None", creature)
            return result
        if creature.moved or creature.engaged:
            return result
        if (self.battle_turn == 1 and creature.legion == self.defender_legion
          and self.battlemap.startlist):
            for hexlabel2 in self.battlemap.startlist:
                # There can't be any mobile allies there on turn 1.
                if not self.is_battle_hex_occupied(hexlabel2):
                    result.add(hexlabel2)
            return result
        return self._find_battle_moves_inner(creature, creature.hexlabel,
          creature.skill, ignore_mobile_allies)

    def move_creature(self, playername, creature_name, old_hexlabel,
      new_hexlabel):
        """Called from Server."""
        player = self.get_player_by_name(playername)
        if player != self.battle_active_player:
            raise AssertionError("wrong player tried to move")
        creature = self.battle_active_legion.find_creature(creature_name,
          old_hexlabel)
        if creature is None:
            raise AssertionError("no %s in %s" % (creature_name, old_hexlabel))
        if new_hexlabel not in self.find_battle_moves(creature):
            raise AssertionError("illegal battle move %s %s" % (creature,
              new_hexlabel))
        logging.info("move creature %s to %s", creature, new_hexlabel)
        creature.move(new_hexlabel)
        action = Action.MoveCreature(self.name, playername, creature_name,
          old_hexlabel, new_hexlabel)
        self.notify(action)

    def undo_move_creature(self, playername, creature_name, new_hexlabel):
        """Called from Server."""
        player = self.get_player_by_name(playername)
        for legion in self.battle_legions:
            if legion.player == player:
                break
        else:
            legion = None
        creature = self.battle_active_legion.find_creature(creature_name,
          new_hexlabel)
        if creature is None:
            logging.warning("%s %s %s", playername, creature_name,
              new_hexlabel)
            return
        action = Action.UndoMoveCreature(self.name, playername, creature_name,
          creature.previous_hexlabel, new_hexlabel)
        creature.undo_move()
        self.notify(action)

    def done_with_reinforcements(self, playername):
        """Try to end playername's reinforce battle phase.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            logging.info("%s ending reinforcement phase out of turn" %
              playername)
            return
        if self.battle_phase == Phase.REINFORCE:
            player.done_with_reinforcements()

    def done_with_maneuvers(self, playername):
        """Try to end playername's maneuver battle phase.

        Called from Server.
        """
        logging.info("%s", playername)
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending maneuver phase out of turn")
        if self.battle_phase == Phase.MANEUVER:
            player.done_with_maneuvers()

    def apply_drift_damage(self):
        """Apply drift damage to any non-natives in drift.

        Called from update.
        """
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if not creature.dead:
                    if creature.hexlabel:
                        hex1 = self.battlemap.hexes[creature.hexlabel]
                        if hex1.terrain == "Drift" and not creature.is_native(
                          hex1.terrain):
                            creature.hits += 1
                            action = Action.DriftDamage(self.name,
                              creature.name, creature.hexlabel, 1)
                            self.notify(action)
                    else:
                        logging.info("apply_drift_damage %s has hexlabel None"
                          % creature)

    def strike(self, playername, striker_name, striker_hexlabel, target_name,
      target_hexlabel, num_dice, strike_number):
        """Called from Server."""
        logging.info("")
        player = self.get_player_by_name(playername)
        assert player == self.battle_active_player, "striking out of turn"
        assert self.battle_phase in [Phase.STRIKE, Phase.COUNTERSTRIKE], \
          "striking out of phase"
        strikers = self.creatures_in_battle_hex(striker_hexlabel)
        assert len(strikers) == 1
        striker = strikers.pop()
        assert striker.can_strike, "illegal strike"
        assert striker.name == striker_name
        targets = self.creatures_in_battle_hex(target_hexlabel)
        assert len(targets) == 1
        target = targets.pop()
        assert target.name == target_name
        logging.info("striker %s target %s", striker, target)
        logging.info("num_dice %s strike_number %s", num_dice, strike_number)
        assert (num_dice, strike_number) in striker.valid_strike_penalties(
          target)
        rolls = Dice.roll(num_dice)
        hits = 0
        for roll in rolls:
            if roll >= strike_number:
                hits += 1
        logging.info("rolls %s hits %s", rolls, hits)
        target.hits += hits
        if target.is_titan and target.dead:
            target.legion.player.has_titan = False
        if target.hits > target.power:
            carries = target.hits - target.power
            target.hits -= carries
            max_carries = striker.max_possible_carries(target, num_dice,
              strike_number)
            carries = min(carries, max_carries)
        else:
            carries = 0
        striker.struck = True
        action = Action.Strike(self.name, playername, striker_name,
          striker_hexlabel, target_name, target_hexlabel, num_dice,
          strike_number, rolls, hits, carries)
        if carries:
            self.pending_carry = action
        self.notify(action)

    def done_with_strikes(self, playername):
        """Try to end playername's strike battle phase.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            raise AssertionError("ending strike phase out of turn")
        if self.battle_phase == Phase.STRIKE:
            player.done_with_strikes()

    @property
    def is_battle_over(self):
        """Return True iff the battle is over."""
        logging.info("battle_legions %s", self.battle_legions)
        for legion in self.battle_legions:
            if legion.dead:
                logging.info("%s is dead", legion)
                return True
        if self.battle_turn > 7:
            logging.info("battle_turn > 7; time loss")
            return True
        return False

    def _end_battle(self):
        """Determine the winner, set up summoning or reinforcing if
        possible, remove the dead legion(s), award points, and heal surviving
        creatures in the winning legion.
        """
        logging.info("_end_battle")
        if not self.attacker_legion or not self.defender_legion:
            return
        # XXX Redundant but fixes timing issues with _cleanup_battle
        self.defender_chose_not_to_flee = False
        if self.battle_turn > 7:
            # defender wins on time loss, possible reinforcement
            if self.defender_legion and self.defender_legion.can_recruit:
                self.pending_reinforcement = True
            self.attacker_legion.die(self.defender_legion, False, True,
              kill_all_creatures=True)
        elif (self.attacker_legion and self.attacker_legion.dead and
          self.defender_legion and self.defender_legion.dead):
            # Don't check for victory until both legions are dead,
            # to avoid prematurely declaring a victory in a mutual.
            # But make sure that if there's a titan in only one legion, it
            # dies last, so we do check for victory.
            if self.attacker_legion.has_titan:
                self.defender_legion.die(self.attacker_legion, False, True,
                  False)
                self.attacker_legion.die(self.defender_legion, False, True)
            else:
                self.attacker_legion.die(self.defender_legion, False, True,
                  False)
                self.defender_legion.die(self.attacker_legion, False, True)
        elif self.attacker_legion and self.attacker_legion.dead:
            # defender wins, possible reinforcement
            if (self.defender_legion and self.attacker_entered and
              self.defender_legion.can_recruit):
                logging.info("setting pending_reinforcement = True")
                self.pending_reinforcement = True
            self.attacker_legion.die(self.defender_legion, False, False)
        elif self.defender_legion and self.defender_legion.dead:
            # attacker wins, possible summon
            if self.attacker_legion and self.attacker_legion.can_summon:
                logging.info("setting pending_summon = True")
                self.pending_summon = True
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
                    creature.hexlabel = None
                for creature_name in creature_names_to_remove:
                    legion.remove_creature_by_name(creature_name)
                    self.caretaker.kill_one(creature_name)
        if (not self.pending_summon and not self.pending_reinforcement and not
          self.pending_acquire):
            self._cleanup_battle()
        reactor.callLater(1, self._end_dead_player_turn)

    def _end_dead_player_turn(self):
        """If the active player is dead then advance phases if possible."""
        if self.master:
            if (self.active_player.dead and not self.pending_acquire and not
              self.pending_summon and not self.pending_reinforcement):
                logging.info("_end_dead_player_turn")
                if self.phase == Phase.SPLIT:
                    self.active_player.done_with_splits()
                if self.phase == Phase.MOVE:
                    self.active_player.done_with_moves()
                if self.phase == Phase.FIGHT:
                    self.active_player.done_with_engagements()
                if self.phase == Phase.MUSTER:
                    self.active_player.done_with_recruits()

    def done_with_counterstrikes(self, playername):
        """Try to end playername's counterstrike battle phase.

        Called from Server.
        """
        logging.info("done_with_counterstrikes %s", playername)
        player = self.get_player_by_name(playername)
        if player is not self.battle_active_player:
            logging.info("ending counterstrike phase out of turn")
            return
        if self.battle_phase != Phase.COUNTERSTRIKE:
            logging.info("ending counterstrike phase out of phase")
            return
        if (not self.is_battle_over and
          self.battle_active_legion == self.defender_legion):
            self.battle_turn += 1
            logging.info("bumped battle turn to %s", self.battle_turn)
        if self.is_battle_over:
            logging.info("battle over")
            time_loss = self.battle_turn > 7
            logging.info("time_loss is %s", time_loss)
            # If it's a draw, arbitrarily call the defender the "winner"
            if time_loss or self.attacker_legion.dead:
                winner = self.defender_legion
            else:
                winner = self.attacker_legion
            loser = self.other_battle_legion(winner)
            mutual = self.attacker_legion.dead and self.defender_legion.dead
            logging.info("winner %s loser %s mutual %s", winner, loser, mutual)
            action = Action.BattleOver(self.name, winner.markerid,
              winner.living_creature_names, winner.dead_creature_names,
              loser.markerid, loser.living_creature_names,
              loser.dead_creature_names, time_loss,
              self.current_engagement_hexlabel, mutual)
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
        logging.info("cleanup_offboard_creatures")
        for legion in self.battle_legions:
            if legion != self.battle_active_legion:
                for creature in legion.creatures:
                    if not creature.dead:
                        if creature.hexlabel:
                            hex1 = self.battlemap.hexes[creature.hexlabel]
                            if hex1.entrance:
                                # We call this at the beginning of the turn, so
                                # it will actually be turn 2 if the attacker
                                # left creatures offboard in turn 1.
                                if self.battle_turn <= 2:
                                    creature.kill()
                                elif legion == self.attacker_legion:
                                    legion.player.unsummon_angel(legion,
                                      creature.name)
                                else:
                                    legion.unreinforce()
                        else:
                            logging.info("%s has hexlabel None", creature)

    def cleanup_dead_creatures(self):
        logging.info("cleanup_dead_creatures")
        for legion in self.battle_legions:
            for creature in legion.creatures:
                if creature.dead:
                    if (self.first_attacker_kill is None
                      and creature.legion is self.defender_legion
                      and creature.hexlabel != "DEFENDER"
                      and creature.hexlabel is not None):
                        self.first_attacker_kill = self.battle_turn
                        logging.info("first_attacker_kill %s",
                          self.battle_turn)
                    creature.previous_hexlabel = creature.hexlabel
                    creature.hexlabel = None

    def withdraw(self, playername):
        """Withdraw playername from this game.

        Called from Server.
        """
        player = self.get_player_by_name(playername)
        if player is None:
            return
        if player.dead:
            return
        if self.over:
            return
        # First concede the current battle if applicable.
        for legion in self.battle_legions:
            if legion.player.name == playername:
                self.concede(playername, legion.markerid)
        player.withdraw()

    def pause_ai(self, playername):
        action = Action.PauseAI(self.name, playername)
        self.notify(action)

    def resume_ai(self, playername):
        action = Action.ResumeAI(self.name, playername)
        self.notify(action)

    def _update_finish_order(self, winner_player, loser_player):
        logging.info("%s %s %s", winner_player, loser_player,
          self.finish_order)
        # If loser player is already in finish_order, abort.
        if self.finish_order and loser_player in self.finish_order[0]:
            logging.info("")
            # Avoid inserting duplicates.
            pass
        elif (len(self.finish_order) >= 2 and winner_player in
          self.finish_order[0] and loser_player in self.finish_order[1]):
            logging.info("")
            # Avoid inserting duplicates.
            pass
        elif winner_player is None:
            # Just one player died, so no tie.
            logging.info("")
            self.finish_order.insert(0, (loser_player, ))
        elif self.finish_order and winner_player in self.finish_order[0]:
            # Mutual titan kill, so tie.
            logging.info("")
            self.finish_order[0] = (loser_player, winner_player)
        elif self.over and winner_player.dead:
            # Mutual titan kill, so tie
            logging.info("")
            self.finish_order.insert(0, (winner_player, loser_player))
        elif self.over:
            # Game over so insert both the winner and the loser.
            logging.info("")
            self.finish_order.insert(0, (loser_player, ))
            self.finish_order.insert(0, (winner_player, ))
        else:
            # Just one player died, so no tie.
            logging.info("")
            self.finish_order.insert(0, (loser_player, ))

    def _cleanup_dead_players(self, winner_names):
        """Eliminate all non-winning players.

        This is called when we get the GameOver action, in case we missed
        any EliminatePlayer actions, so the game shows up as finished
        in the Lobby.
        """
        for player in self.players:
            if player.name not in winner_names:
                if not player.dead:
                    logging.info(player)
                    player.die(None, False)
        # Also eliminate the winning players, if there was a draw.
        if len(winner_names) == 2:
            winning_players = [self.get_player_by_name(playername)
              for playername in winner_names]
            player0 = winning_players[0]
            player1 = winning_players[1]
            if player0 and player1:
                if not player0.dead:
                    player0.die(player1, False)
                if not player1.dead:
                    player1.die(player0, False)

    def update(self, observed, action, names):
        if hasattr(action, "game_name") and action.game_name != self.name:
            return
        logging.info("%s %s", observed, action)

        if isinstance(action, Action.JoinGame):
            if action.game_name == self.name:
                self.add_player(action.playername, action.player_class,
                  action.player_info)

        elif isinstance(action, Action.AssignTower):
            self.started = True
            player = self.get_player_by_name(action.playername)
            if player.starting_tower is None:
                player.assign_starting_tower(action.tower_num)
            else:
                logging.info("player %s already has tower %s" % (player,
                  player.starting_tower))

        elif isinstance(action, Action.AssignedAllTowers):
            self.start_time = time.time()
            self.sort_players()

        elif isinstance(action, Action.PickedColor):
            self.assign_color(action.playername, action.color)

        elif isinstance(action, Action.CreateStartingLegion):
            player = self.get_player_by_name(action.playername)
            player.created_starting_legion = True
            # Avoid doing twice
            if not player.markerid_to_legion:
                player.pick_marker(action.markerid)
                player.create_starting_legion()

        elif isinstance(action, Action.SplitLegion):
            if action.game_name == self.name:
                player = self.get_player_by_name(action.playername)
                # Avoid doing the same split twice.
                if action.child_markerid not in player.markerid_to_legion:
                    self.split_legion(action.playername,
                      action.parent_markerid, action.child_markerid,
                      action.parent_creature_names,
                      action.child_creature_names)

        elif isinstance(action, Action.UndoSplit):
            player = self.get_player_by_name(action.playername)
            # Avoid undoing the same split twice.
            if action.child_markerid in player.markerid_to_legion:
                self.undo_split(action.playername, action.parent_markerid,
                  action.child_markerid)

        elif isinstance(action, Action.RollMovement):
            player = self.get_player_by_name(action.playername)
            self.phase = Phase.MOVE
            # Possibly redundant, but harmless
            player.movement_roll = action.movement_roll
            player.mulligans_left = action.mulligans_left
            for player in self.players:
                # Reset recruited again, in case the player reinforced late.
                player.clear_recruited()

        elif isinstance(action, Action.MoveLegion):
            if action.game_name == self.name:
                player = self.get_player_by_name(action.playername)
                markerid = action.markerid
                legion = player.markerid_to_legion.get(markerid)
                if legion is None:
                    return
                hexlabel = action.hexlabel
                # Avoid double move
                if not (legion.moved and legion.hexlabel == hexlabel):
                    self.move_legion(action.playername, markerid,
                      action.hexlabel, action.entry_side, action.teleport,
                      action.teleporting_lord)

        elif isinstance(action, Action.UndoMoveLegion):
            if action.game_name == self.name:
                player = self.get_player_by_name(action.playername)
                markerid = action.markerid
                legion = player.markerid_to_legion.get(markerid)
                if legion is None:
                    return
                # Avoid double undo
                if legion.moved:
                    self.undo_move_legion(action.playername, markerid)

        elif isinstance(action, Action.StartFightPhase):
            self.phase = Phase.FIGHT
            self._cleanup_battle()
            for player in self.players:
                player.reset_angels_pending()

        elif isinstance(action, Action.ResolvingEngagement):
            logging.info("ResolvingEngagement; reset_angels_pending")
            self._cleanup_battle()
            for player in self.players:
                player.reset_angels_pending()

        elif isinstance(action, Action.RevealLegion):
            legion = self.find_legion(action.markerid)
            if legion:
                legion.reveal_creatures(action.creature_names)

        elif isinstance(action, Action.Flee):
            legion = self.find_legion(action.markerid)
            if legion:
                playername = legion.player.name
                self._flee(playername, action.markerid)

        elif isinstance(action, Action.DoNotFlee):
            legion = self.find_legion(action.markerid)
            if legion:
                playername = legion.player.name
                self._do_not_flee(playername, action.markerid)

        elif isinstance(action, Action.Concede):
            legion = self.find_legion(action.markerid)
            if legion is not None:
                playername = legion.player.name
                self._concede(playername, action.markerid)

        elif isinstance(action, Action.AcceptProposal):
            attacker_legion = self.find_legion(action.attacker_markerid)
            defender_legion = self.find_legion(action.defender_markerid)
            if attacker_legion and defender_legion:
                self._accept_proposal(attacker_legion,
                  action.attacker_creature_names, defender_legion,
                  action.defender_creature_names)

        elif isinstance(action, Action.StartMusterPhase):
            self.phase = Phase.MUSTER
            for player in self.players:
                player.remove_empty_legions()

        elif isinstance(action, Action.RecruitCreature):
            self.recruit_creature(action.playername, action.markerid,
              action.creature_name, action.recruiter_names)

        elif isinstance(action, Action.UndoRecruit):
            self.undo_recruit(action.playername, action.markerid)

        elif isinstance(action, Action.DoNotReinforce):
            self._do_not_reinforce(action.playername, action.markerid)

        elif isinstance(action, Action.UnReinforce):
            self._unreinforce(action.playername, action.markerid)

        elif isinstance(action, Action.StartSplitPhase):
            self.turn = action.turn
            self.phase = Phase.SPLIT
            self.active_player = self.get_player_by_name(action.playername)
            for player in self.players:
                player.new_turn()

        elif isinstance(action, Action.SummonAngel):
            self.summon_angel(action.playername, action.markerid,
              action.donor_markerid, action.creature_name)

        elif isinstance(action, Action.UnsummonAngel):
            player = self.get_player_by_name(action.playername)
            legion = player.markerid_to_legion.get(action.markerid)
            if legion is None:
                return
            player.unsummon_angel(legion, action.creature_name)

        elif isinstance(action, Action.DoNotSummonAngel):
            self._do_not_summon_angel(action.playername, action.markerid)

        elif isinstance(action, Action.Fight):
            if action.game_name == self.name:
                attacker_markerid = action.attacker_markerid
                attacker = self.find_legion(attacker_markerid)
                if attacker is not None:
                    defender_markerid = action.defender_markerid
                    self._fight(attacker.player.name, attacker_markerid,
                      defender_markerid)

        elif isinstance(action, Action.MoveCreature):
            if not self.battle_active_legion:
                return
            creature = self.battle_active_legion.find_creature(
              action.creature_name, action.old_hexlabel)
            if creature is None:
                raise AssertionError("no %s in %s" % (action.creature_name,
                  action.old_hexlabel))
            creature.move(action.new_hexlabel)

        elif isinstance(action, Action.UndoMoveCreature):
            creature = self.battle_active_legion.find_creature(
              action.creature_name, action.new_hexlabel)
            if creature is None:
                raise AssertionError("no %s in %s" % (action.creature_name,
                  action.old_hexlabel))
            # Avoid double undo
            if creature.moved:
                creature.undo_move()

        elif isinstance(action, Action.StartManeuverBattlePhase):
            self.battle_phase = Phase.MANEUVER

        elif isinstance(action, Action.StartStrikeBattlePhase):
            if (not self.attacker_entered and self.attacker_legion and
              self.battle_active_legion == self.attacker_legion):
                for creature in self.attacker_legion.creatures:
                    if not creature.dead and creature.hexlabel != "ATTACKER":
                        self.attacker_entered = True
                        break
            self.battle_phase = Phase.DRIFTDAMAGE
            self.apply_drift_damage()
            self.battle_phase = Phase.STRIKE

        elif isinstance(action, Action.Strike):
            creatures = self.creatures_in_battle_hex(action.target_hexlabel)
            if creatures:
                target = creatures.pop()
                target.hits += action.hits
                target.hits = min(target.hits, target.power)
                if target.is_titan and target.dead:
                    target.legion.player.has_titan = False
                strikers = self.creatures_in_battle_hex(
                  action.striker_hexlabel)
                if strikers:
                    striker = strikers.pop()
                    striker.struck = True
                else:
                    logging.info("no strikers in %s", action.striker_hexlabel)
                    raise AssertionError("no strikers in %s" %
                      action.striker_hexlabel)
                if action.carries:
                    self.pending_carry = action
                else:
                    self.pending_carry = None

        elif isinstance(action, Action.DriftDamage):
            target = self.creatures_in_battle_hex(action.target_hexlabel).pop()
            target.hits += action.hits
            target.hits = min(target.hits, target.power)

        elif isinstance(action, Action.Carry):
            creatures = self.creatures_in_battle_hex(
              action.carry_target_hexlabel)
            if creatures:
                carry_target = creatures.pop()
                carry_target.hits += action.carries
                carry_target.hits = min(carry_target.hits, carry_target.power)
                if action.carries_left:
                    self.pending_carry = action
                else:
                    self.pending_carry = None

        elif isinstance(action, Action.StartCounterstrikeBattlePhase):
            self.battle_phase = Phase.COUNTERSTRIKE
            # Switch active players before the counterstrike phase.
            if self.defender_legion and self.attacker_legion:
                if action.playername == self.defender_legion.player.name:
                    self.battle_active_legion = self.defender_legion
                else:
                    self.battle_active_legion = self.attacker_legion
            else:
                logging.info("missing defender_legion or attacker_legion")

        elif isinstance(action, Action.StartReinforceBattlePhase):
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

        elif isinstance(action, Action.AcquireAngels):
            player = self.get_player_by_name(action.playername)
            legion = player.markerid_to_legion.get(action.markerid)
            if legion is None:
                return
            angels = [Creature.Creature(name) for name in action.angel_names]
            legion.acquire_angels(angels)
            reactor.callLater(1, self._end_dead_player_turn)

        elif isinstance(action, Action.DoNotAcquireAngels):
            player = self.get_player_by_name(action.playername)
            legion = player.markerid_to_legion.get(action.markerid)
            if legion is None:
                return
            legion.do_not_acquire_angels()
            reactor.callLater(1, self._end_dead_player_turn)

        elif isinstance(action, Action.EliminatePlayer):
            winner_player = self.get_player_by_name(action.winner_playername)
            loser_player = self.get_player_by_name(action.loser_playername)
            logging.info("%s eliminated by %s", loser_player, winner_player)
            player_to_full_points = defaultdict(int)
            for legion in loser_player.legions:
                if legion.engaged:
                    player = loser_player.enemy_legions(
                      legion.hexlabel).pop().player
                else:
                    player = winner_player
                player_to_full_points[player] += legion.living_creatures_score
            for player, full_points in player_to_full_points.iteritems():
                if player is not None:
                    half_points = full_points // 2
                    player.add_points(half_points)
            loser_player.remove_all_legions()
            # This will make the player dead even if we missed earlier actions.
            loser_player.created_starting_legion = True
            logging.info(loser_player.dead)
            if winner_player:
                winner_player.eliminated_colors.add(loser_player.color_abbrev)
                winner_player.markerids_left.update(
                  loser_player.markerids_left)
            self._update_finish_order(winner_player, loser_player)
            if action.check_for_victory:
                self.check_for_victory()
            reactor.callLater(1, self._end_dead_player_turn)

        elif isinstance(action, Action.GameOver):
            self.finish_time = action.finish_time
            reactor.callLater(1, self._cleanup_dead_players,
              action.winner_names)

        elif isinstance(action, Action.Withdraw):
            if action.game_name == self.name:
                if not self.started:
                    self.remove_player(action.playername)
                else:
                    player = self.get_player_by_name(action.playername)
                    player.die(None, True)
                    self._end_dead_player_turn()

        self.notify(action, names)
