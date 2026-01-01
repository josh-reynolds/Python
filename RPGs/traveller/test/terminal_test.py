"""Contains tests for the terminal module."""
import unittest
from typing import cast, List
from test.mock import ControlsMock
from main import Game
from src.model import Model
from src.terminal import TerminalScreen
from src.star_system import StarSystem

class TerminalScreenTestCase(unittest.TestCase):
    """Test TerminalScreen class."""

    # TO_DO: should move to model_test module
    @unittest.skip("test has side effects: printing")
    def test_get_destinations(self) -> None:
        """Test getting list of passenger destinations."""
        game = Game()
        model = Model(ControlsMock([]))
        passengers = TerminalScreen(game, model)
        potential_destinations = cast(List[StarSystem],
                                      passengers.model.map_hex.destinations.copy())

        destinations = passengers.model.get_destinations(potential_destinations,
                                                    1, "passengers")
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # TO_DO: move to model_test
    @unittest.skip("test has side effects: printing & input")
    def test_select_passengers(self) -> None:
        """Test selection of passengers from a list."""
        game = Game()
        model = Model(ControlsMock([]))
        passengers = TerminalScreen(game, model)
        available = (5,5,5)
        destination = passengers.model.map_hex.destinations[0]

        selection = passengers.model.select_passengers(available, destination)
        print(selection)

        # no passengers remaining, auto-exit
        # quit selection
        # select high passengers
        # select all high passengers
        # no cargo space left
        # select middle passengers
        # select all middle passengers
        # no staterooms left
        # select low passengers
        # select all low passengers
        # no low berths left
