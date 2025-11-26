"""Contains tests for the baggage module."""
import unittest
from test.mock import SystemMock
from src.baggage import Baggage, baggage_from
from src.coordinate import Coordinate

class BaggageTestCase(unittest.TestCase):
    """Tests Baggage class."""

    def test_baggage_string(self) -> None:
        """Test the string representation of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage}",
                         "Baggage : 1 ton : Pluto -> Uranus")

    def test_baggage_repr(self) -> None:
        """Test the repr string of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage!r}",
                         "Baggage(SystemMock('Pluto'), SystemMock('Uranus'))")

    def test_baggage_from(self) -> None:
        """Test importing Baggage from a parsed string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source}

        actual = baggage_from("(1, 0, -1)", "(0, 0, 0)", systems)
        expected = Baggage(source, destination)
        self.assertEqual(actual, expected)

        actual = baggage_from("(0, 0, 0)", "(1, 0, -1)", systems)
        expected = Baggage(destination, source)
        self.assertEqual(actual, expected)

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, -1, 0)", "(1, 0, -1)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(0, 0, 0)", "(1, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(m, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, 0, -1)", "(0, m, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: ' m'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, 1, 1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")

    def test_encode(self) -> None:
        """Test exporting a Baggage object to a string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        baggage = Baggage(source, destination)

        actual = baggage.encode()
        expected = "Baggage - (1, 0, -1) - (0, 0, 0)"
        self.assertEqual(actual, expected)
