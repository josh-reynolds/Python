"""Contains tests for the credits module."""
import unittest
from src.credits import Credits

class CreditsTestCase(unittest.TestCase):
    """Tests Credits class."""

    def test_credits_string(self) -> None:
        """Tests string representation of a Credits object."""
        credits1 = Credits(1)
        credits2 = Credits(10)
        credits3 = Credits(100)
        credits4 = Credits(1000)
        credits5 = Credits(10000)
        credits6 = Credits(100000)
        credits7 = Credits(1000000)
        credits8 = Credits(11500000)
        credits9 = Credits(1000000000)
        self.assertEqual(f"{credits1}", "1 Cr")
        self.assertEqual(f"{credits2}", "10 Cr")
        self.assertEqual(f"{credits3}", "100 Cr")
        self.assertEqual(f"{credits4}", "1,000 Cr")
        self.assertEqual(f"{credits5}", "10,000 Cr")
        self.assertEqual(f"{credits6}", "100,000 Cr")
        self.assertEqual(f"{credits7}", "1.0 MCr")
        self.assertEqual(f"{credits8}", "11.5 MCr")
        self.assertEqual(f"{credits9}", "1,000.0 MCr")

    def test_credits_comparison(self) -> None:
        """Tests comparison of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        credits3 = Credits(2)
        self.assertGreater(credits2,credits1)
        self.assertLess(credits1,credits2)
        self.assertEqual(credits2,credits3)

    def test_credits_addition(self) -> None:
        """Tests addition of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(1)
        self.assertEqual(credits1+credits2,Credits(2))

    def test_credits_subtraction(self) -> None:
        """Tests subtraction of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        self.assertEqual(credits2-credits1,Credits(1))

    def test_credits_multiplication(self) -> None:
        """Tests multiplication of a Credits object by an integer."""
        credits1 = Credits(10)
        self.assertEqual(credits1 * 5, Credits(50))
