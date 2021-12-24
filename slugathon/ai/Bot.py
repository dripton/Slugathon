from zope.interface import Interface

from slugathon.game import Game, Player

__copyright__ = "Copyright (c) 2010-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Interface for the AI."""


class Bot(Interface):
    def player_info() -> str:
        """Return a string with information for result-tracking purposes."""

    def maybe_pick_color(game: Game.Game) -> None:
        """Pick a color if it's my turn."""

    def maybe_pick_first_marker(game: Game.Game, playername: str) -> None:
        """Pick my first legion marker if I know my color."""

    def choose_marker(player: Player.Player) -> str:
        """Choose a legion marker."""

    def split(game: Game.Game) -> None:
        """Split if it's my turn."""

    def move_legions(game: Game.Game) -> None:
        """Try to move legions."""

    def choose_engagement(game: Game.Game) -> None:
        """Pick an engagement to resolve next."""

    def resolve_engagement(game: Game.Game, hexlabel: int) -> None:
        """Resolve the engagement in hexlabel."""

    def move_creatures(game: Game.Game) -> None:
        """Move creatures in battle."""

    def strike(game: Game.Game) -> None:
        """Choose strikes or strikebacks."""

    def carry(
        game: Game.Game,
        striker_name: str,
        striker_hexlabel: str,
        target_name: str,
        target_hexlabel: str,
        num_dice: int,
        strike_number: int,
        carries: int,
    ) -> None:
        """Choose how to apply one carry."""

    def recruit(game: Game.Game) -> None:
        """Recruit during the Muster phase."""

    def reinforce(game: Game.Game) -> None:
        """Muster a reinforcement during or after battle."""

    def summon_angel(game: Game.Game) -> None:
        """Summon angel, during or after battle."""

    def acquire_angels(
        game: Game.Game, markerid: str, num_angels: int, num_archangels: int
    ) -> None:
        """Acquire angels."""
