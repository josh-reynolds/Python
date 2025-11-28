"""Contains tests for the menu module."""
import unittest
from typing import cast, List
from main import Game
from src.menu import Menu, Trade
from src.ship import Ship
from src.star_system import StarSystem

class MenuTestCase(unittest.TestCase):
    """Test menu screen."""

    class ShipMock(Ship):
        """Mocks a Ship for testing."""


    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        Menu.update(MenuTestCase.ShipMock("Type A Free Trader"))


class TradeTestCase(unittest.TestCase):
    """Test Trade screen."""

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_freight_destinations of a client class
    @unittest.skip("test has side effects: printing")
    def test_get_freight_destinations(self) -> None:
        """Test getting list of freight destinations."""
        game = Game()
        trade = Trade(game)
        potential_destinations = cast(List[StarSystem], game.location.destinations.copy())

        destinations = trade._get_freight_destinations(potential_destinations, 1)
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
        trade = Trade(game)
        available = [5, 10, 15, 20]
        destination = game.location.destinations[0]

        tonnage, selection = trade._select_freight_lots(available, destination)
        print(tonnage, selection)

        # no freight remaining, auto-exit
        # quit selection
        # non-numeric input
        # freight selection in list
        # freight selection not in list
        # not enough space in hold
