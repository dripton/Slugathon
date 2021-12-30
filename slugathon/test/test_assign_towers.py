import time
from typing import Callable, Dict

from slugathon.game import Game

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


class TestAssignTowers(object):
    def setup_method(self, method: Callable) -> None:
        now = time.time()
        self.game = Game.Game("g1", "p1", now, now, 2, 6)

    def _simple_helper(self, num_players: int) -> None:
        for num in range(num_players - 1):
            self.game.add_player(f"p{(num + 2)}")
        self.game.assign_towers()
        towers = {player.starting_tower for player in self.game.players}
        assert len(towers) == num_players
        for tower in towers:
            assert tower in self.game.board.get_tower_labels()

    def test_1_player_simple(self) -> None:
        self._simple_helper(1)

    def test_6_player_simple(self) -> None:
        self._simple_helper(6)

    def _range_helper(self, num_players: int) -> None:
        trials = 50
        num_towers = 6
        counts = {}  # type: Dict[int, int]
        for num in range(num_players - 1):
            self.game.add_player(f"p{(num + 2)}")
        for unused in range(trials):
            self.game.assign_towers()
            towers = {player.starting_tower for player in self.game.players}
            assert len(towers) == num_players
            for tower in towers:
                counts[tower] = counts.get(tower, 0) + 1  # type: ignore
        assert len(counts) == num_towers, f"len(counts) is wrong: {counts=}"
        assert sum(counts.values()) == trials * num_players
        chi_square = 0.0
        mean = 1.0 * trials * num_players / num_towers
        for count in counts.values():
            chi_square += (count - mean) ** 2.0 / mean
        chi_square /= trials - 1
        # degrees of freedome = 5, 99.5% chance of randomness
        assert chi_square < 0.4117

    def test_1_player(self) -> None:
        self._range_helper(1)

    def test_2_player(self) -> None:
        self._range_helper(2)

    def test_3_player(self) -> None:
        self._range_helper(3)

    def test_4_player(self) -> None:
        self._range_helper(4)

    def test_5_player(self) -> None:
        self._range_helper(5)

    def test_6_player(self) -> None:
        self._range_helper(6)
