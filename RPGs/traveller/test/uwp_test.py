"""Contains tests for the star_map module."""
import unittest
from src.uwp import uwp_from, UWP

class UWPTestCase(unittest.TestCase):
    """Tests UWP class."""

    def test_from_string(self) -> None:
        """Test importing a UWP from a string."""
        string = "A123456-7"
        actual = uwp_from(string)
        expected = UWP('A', 1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(actual, expected)

        string = "A877777-7"
        actual = uwp_from(string)
        expected = UWP('A', 8, 7, 7, 7, 7, 7, 7)
        self.assertEqual(actual, expected)

        string = "AAAAAAA-A"
        actual = uwp_from(string)
        expected = UWP('A', 10, 10, 10, 10, 10, 10, 10)
        self.assertEqual(actual, expected)

        string = "AG77777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 16: 'G'")

        string = "M777777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for starport: 'M'")

        string = "A7777777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "string length should be exactly 9 characters: 10")

        string = "A77777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "string length should be exactly 9 characters: 8")

        string = "A777777!7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "tech level should be separated by a '-' character: '!'")

        uwp = UWP('A', 1, 2, 3, 4, 5, 6, 7)
        uwp_string = f"{uwp}"
        actual = uwp_from(uwp_string)
        self.assertEqual(actual, uwp)
