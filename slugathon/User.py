__copyright__ = "Copyright (c) 2003-2008 David Ripton"
__license__ = "GNU GPL v2"


from twisted.spread import pb
import time
from zope.interface import implements

from Observer import IObserver
import Action

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

    def perspective_send_chat_message(self, text):
        self.server.send_chat_message(self.name, None, text)

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

    def perspective_acquire_angel(self, game_name, markername,
      angel_name):
        self.server.acquire_angel(self.name, game_name, markername,
          angel_name)

    def perspective_done_with_engagements(self, game_name):
        self.server.done_with_engagements(self.name, game_name)

    def perspective_recruit_creature(self, game_name, markername,
      creature_name):
        self.server.recruit_creature(self.name, game_name, markername,
          creature_name)

    def perspective_done_with_recruits(self, game_name):
        self.server.done_with_recruits(self.name, game_name)

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
        elif isinstance(action, Action.DoneMoving):
            self.server.done_with_moves(self.name, action.game_name)
        elif isinstance(action, Action.MoveCreature):
            self.server.move_creature(self.name, action.game_name,
              action.creature_name, action.old_hexlabel, action.new_hexlabel)
        elif isinstance(action, Action.RecruitCreature):
            self.server.recruit_creature(self.name, action.game_name,
              action.markername, action.creature_name)
        elif isinstance(action, Action.DoneRecruiting):
            self.server.done_with_recruits(self.name, action.game_name)

    def perspective_save(self, game_name):
        self.server.save(self.name, game_name)

    def __repr__(self):
        return "User " + self.name

    def add_observer(self, mind):
        def1 = self.client.callRemote("set_name", self.name)
        def1.addCallback(self.did_set_name)
        def1.addErrback(self.failure)
        def2 = self.client.callRemote("ping", time.time())
        def2.addCallback(self.did_ping)
        def2.addErrback(self.failure)

    def did_set_name(self, arg):
        pass

    def success(self, arg):
        pass

    def failure(self, arg):
        print "User.failure", arg

    def did_ping(self, arg):
        pass

    def logout(self):
        self.server.remove_observer(self)

    def update(self, observed, action):
        """Defers updates to its client, dropping the observed reference."""
        # XXX Don't pass the AcquireAngels event from server to client
        if not isinstance(action, Action.AcquireAngels):
            def1 = self.client.callRemote("update", action)
            def1.addErrback(self.failure)
