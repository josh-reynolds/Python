"""Contains tests for the traveller module."""
import unittest
from main import Game
from src.menu import Menu

# most of these methods necessarily have side effects,
# so we're going to have to tease out the testable bits
# and/or monkeypatch/mock
class GameTestCase(unittest.TestCase):
    """Tests game logic."""

    def test_game_ctor(self) -> None:
        """Tests construction of a Game object."""
        game = Game()
        self.assertFalse(game.running)
        self.assertTrue(isinstance(game.screen, Menu))

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
