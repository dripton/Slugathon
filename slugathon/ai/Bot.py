__copyright__ = "Copyright (c) 2010-2012 David Ripton"
__license__ = "GNU GPL v2"


"""Interface for the AI."""


from zope.interface import Interface


class Bot(Interface):
    def player_info():
        """Return a string with information for result-tracking purposes."""

    def maybe_pick_color(game):
        """Pick a color if it's my turn."""

    def maybe_pick_first_marker(game, playername):
        """Pick my first legion marker if I know my color."""

    def choose_marker(player):
        """Choose a legion marker."""

    def split(game):
        """Split if it's my turn."""

    def move_legions(game):
        """Try to move legions."""

    def choose_engagement(game):
        """Pick an engagement to resolve next."""

    def resolve_engagement(game, hexlabel, did_not_flee):
        """Resolve the engagement in hexlabel."""

    def move_creatures(game):
        """Move creatures in battle."""

    def strike(game):
        """Choose strikes or strikebacks."""

    def carry(game, striker_name, striker_hexlabel, target_name,
              target_hexlabel, num_dice, strike_number, carries):
        """Choose how to apply one carry."""

    def recruit(game):
        """Recruit during the Muster phase."""

    def reinforce(game):
        """Muster a reinforcement during or after battle."""

    def summon_angel(game):
        """Summon angel, during or after battle."""

    def acquire_angels(game, markerid, num_angels, num_archangels):
        """Acquire angels."""
