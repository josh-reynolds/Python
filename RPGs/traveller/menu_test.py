"""Contains tests for the menu module."""
import unittest
from menu import Menu
from ship import Ship

class MenuTestCase(unittest.TestCase):
    """Test menu screen."""

    class ShipMock(Ship):
        """Mocks a Ship for testing."""


    @unittest.skip("test has side effects: input, clear screen & printing")
    def test_update(self):
        """Tests the basic front end menu screen."""
        Menu.update(MenuTestCase.ShipMock())


# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
