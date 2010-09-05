__copyright__ = "Copyright (c) 2003-2010 David Ripton"
__license__ = "GNU GPL v2"

import time

from twisted.spread import pb
from zope.interface import implements

from slugathon.util.Observer import IObserver
from slugathon.game import Action
from slugathon.util.log import log


class User(pb.Avatar):
    """Perspective for a player or spectator."""

    implements(IObserver)

    def __init__(self, name, server, client):
        self.name = name
        self.server = server
        self.client = client
        self.server.add_observer(self)

    def attached(self, mind):
        pass

    def detached(self, mind):
        pass

    def perspective_get_name(self, arg):
        return self.name

    def perspective_get_usernames(self):
        return self.server.get_usernames()

    def perspective_get_games(self):
        games = self.server.get_games()
        return [game.to_info_tuple() for game in games]

    def perspective_send_chat_message(self, dest, text):
        """Send chat text to dest, a set of usernames.

        If dest is None, send to everyone.
        """
        self.server.send_chat_message(self.name, dest, text)

    def receive_chat_message(self, text):
        def1 = self.client.callRemote("receive_chat_message", text)
        def1.addErrback(self.failure)

    def perspective_form_game(self, game_name, min_players, max_players):
        self.server.form_game(self.name, game_name, min_players, max_players)

    def perspective_join_game(self, game_name):
        self.server.join_game(self.name, game_name)

    def perspective_drop_from_game(self, game_name):
        self.server.drop_from_game(self.name, game_name)

    def perspective_start_game(self, game_name):
        self.server.start_game(self.name, game_name)

    def perspective_pick_color(self, game_name, color):
        self.server.pick_color(self.name, game_name, color)

    def perspective_pick_first_marker(self, game_name, markername):
        self.server.pick_first_marker(self.name, game_name, markername)

    def perspective_split_legion(self, game_name, parent_markername,
      child_markername, parent_creature_names, child_creature_names):
        self.server.split_legion(self.name, game_name, parent_markername,
          child_markername, parent_creature_names, child_creature_names)

    def perspective_done_with_splits(self, game_name):
        self.server.done_with_splits(self.name, game_name)

    def perspective_take_mulligan(self, game_name):
        self.server.take_mulligan(self.name, game_name)

    def perspective_move_legion(self, game_name, markername, hexlabel,
      entry_side, teleport, teleporting_lord):
        self.server.move_legion(self.name, game_name, markername, hexlabel,
          entry_side, teleport, teleporting_lord)

    def perspective_done_with_moves(self, game_name):
        self.server.done_with_moves(self.name, game_name)

    def perspective_resolve_engagement(self, game_name, hexlabel):
        self.server.resolve_engagement(self.name, game_name, hexlabel)

    def perspective_flee(self, game_name, markername):
        self.server.flee(self.name, game_name, markername)

    def perspective_do_not_flee(self, game_name, markername):
        self.server.do_not_flee(self.name, game_name, markername)

    def perspective_concede(self, game_name, markername, enemy_markername,
      hexlabel):
        self.server.concede(self.name, game_name, markername,
          enemy_markername, hexlabel)

    def perspective_make_proposal(self, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        self.server.make_proposal(self.name, game_name, attacker_markername,
          attacker_creature_names, defender_markername,
          defender_creature_names)

    def perspective_accept_proposal(self, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        self.server.accept_proposal(self.name, game_name, attacker_markername,
          attacker_creature_names, defender_markername,
          defender_creature_names)

    def perspective_reject_proposal(self, game_name, attacker_markername,
      attacker_creature_names, defender_markername, defender_creature_names):
        self.server.reject_proposal(self.name, game_name, attacker_markername,
          attacker_creature_names, defender_markername,
          defender_creature_names)

    def perspective_fight(self, game_name, attacker_markername,
      defender_markername):
        self.server.fight(self.name, game_name, attacker_markername,
          defender_markername)

    def perspective_move_creature(self, game_name, creature_name,
      old_hexlabel, new_hexlabel):
        self.server.move_creature(self.name, game_name, creature_name,
          old_hexlabel, new_hexlabel)

    def perspective_done_with_reinforcements(self, game_name):
        self.server.done_with_reinforcements(self.name, game_name)

    def perspective_done_with_maneuvers(self, game_name):
        self.server.done_with_maneuvers(self.name, game_name)

    def perspective_done_with_strikes(self, game_name):
        self.server.done_with_strikes(self.name, game_name)

    def perspective_done_with_counterstrikes(self, game_name):
        self.server.done_with_counterstrikes(self.name, game_name)

    def perspective_strike(self, game_name, creature_name, hexlabel,
      target_creature_name, target_hexlabel, num_dice, strike_number):
        self.server.strike(self.name, game_name, creature_name, hexlabel,
          target_creature_name, target_hexlabel, num_dice, strike_number)

    def perspective_acquire_angels(self, game_name, markername,
      angel_names):
        self.server.acquire_angels(self.name, game_name, markername,
          angel_names)

    def perspective_do_not_acquire(self, game_name, markername):
        log("do_not_acquire", self, game_name, markername)
        self.server.do_not_acquire(self.name, game_name, markername)

    def perspective_done_with_engagements(self, game_name):
        self.server.done_with_engagements(self.name, game_name)

    def perspective_recruit_creature(self, game_name, markername,
      creature_name, recruiter_names):
        self.server.recruit_creature(self.name, game_name, markername,
          creature_name, recruiter_names)

    def perspective_done_with_recruits(self, game_name):
        self.server.done_with_recruits(self.name, game_name)

    def perspective_summon_angel(self, game_name, markername,
      donor_markername, creature_name):
        self.server.summon_angel(self.name, game_name, markername,
          donor_markername, creature_name)

    def perspective_do_not_summon(self, game_name, markername):
        self.server.do_not_summon(self.name, game_name, markername)

    def perspective_do_not_reinforce(self, game_name, markername):
        self.server.do_not_reinforce(self.name, game_name, markername)

    def perspective_carry(self, game_name, carry_target_name,
      carry_target_hexlabel, carries):
        log("perspective_carry", carry_target_name, carry_target_hexlabel,
          carries)
        self.server.carry(self.name, game_name, carry_target_name,
          carry_target_hexlabel, carries)

    def perspective_apply_action(self, action):
        """Pull the exact method and args out of the Action."""
        if isinstance(action, Action.UndoSplit):
            self.server.undo_split(self.name, action.game_name,
              action.parent_markername, action.child_markername)
        elif isinstance(action, Action.UndoMoveLegion):
            self.server.undo_move_legion(self.name, action.game_name,
              action.markername)
        elif isinstance(action, Action.UndoRecruit):
            self.server.undo_recruit(self.name, action.game_name,
              action.markername)
        elif isinstance(action, Action.UndoMoveCreature):
            self.server.undo_move_creature(self.name, action.game_name,
              action.creature_name, action.new_hexlabel)
        elif isinstance(action, Action.SplitLegion):
            self.server.split_legion(self.name, action.game_name,
              action.parent_markername, action.child_markername,
              action.parent_creature_names, action.child_creature_names)
        elif isinstance(action, Action.MoveLegion):
            self.server.move_legion(self.name, action.game_name,
              action.markername, action.hexlabel, action.entry_side,
              action.teleport, action.teleporting_lord)
        elif isinstance(action, Action.MoveCreature):
            self.server.move_creature(self.name, action.game_name,
              action.creature_name, action.old_hexlabel, action.new_hexlabel)
        elif isinstance(action, Action.RecruitCreature):
            self.server.recruit_creature(self.name, action.game_name,
              action.markername, action.creature_name, action.recruiter_names)

    def perspective_save(self, game_name):
        self.server.save(self.name, game_name)

    def __repr__(self):
        return "User " + self.name

    def add_observer(self, mind):
        def1 = self.client.callRemote("set_name", self.name)
        def1.addErrback(self.failure)
        def2 = self.client.callRemote("ping", time.time())
        def2.addErrback(self.failure)

    def failure(self, arg):
        log("failure", arg)

    def logout(self):
        self.server.remove_observer(self)

    def update(self, observed, action):
        """Defers updates to its client, dropping the observed reference."""
        if not isinstance(action, Action.DriftDamage):
            def1 = self.client.callRemote("update", action)
            def1.addErrback(self.failure)
