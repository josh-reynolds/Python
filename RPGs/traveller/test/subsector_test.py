"""Contains tests for the subsector module."""
import unittest
from src.subsector import Subsector, subsector_from

class SubsectorTestCase(unittest.TestCase):
    """Tests Subsector class."""

    def test_from_string(self) -> None:
        """Test importing a Subsector from a string."""
        string = "(0, 0) - Regina"
        actual = subsector_from(string)
        expected = Subsector("Regina", (0,0))
        self.assertEqual(actual, expected)

        string = "(-1, 0) - Betelgeuse Marches"
        actual = subsector_from(string)
        expected = Subsector("Betelgeuse Marches", (-1,0))
        self.assertEqual(actual, expected)

        string = "Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "input string is missing data: 'Betelgeuse Marches'")

        string = "(-1, 0) - Betelgeuse Marches - extra - stuff"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "input string has extra data: " +
                         "'(-1, 0) - Betelgeuse Marches - extra - stuff'")

        string = "(0) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "coordinate should have exactly two integers: '(0,)'")

        string = "(0,0,0) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "coordinate should have exactly two integers: '(0, 0, 0)'")

        string = "(0,m) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")
