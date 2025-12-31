"""Contains tests for the trade module."""
import unittest
from typing import List, cast
from test.mock import ControlsMock
from main import Game
from src.model import Model
from src.trade import TradeScreen
from src.star_system import StarSystem

class TradeScreenTestCase(unittest.TestCase):
    """Test TradeScreen class."""

    # TO_DO: should move to model_test module
    @unittest.skip("test has side effects: printing")
    def test_get_destinations(self) -> None:
        """Test getting list of freight destinations."""
        game = Game()
        model = Model(ControlsMock([]))
        trade = TradeScreen(game, model)
        potential_destinations = cast(List[StarSystem],
                                      trade.model.map_hex.destinations.copy())

        destinations = trade.model.get_destinations(potential_destinations,
                                               1, "freight shipments")
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # TO_DO: should move to model_test module
    @unittest.skip("test has side effects: printing & input")
    def test_select_freight_lots(self):
        """Test selection of freight from a list."""
        game = Game()
        model = Model(ControlsMock([]))
        trade = TradeScreen(game, model)
        available = [5, 10, 15, 20]
        destination = trade.model.map_hex.destinations[0]

        tonnage, selection = trade.model.select_freight_lots(available, destination)
        print(tonnage, selection)

        # no freight remaining, auto-exit
        # quit selection
        # non-numeric input
        # freight selection in list
        # freight selection not in list
        # not enough space in hold
