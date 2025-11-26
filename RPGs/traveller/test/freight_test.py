"""Contains tests for the freight module."""
import unittest
from test.mock import SystemMock
from src.coordinate import Coordinate
from src.freight import Freight, freight_from

class FreightTestCase(unittest.TestCase):
    """Tests Freight class."""

    def test_freight_string(self) -> None:
        """Test the string representation of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight}",
                         "Freight : 10 tons : Pluto -> Uranus")

    def test_freight_repr(self) -> None:
        """Test the repr string of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight!r}",
                         "Freight(10, SystemMock('Pluto'), SystemMock('Uranus'))")

    def test_freight_from(self) -> None:
        """Test importing Freight from a parsed string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source}

        actual = freight_from(10, "(1, 0, -1)", "(0, 0, 0)", systems)
        expected = Freight(10, source, destination)
        self.assertEqual(actual, expected)

        actual = freight_from(100, "(0, 0, 0)", "(1, 0, -1)", systems)
        expected = Freight(100, destination, source)
        self.assertEqual(actual, expected)

        with self.assertRaises(ValueError) as context:
            _ = freight_from(100, "(1, -1, 0)", "(1, 0, -1)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(100, "(0, 0, 0)", "(1, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(0, "(1, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "tonnage must be a positive number: '0'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(-10, "(1, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "tonnage must be a positive number: '-10'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(m, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(1, 0, -1)", "(0, m, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: ' m'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(1, 1, 1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")

    def test_encode(self) -> None:
        """Test exporting a Freight object to a string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        freight = Freight(10, source, destination)

        actual = freight.encode()
        expected = "Freight - 10 - (1, 0, -1) - (0, 0, 0)"
        self.assertEqual(actual, expected)
