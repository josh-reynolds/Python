"""Contains tests for the menu module."""
import unittest
from test.mock import ShipMock
from src.menu import Menu

class MenuTestCase(unittest.TestCase):
    """Test menu screen."""

    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        Menu.update(ShipMock("Type A Free Trader"))
