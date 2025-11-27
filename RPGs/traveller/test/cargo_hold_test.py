"""Contains tests for the populating a cargo hold."""
import unittest
from typing import Sequence
from test.mock import SystemMock
from src.baggage import Baggage
from src.cargo import Cargo
from src.cargo_depot import cargo_hold_from
from src.coordinate import Coordinate
from src.credits import Credits
from src.freight import Freight
from src.utilities import dictionary_from

# pylint: disable=R0915
# R0915 Too many statements (52/50)
class CargoHoldTestCase(unittest.TestCase):
    """Tests populating a cargo hold from saved JSON data."""

    def test_cargo_hold_from(self) -> None:
        """Test importing a list of cargo hold items from JSON string data."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        alternate = SystemMock("Mars")
        alternate.coordinate = Coordinate(-1,0,1)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source,
                   Coordinate(-1,0,1) : alternate}

        data = ["Baggage - (1, 0, -1) - (0, 0, 0)"]
        actual = cargo_hold_from(data, systems)
        expected: Sequence[Freight | Cargo] = [Baggage(source, destination)]
        self.assertEqual(actual, expected)

        data = ["Freight - 10 - (1, 0, -1) - (0, 0, 0)"]
        actual = cargo_hold_from(data, systems)
        expected = [Freight(10, source, destination)]
        self.assertEqual(actual, expected)

        data = ["Cargo - Meat - 10 - None"]
        actual = cargo_hold_from(data, systems)
        expected = [Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)

        data = ["Baggage - (1, 0, -1) - (0, 0, 0)",
                "Freight - 10 - (1, 0, -1) - (0, 0, 0)",
                "Cargo - Meat - 10 - None"]
        actual = cargo_hold_from(data, systems)
        expected = [Baggage(source, destination),
                    Freight(10, source, destination),
                    Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)

        data = ["Freight - m - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "invalid literal for int() with base 10: 'm'")

        data = ["Freight - 0 - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "tonnage must be a positive number: '0'")

        data = ["Cargo - Meat - m - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "invalid literal for int() with base 10: 'm'")

        data = ["Cargo - Meat - -1 - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "quantity must be a positive number: '-1'")

        data = ["Monkeys - Meat - 100 - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "unknown hold content type: 'Monkeys'")

        data = ["Freight - 5 - (1, 0, -1) - (0, 0, 0)",
                "Baggage - (1, 0, -1) - (0, 0, 0)",
                "Freight - 10 - (1, 0, -1) - (-1, 0, 1)",
                "Freight - 15 - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "more than one destination in saved "
                          + "data: '{'(0, 0, 0)', '(-1, 0, 1)'}'")

        data = ["Freight - 5 - (1, 0, -1) - (2, 0, -2)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(2, 0, -2)'")

    def test_cargo_hold_from_encode(self) -> None:
        """Test compatibility of *.encode() and cargo_hold_from()."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        alternate = SystemMock("Mars")
        alternate.coordinate = Coordinate(-1,0,1)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source,
                   Coordinate(-1,0,1) : alternate}

        data = [Baggage(source, destination).encode(),
                Freight(10, source, destination).encode(),
                Cargo("Meat", "10", Credits(1500), 1,
                      dictionary_from("{Ag:-2,Na:2,In:3}"),
                      dictionary_from("{Ag:-2,In:2,Po:1}")).encode()]
        actual = cargo_hold_from(data, systems)
        expected = [Baggage(source, destination),
                    Freight(10, source, destination),
                    Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)
