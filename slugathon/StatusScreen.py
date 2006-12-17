#!/usr/bin/env python

import time

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import gtk.glade
import zope.interface

import icon
import guiutils
from Observer import IObserver
import Game
import Player
import creaturedata
import Legion
import Creature
import Action
import Phase


class StatusScreen(gtk.Window):
    """Game status window."""

    zope.interface.implements(IObserver)

    def __init__(self, game, user, username):
        gtk.Window.__init__(self)

        self.game = game
        self.user = user
        self.username = username
        self.glade = gtk.glade.XML("../glade/statusscreen.glade")
        self.widgets = ["status_screen_window", "turn_table", "player_table",
          "game_turn_label", "game_player_label", "game_phase_label",
          "battle_turn_label", "battle_player_label", "battle_phase_label",
        ]
        for num, player in enumerate(self.game.players):
            self.widgets.append("name%d_label" % num)
            self.widgets.append("tower%d_label" % num)
            self.widgets.append("color%d_label" % num)
            self.widgets.append("legions%d_label" % num)
            self.widgets.append("markers%d_label" % num)
            self.widgets.append("creatures%d_label" % num)
            self.widgets.append("titan_power%d_label" % num)
            self.widgets.append("eliminated%d_label" % num)
            self.widgets.append("score%d_label" % num)
        for widget_name in self.widgets:
            setattr(self, widget_name, self.glade.get_widget(widget_name))

        self._init_turn()
        self._init_players()

        self.status_screen_window.set_icon(icon.pixbuf)
        self.status_screen_window.set_title("%s - %s" % (
          self.status_screen_window.get_title(), self.username))
        self.status_screen_window.show()

    def _init_turn(self):
        self.game_turn_label.set_text(str(self.game.turn))
        self.game_phase_label.set_text(Phase.phase_names[self.game.phase])
        if self.game.active_player:
            self.game_player_label.set_text(self.game.active_player.name)

    def _init_players(self):
        for num, player in enumerate(self.game.players):
            name_label = getattr(self, "name%d_label" % num)
            name_label.set_text(player.name)
            tower_label = getattr(self, "tower%d_label" % num)
            tower_label.set_text(str(player.starting_tower))
            color_label = getattr(self, "color%d_label" % num)
            color_label.set_text(player.color or "")
            legions_label = getattr(self, "legions%d_label" % num)
            legions_label.set_text(str(len(player.legions)))
            markers_label = getattr(self, "markers%d_label" % num)
            markers_label.set_text(str(len(player.markernames)))
            creatures_label = getattr(self, "creatures%d_label" % num)
            creatures_label.set_text(str(player.num_creatures()))
            titan_power_label = getattr(self, "titan_power%d_label" % num)
            titan_power_label.set_text(str(player.titan_power()))
            eliminated_label = getattr(self, "eliminated%d_label" % num)
            eliminated_label.set_text("")
            score_label = getattr(self, "score%d_label" % num)
            score_label.set_text(str(player.score))

    def update(self, observed, action):
        print "StatusScreen.update", self, observed, action

        if isinstance(action, Action.AssignedAllTowers):
            # Players got renumbered, so re-init everything.
            self._init_players()
            self._init_turn()

        elif isinstance(action, Action.PickedColor):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            player_num = self.game.players.index(player)
            color = action.color
            color_label = getattr(self, "color%d_label" % player_num)
            color_label.set_text(color)

        elif isinstance(action, Action.CreateStartingLegion):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            player_num = self.game.players.index(player)
            legions_label = getattr(self, "legions%d_label" % player_num)
            legions_label.set_text(str(len(player.legions)))
            creatures_label = getattr(self, "creatures%d_label" % player_num)
            creatures_label.set_text(str(player.num_creatures()))
            markers_label = getattr(self, "markers%d_label" % player_num)
            markers_label.set_text(str(len(player.markernames)))

        elif (isinstance(action, Action.SplitLegion) or
          isinstance(action, Action.UndoSplit) or
          isinstance(action, Action.MergeLegions)):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            player_num = self.game.players.index(player)
            legions_label = getattr(self, "legions%d_label" % player_num)
            legions_label.set_text(str(len(player.legions)))
            markers_label = getattr(self, "markers%d_label" % player_num)
            markers_label.set_text(str(len(player.markernames)))

        elif isinstance(action, Action.RollMovement):
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])

        elif isinstance(action, Action.DoneMoving):
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])

        elif (isinstance(action, Action.RecruitCreature) or 
          isinstance(action, Action.UndoRecruit)):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            player_num = self.game.players.index(player)
            creatures_label = getattr(self, "creatures%d_label" % player_num)
            creatures_label.set_text(str(player.num_creatures()))

        elif isinstance(action, Action.DoneRecruiting):
            self._init_turn()

        elif (isinstance(action, Action.Flee) or 
          isinstance(action, Action.Concede)):
            for num, player in enumerate(self.game.players):
                legions_label = getattr(self, "legions%d_label" % num)
                legions_label.set_text(str(len(player.legions)))
                markers_label = getattr(self, "markers%d_label" % num)
                markers_label.set_text(str(len(player.markernames)))
                creatures_label = getattr(self, "creatures%d_label" % num)
                creatures_label.set_text(str(player.num_creatures()))
                titan_power_label = getattr(self, "titan_power%d_label" % num)
                titan_power_label.set_text(str(player.titan_power()))
                score_label = getattr(self, "score%d_label" % num)
                score_label.set_text(str(player.score))

        elif isinstance(action, Action.DoneFighting):
            self._init_turn()


if __name__ == "__main__":
    now = time.time()
    user = None
    username = "p0"
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    game = Game.Game("g1", "p0", now, now, 2, 6)
    player0 = Player.Player(username, game, 0)
    player0.assign_starting_tower(600)
    assert player0.starting_tower == 600
    player0.assign_color("Red")
    assert player0.color == "Red"
    player0.pick_marker("Rd01")
    player0.create_starting_legion()
    assert len(player0.legions) == 1

    status_screen = StatusScreen(game, user, username)
    status_screen.status_screen_window.connect("destroy", guiutils.die)
    gtk.main()

