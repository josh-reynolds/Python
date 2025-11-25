"""Contains tests for the imperial_date module."""
import unittest
from src.imperial_date import ImperialDate, imperial_date_from

class ImperialDateTestCase(unittest.TestCase):
    """Tests ImperialDate class."""

    def test_date_string(self) -> None:
        """Test an ImperialDate string is properly formatted."""
        date = ImperialDate(1, 100)
        self.assertEqual(f"{date}", "001-100")

    def test_date_equality(self) -> None:
        """Test equality for ImperialDates."""
        date1 = ImperialDate(1,100)
        date2 = ImperialDate(1,100)
        date3 = ImperialDate(2,100)
        self.assertEqual(date1, date2)
        self.assertNotEqual(date1, date3)
        self.assertNotEqual(date2, date3)
        self.assertNotEqual(date1, (1, 100))

    def test_date_comparison(self) -> None:
        """Test comparison between two ImperialDates."""
        date1 = ImperialDate(10, 100)
        date2 = ImperialDate(11, 100)
        date3 = ImperialDate(1, 101)
        date4 = ImperialDate(20, 99)
        date5 = ImperialDate(1, 100)
        date6 = ImperialDate(11, 100)
        self.assertGreater(date2, date1)
        self.assertGreater(date3, date1)
        self.assertLess(date4, date1)
        self.assertLess(date5, date1)
        self.assertGreaterEqual(date2, date1)
        self.assertGreaterEqual(date2, date6)
        self.assertLessEqual(date4, date1)
        self.assertLessEqual(date6, date2)

    def test_date_copy(self) -> None:
        """Test copying an ImperialDate."""
        date1 = ImperialDate(1, 100)
        date2 = date1.copy()
        self.assertEqual(date2.day, 1)
        self.assertEqual(date2.year, 100)
        self.assertEqual(date1, date2)

    def test_date_plus_days(self) -> None:
        """Test adding days to an ImperialDate."""
        date1 = ImperialDate(1, 100)
        date2 = ImperialDate(365, 100)
        self.assertEqual(date1 + 1, ImperialDate(2, 100))
        self.assertEqual(date2 + 1, ImperialDate(1, 101))
        self.assertEqual(date1 + -1, ImperialDate(365, 99))
        self.assertEqual(date2 + -1, ImperialDate(364, 100))
        self.assertEqual(date1 + -10, ImperialDate(356, 99))

    def test_date_minus_date(self) -> None:
        """Test subtracting an ImperialDate from another."""
        date1 = ImperialDate(1, 100)
        date2 = ImperialDate(5, 100)
        date3 = ImperialDate(365, 99)
        date4 = ImperialDate(1, 98)
        self.assertEqual(date2-date1, 4)
        self.assertEqual(date1-date2, -4)
        self.assertEqual(date1-date3, 1)
        self.assertEqual(date3-date1, -1)
        self.assertEqual(date1-date4, 730)

    def test_date_minus_day(self) -> None:
        """Test subtracting a number of days from an ImperialDate."""
        date1 = ImperialDate(5,100)
        self.assertEqual(date1-1, ImperialDate(4, 100))
        self.assertEqual(date1-5, ImperialDate(365, 99))

    # pylint: disable=W0212
    # W0212: Access to a protected member _date_value of a client class
    def test_date_value(self) -> None:
        """Test the internal value of an ImperialDate."""
        date1 = ImperialDate(1, 10)
        self.assertEqual(date1._date_value(), 3651)

    def test_from_string(self) -> None:
        """Test importing an ImperialDate from a string."""
        string = "111-1111"
        actual = imperial_date_from(string)
        expected = ImperialDate(111, 1111)
        self.assertEqual(actual, expected)

        string = "222-1111"
        actual = imperial_date_from(string)
        expected = ImperialDate(222, 1111)
        self.assertEqual(actual, expected)

        string = "000-1111"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "day value must be between 1 and 365: '000'")

        string = "366-1111"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "day value must be between 1 and 365: '366'")

        string = "001"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "string must have both day and year values: '001'")

        string = "001-1111-22"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "string must have only day and year values: '001-1111-22'")

        string = "00m-1111"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: '00m'")

        string = "001-111m"
        with self.assertRaises(ValueError) as context:
            _ = imperial_date_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: '111m'")
