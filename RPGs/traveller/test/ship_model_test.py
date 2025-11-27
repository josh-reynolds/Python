"""Contains tests for the ship_model module."""
import unittest
from src.credits import Credits
from src.ship_model import ship_model_from, ShipModel, get_ship_models

class ShipModelTestCase(unittest.TestCase):
    """Tests ShipModel class."""

    def test_ship_model_from(self) -> None:
        """Test creation of a ShipModel from a name string."""
        actual = ship_model_from("Type A Free Trader")
        expected = ShipModel()
        self.assertEqual(actual, expected)

        actual = ship_model_from("Type S Scout/Courier")
        expected = ShipModel()
        expected.name = "Type S Scout/Courier"
        expected.hull = 100
        expected.passenger_berths = 3
        expected.low_berths = 0
        expected.acceleration = 2
        expected.streamlined = True
        expected.hold_size = 3
        expected.fuel_tank = 40
        expected.jump_range = 2
        expected.jump_fuel_cost = 20
        expected.trip_fuel_cost = 20
        expected.base_price = Credits(29_430_000)
        self.assertEqual(actual, expected)

    def test_get_ship_models(self) -> None:
        """Test retrieval of available ship models."""
        actual = get_ship_models()
        expected = ["Type A Free Trader", "Type S Scout/Courier", "Type Y Yacht"]
        self.assertEqual(actual, expected)
