#!/usr/bin/env python3


from typing import List, Optional, Union

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk
from zope.interface import implementer

from slugathon.game import Action, Game, Phase
from slugathon.util import colors
from slugathon.util.Observed import IObserved, IObserver


__copyright__ = "Copyright (c) 2006-2021 David Ripton"
__license__ = "GNU GPL v2"


def add_label(
    table: Gtk.Table, col: int, row: int, gtkcolor: Gdk.Color, text: str = ""
) -> Gtk.Label:
    """Add a label inside an eventbox to the table."""
    label = Gtk.Label(label=text)
    eventbox = Gtk.EventBox()
    eventbox.add(label)
    eventbox.modify_bg(Gtk.StateType.NORMAL, gtkcolor)
    label.eventbox = eventbox
    table.attach(eventbox, col, col + 1, row, row + 1)
    return label


def set_bg(label: Gtk.Label, color: Union[str, Gdk.Color]) -> None:
    if color:
        if isinstance(color, str):
            gtkcolor = Gdk.color_parse(color)
        else:
            gtkcolor = color
        label.eventbox.modify_bg(Gtk.StateType.NORMAL, gtkcolor)


@implementer(IObserver)
class StatusScreen(Gtk.EventBox):

    """Game status window."""

    def __init__(self, game: Game.Game, playername: str):
        GObject.GObject.__init__(self)
        self.game = game
        self.playername = playername

        self.vbox = Gtk.VBox()
        self.add(self.vbox)

        turn_table = Gtk.Table(n_rows=4, n_columns=3)
        self.vbox.pack_start(turn_table, True, True, 0)

        self.default_bg = Gdk.color_parse("lightgray")

        add_label(turn_table, 2, 1, self.default_bg, "Game")
        add_label(turn_table, 3, 1, self.default_bg, "Battle")
        add_label(turn_table, 1, 2, self.default_bg, "Turn")
        add_label(turn_table, 1, 3, self.default_bg, "Player")
        add_label(turn_table, 1, 4, self.default_bg, "Phase")
        self.game_turn_label = add_label(turn_table, 2, 2, self.default_bg)
        self.battle_turn_label = add_label(turn_table, 3, 2, self.default_bg)
        self.game_player_label = add_label(turn_table, 2, 3, self.default_bg)
        self.battle_player_label = add_label(turn_table, 3, 3, self.default_bg)
        self.game_phase_label = add_label(turn_table, 2, 4, self.default_bg)
        self.battle_phase_label = add_label(turn_table, 3, 4, self.default_bg)

        hseparator1 = Gtk.HSeparator()
        self.vbox.pack_start(hseparator1, True, True, 0)
        self.player_table = Gtk.Table(
            n_rows=9, n_columns=len(self.game.players) + 1
        )
        self.vbox.pack_start(self.player_table, True, True, 0)

        for row, text in enumerate(
            [
                "Name",
                "Tower",
                "Color",
                "Legions",
                "Markers",
                "Creatures",
                "Titan Power",
                "Eliminated",
                "Score",
            ]
        ):
            add_label(self.player_table, 1, row, self.default_bg, text)

        for col in range(len(self.game.players)):
            for row, st in enumerate(
                [
                    "name%d_label",
                    "tower%d_label",
                    "color%d_label",
                    "legions%d_label",
                    "markers%d_label",
                    "creatures%d_label",
                    "titan_power%d_label",
                    "eliminated%d_label",
                    "score%d_label",
                ]
            ):
                name = st % col
                label = add_label(
                    self.player_table, col + 2, row, self.default_bg
                )
                setattr(self, name, label)

        self.modify_bg(Gtk.StateType.NORMAL, self.default_bg)
        self._init_players()
        self._init_turn()

        self.show_all()

    def _init_turn(self) -> None:
        self.game_turn_label.set_text(str(self.game.turn))
        self.game_phase_label.set_text(Phase.phase_names[self.game.phase])
        if self.game.active_player:
            if self.game.active_player.name == self.playername:
                set_bg(self.game_player_label, "Yellow")
            else:
                set_bg(self.game_player_label, self.default_bg)
            self.game_player_label.set_text(self.game.active_player.name)
        self._clear_battle()
        self._color_player_columns()

    def _color_player_columns(self) -> None:
        for num, player in enumerate(self.game.players):
            bg = self.default_bg
            if (
                self.game.active_player is not None
                and player.name == self.game.active_player.name
            ):
                bg = "Yellow"
            elif player.dead:
                bg = "Red"
            playercolor = self.default_bg
            if player.color is not None:
                playercolor = player.color
            name_label = getattr(self, "name%d_label" % num)
            set_bg(name_label, playercolor)
            tower_label = getattr(self, "tower%d_label" % num)
            set_bg(tower_label, bg)
            color_label = getattr(self, "color%d_label" % num)
            set_bg(color_label, bg)
            legions_label = getattr(self, "legions%d_label" % num)
            set_bg(legions_label, bg)
            markers_label = getattr(self, "markers%d_label" % num)
            set_bg(markers_label, bg)
            creatures_label = getattr(self, "creatures%d_label" % num)
            set_bg(creatures_label, bg)
            titan_power_label = getattr(self, "titan_power%d_label" % num)
            set_bg(titan_power_label, bg)
            eliminated_label = getattr(self, "eliminated%d_label" % num)
            set_bg(eliminated_label, bg)
            score_label = getattr(self, "score%d_label" % num)
            set_bg(score_label, bg)

    def _init_players(self) -> None:
        for num, player in enumerate(self.game.players):
            bg = self.default_bg
            if (
                self.game.active_player is not None
                and player.name == self.game.active_player.name
            ):
                bg = "Yellow"
            elif player.dead:
                bg = "Red"
            playercolor = self.default_bg
            try:
                if player.color is not None:
                    playercolor = player.color
            except AttributeError:
                pass
            name_label = getattr(self, "name%d_label" % num)
            set_bg(name_label, playercolor)
            name_label.set_markup(
                "<span foreground='%s'>%s</span>"
                % (
                    colors.contrasting_colors.get(str(playercolor), "Black"),
                    player.name,
                )
            )
            tower_label = getattr(self, "tower%d_label" % num)
            tower_label.set_text(str(player.starting_tower))
            set_bg(tower_label, bg)
            color_label = getattr(self, "color%d_label" % num)
            color_label.set_text(str(player.color or ""))
            set_bg(color_label, bg)
            legions_label = getattr(self, "legions%d_label" % num)
            legions_label.set_text(str(len(player.markerid_to_legion)))
            set_bg(legions_label, bg)
            markers_label = getattr(self, "markers%d_label" % num)
            markers_label.set_text(str(len(player.markerids_left)))
            set_bg(markers_label, bg)
            creatures_label = getattr(self, "creatures%d_label" % num)
            creatures_label.set_text(str(player.num_creatures))
            set_bg(creatures_label, bg)
            titan_power_label = getattr(self, "titan_power%d_label" % num)
            titan_power_label.set_text(str(player.titan_power))
            set_bg(titan_power_label, bg)
            eliminated_label = getattr(self, "eliminated%d_label" % num)
            eliminated_label.set_text(
                "".join(sorted(player.eliminated_colors))
            )
            set_bg(eliminated_label, bg)
            score_label = getattr(self, "score%d_label" % num)
            score_label.set_text(str(player.score))
            set_bg(score_label, bg)

    def _init_battle(self) -> None:
        if (
            self.game.battle_turn is not None
            and self.game.battle_active_player is not None
        ):
            self.battle_turn_label.set_text(str(self.game.battle_turn))
            if self.game.battle_active_player.name == self.playername:
                set_bg(self.battle_player_label, "Yellow")
            else:
                set_bg(self.battle_player_label, self.default_bg)
            self.battle_player_label.set_text(
                self.game.battle_active_player.name
            )
            assert self.game.battle_phase is not None
            self.battle_phase_label.set_text(
                Phase.battle_phase_names[self.game.battle_phase]
            )
        else:
            self._clear_battle()

    def _clear_battle(self) -> None:
        self.battle_turn_label.set_text("")
        set_bg(self.battle_player_label, self.default_bg)
        self.battle_player_label.set_text("")
        self.battle_phase_label.set_text("")

    def update(
        self,
        observed: Optional[IObserved],
        action: Action.Action,
        names: List[str] = None,
    ) -> None:
        if isinstance(action, Action.AssignedAllTowers):
            # Players got renumbered, so re-init everything.
            self._init_players()
            self._init_turn()

        elif isinstance(action, Action.PickedColor):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            assert player is not None
            player_num = self.game.players.index(player)
            color = action.color
            color_label = getattr(self, "color%d_label" % player_num)
            color_label.set_text(color)
            name_label = getattr(self, "name%d_label" % player_num)
            set_bg(name_label, color)
            name_label.set_markup(
                "<span foreground='%s'>%s</span>"
                % (
                    colors.contrasting_colors.get(str(color), "Black"),
                    player.name,
                )
            )

        elif isinstance(action, Action.AssignedAllColors):
            self._init_turn()

        elif isinstance(action, Action.CreateStartingLegion):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            assert player is not None
            player_num = self.game.players.index(player)
            legions_label = getattr(self, "legions%d_label" % player_num)
            legions_label.set_text(str(len(player.markerid_to_legion)))
            creatures_label = getattr(self, "creatures%d_label" % player_num)
            creatures_label.set_text(str(player.num_creatures))
            markers_label = getattr(self, "markers%d_label" % player_num)
            markers_label.set_text(str(len(player.markerids_left)))

        elif (
            isinstance(action, Action.SplitLegion)
            or isinstance(action, Action.UndoSplit)
            or isinstance(action, Action.MergeLegions)
        ):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            assert player is not None
            player_num = self.game.players.index(player)
            legions_label = getattr(self, "legions%d_label" % player_num)
            legions_label.set_text(str(len(player.markerid_to_legion)))
            markers_label = getattr(self, "markers%d_label" % player_num)
            markers_label.set_text(str(len(player.markerids_left)))

        elif isinstance(action, Action.RollMovement):
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])

        elif isinstance(action, Action.StartFightPhase):
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])

        elif isinstance(action, Action.StartMusterPhase):
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            assert player is not None
            player_num = self.game.players.index(player)
            legions_label = getattr(self, "legions%d_label" % player_num)
            legions_label.set_text(str(len(player.markerid_to_legion)))
            markers_label = getattr(self, "markers%d_label" % player_num)
            markers_label.set_text(str(len(player.markerids_left)))

        elif (
            isinstance(action, Action.RecruitCreature)
            or isinstance(action, Action.UndoRecruit)
            or isinstance(action, Action.UnReinforce)
            or isinstance(action, Action.AcquireAngels)
        ):
            playername = action.playername
            player = self.game.get_player_by_name(playername)
            assert player is not None
            player_num = self.game.players.index(player)
            creatures_label = getattr(self, "creatures%d_label" % player_num)
            creatures_label.set_text(str(player.num_creatures))

        elif isinstance(action, Action.StartSplitPhase):
            self._init_turn()

        elif (
            isinstance(action, Action.Flee)
            or isinstance(action, Action.Concede)
            or isinstance(action, Action.AcceptProposal)
            or isinstance(action, Action.EliminatePlayer)
            or isinstance(action, Action.BattleOver)
            or isinstance(action, Action.GameOver)
            or isinstance(action, Action.StartMusterPhase)
            or isinstance(action, Action.DoNotReinforce)
            or isinstance(action, Action.SummonAngel)
            or isinstance(action, Action.DoNotSummonAngel)
        ):
            self._clear_battle()
            self._color_player_columns()
            self.game_phase_label.set_text(Phase.phase_names[self.game.phase])
            for num, player in enumerate(self.game.players):
                legions_label = getattr(self, "legions%d_label" % num)
                legions_label.set_text(str(len(player.markerid_to_legion)))
                markers_label = getattr(self, "markers%d_label" % num)
                markers_label.set_text(str(len(player.markerids_left)))
                creatures_label = getattr(self, "creatures%d_label" % num)
                creatures_label.set_text(str(player.num_creatures))
                titan_power_label = getattr(self, "titan_power%d_label" % num)
                titan_power_label.set_text(str(player.titan_power))
                score_label = getattr(self, "score%d_label" % num)
                score_label.set_text(str(player.score))
                eliminated_label = getattr(self, "eliminated%d_label" % num)
                eliminated_label.set_text("".join(player.eliminated_colors))

        elif (
            isinstance(action, Action.Fight)
            or isinstance(action, Action.StartManeuverBattlePhase)
            or isinstance(action, Action.StartStrikeBattlePhase)
            or isinstance(action, Action.StartCounterstrikeBattlePhase)
            or isinstance(action, Action.StartReinforceBattlePhase)
        ):
            self._init_battle()


