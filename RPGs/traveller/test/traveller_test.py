"""Contains tests for the traveller module."""
import unittest
from src.coordinate import Coordinate
from src.financials import Credits
from src.star_map import StarSystemFactory
from traveller import Game

# most of these methods necessarily have side effects,
# so we're going to have to tease out the testable bits
# and/or monkeypatch/mock
class GameTestCase(unittest.TestCase):
    """Tests game logic."""

    def test_game_ctor(self) -> None:
        """Tests construction of a Game object."""
        game = Game()
        self.assertEqual(game.location,
                         StarSystemFactory.create("Yorbund", Coordinate(0,0,0),
                                                  "A", 8, 7, 5, 9, 5, 5, 10))
        self.assertEqual(game.financials.balance, Credits(10000000))

    @unittest.skip("test has side effects: input & printing")
    def test_get_input(self) -> None:
        """Test requesting input from the controller."""
        game = Game()

        result2 = game.get_input('', "No constraint test.")

        result2 = game.get_input('confirm', "Confirmation test.")
        self.assertTrue(result2 in ['y', 'n'])

        result3 = game.get_input('int', "Integer input test.")
        self.assertTrue(isinstance(result3, int))

    # side effects only ~ ~ ~ ~ ~ ~ ~
    # on_notify
    # run
