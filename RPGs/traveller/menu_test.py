"""Contains tests for the menu module."""
import unittest
from typing import cast, List
from menu import Menu, Passengers
from ship import Ship
from star_system import StarSystem
from traveller import Game

class MenuTestCase(unittest.TestCase):
    """Test menu screen."""

    class ShipMock(Ship):
        """Mocks a Ship for testing."""


    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        Menu.update(MenuTestCase.ShipMock())

class PassengersTestCase(unittest.TestCase):
    """Test Passengers screen."""

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_passenger_destinations of a client class
    @unittest.skip("test has side effects: printing")
    def test_get_passenger_destinations(self) -> None:
        """Test getting list of passenger destinations."""
        game = Game()
        passengers = Passengers(game)
        potential_destinations = cast(List[StarSystem], game.location.destinations.copy())

        destinations = passengers._get_passenger_destinations(potential_destinations, 1)
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # pylint: disable=W0212
    # W0212: Access to a protected member _select_passengers of a client class
    @unittest.skip("test has side effects: printing")
    def test_select_passengers(self) -> None:
        """Test selection of passengers from a list."""
        game = Game()
        passengers = Passengers(game)
        available = (5,5,5)
        destination = game.location.destinations[0]

        selection = passengers._select_passengers(available, destination)
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



# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
