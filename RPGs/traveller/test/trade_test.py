"""Contains tests for the trade module."""
import unittest
from typing import List, cast
from main import Game
from src.model import Model
from src.trade import TradeScreen
from src.star_system import StarSystem

class TradeScreenTestCase(unittest.TestCase):
    """Test TradeScreen class."""

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_freight_destinations of a client class
    @unittest.skip("test has side effects: printing")
    def test_get_destinations(self) -> None:
        """Test getting list of freight destinations."""
        game = Game()
        model = Model()
        trade = TradeScreen(game, model)
        potential_destinations = cast(List[StarSystem],
                                      game.model.location.destinations.copy())

        destinations = trade._get_destinations(potential_destinations,
                                               1, "freight shipments")
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # pylint: disable=W0212
    # W0212: Access to a protected member _select_freight_lots of a client class
    @unittest.skip("test has side effects: printing & input")
    def test_select_freight_lots(self):
        """Test selection of freight from a list."""
        game = Game()
        model = Model()
        trade = TradeScreen(game, model)
        available = [5, 10, 15, 20]
        destination = game.model.location.destinations[0]

        tonnage, selection = trade._select_freight_lots(available, destination)
        print(tonnage, selection)

        # no freight remaining, auto-exit
        # quit selection
        # non-numeric input
        # freight selection in list
        # freight selection not in list
        # not enough space in hold
