"""Contains tests for the menu module."""
import unittest
from test.mock import ShipMock
from src.menu import MenuScreen

class MenuScreenTestCase(unittest.TestCase):
    """Test MenuScreen class."""

    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        MenuScreen.update(ShipMock("Type A Free Trader"))
