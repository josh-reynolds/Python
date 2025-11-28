"""Contains tests for the menu module."""
import unittest
from src.menu import Menu
from src.ship import Ship

class MenuTestCase(unittest.TestCase):
    """Test menu screen."""

    class ShipMock(Ship):
        """Mocks a Ship for testing."""


    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        Menu.update(MenuTestCase.ShipMock("Type A Free Trader"))