if __name__ == "__main__":
    import time
    from slugathon.util import guiutils
    from slugathon.game import Game, Player, Creature
    from slugathon.data import creaturedata

    now = time.time()
    playername = "p1"
    creatures = Creature.n2c(creaturedata.starting_creature_names)
    game = Game.Game("g1", "Player 1", now, now, 2, 6)

    player1 = game.players[0]
    player1.assign_starting_tower(600)
    player1.assign_color("Red")
    player1.pick_marker("Rd01")
    player1.create_starting_legion()
    game.active_player = player1

    player2 = Player.Player("Player 2", game, 1)
    player2.assign_starting_tower(500)
    player2.assign_color("Blue")
    player2.pick_marker("Bu02")
    player2.create_starting_legion()
    game.players.append(player2)

    player3 = Player.Player("Player 3", game, 2)
    player3.assign_starting_tower(400)
    player3.assign_color("Green")
    player3.pick_marker("Gr03")
    player3.create_starting_legion()
    game.players.append(player3)

    player4 = Player.Player("Player 4", game, 3)
    player4.assign_starting_tower(300)
    player4.assign_color("Brown")
    player4.pick_marker("Br04")
    player4.create_starting_legion()
    game.players.append(player4)

    player5 = Player.Player("Player 5", game, 4)
    player5.assign_starting_tower(200)
    player5.assign_color("Black")
    player5.pick_marker("Bk05")
    player5.create_starting_legion()
    game.players.append(player5)

    player6 = Player.Player("Player 6", game, 5)
    player6.assign_starting_tower(100)
    player6.assign_color("Gold")
    player6.pick_marker("Gd06")
    player6.create_starting_legion()
    game.players.append(player6)

    status_screen = StatusScreen(game, playername)
    status_screen.connect("destroy", guiutils.exit)
    window = Gtk.Window()
    window.add(status_screen)
    window.show_all()
    Gtk.main()
