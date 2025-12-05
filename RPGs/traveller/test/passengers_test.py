"""Contains tests for the passengers module."""
import unittest
from test.mock import SystemMock
from src.coordinate import Coordinate
from src.passengers import Passenger, Passage, passenger_from

class PassengerTestCase(unittest.TestCase):
    """Tests Passenger class."""

    def test_passenger_str(self) -> None:
        """Test the string representation of a Passenger object."""
        passenger = Passenger(Passage.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger}", "Low passage to Uranus")

    def test_passenger_repr(self) -> None:
        """Test the repr string of a Passenger object."""
        passenger = Passenger(Passage.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger!r}", "Passenger(<Passage.LOW: 2>, SystemMock('Uranus'))")

    def test_passenger_guess_survivors(self) -> None:
        """Test Passenger guesses as to number of low lottery survivors."""
        passenger = Passenger(Passage.LOW, SystemMock("Uranus"))
        for _ in range(1000):
            passenger.guess_survivors(10)
            guess = passenger.guess
            self.assertGreaterEqual(guess, 0)       #type: ignore[arg-type]
            self.assertLessEqual(guess, 10)         #type: ignore[arg-type]

    # pylint: disable=R0915
    # R0915: Too many statements (52/50)
    def test_from_string(self) -> None:
        """Test importing a Passenger from a string."""
        string = "high - (0, 0, 0)"
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination}
        actual = passenger_from(string, systems)
        expected = Passenger(Passage.HIGH, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "High passage to Jupiter")

        string = "middle - (1, 0, -1)"
        destination = SystemMock("Mars")
        destination.coordinate = Coordinate(1,0,-1)
        systems[Coordinate(1,0,-1)] = destination
        actual = passenger_from(string, systems)
        expected = Passenger(Passage.MIDDLE, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "Middle passage to Mars")

        string = "low - (-1, 0, 1)"
        destination = SystemMock("Venus")
        destination.coordinate = Coordinate(-1,0,1)
        systems[Coordinate(-1,0,1)] = destination
        actual = passenger_from(string, systems)
        expected = Passenger(Passage.LOW, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "Low passage to Venus")

        string = "HIgh - (0, 0, 0)"
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        actual = passenger_from(string, systems)
        expected = Passenger(Passage.HIGH, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "High passage to Jupiter")

        string = "bollix - (0, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "unrecognized passage class: 'bollix'")

        string = "High - (0, 0, 0) - some - more"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "input string has extra data: 'High - (0, 0, 0) - some - more'")

        string = "High (0, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "input string is missing data: 'High (0, 0, 0)'")

        string = "High - (m, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "High - (1, 1, 1)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")

        string = "High - (2, 0, -2)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(2, 0, -2)'")

    def test_encode(self) -> None:
        """Test exporting a Passenger to a string."""
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(Passage.HIGH, destination)

        actual = passenger.encode()
        expected = "high - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "High passage to Jupiter")

        destination = SystemMock("Neptune")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(Passage.MIDDLE, destination)

        actual = passenger.encode()
        expected = "middle - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "Middle passage to Neptune")

        destination = SystemMock("Uranus")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(Passage.LOW, destination)

        actual = passenger.encode()
        expected = "low - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "Low passage to Uranus")
