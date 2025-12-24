"""Contains tests for the model module."""
import unittest
from src.calendar import Calendar
from src.imperial_date import ImperialDate
from src.model import Model

class ModelTestCase(unittest.TestCase):
    """Tests Model class."""

    def test_get_current_date(self) -> None:
        """Tests querying current date from the Model."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.get_current_date(), ImperialDate(1,1105))
        model.add_day()
        self.assertEqual(model.get_current_date(), ImperialDate(2,1105))

    def test_date_string(self) -> None:
        """Tests retrieval of the current date from the Model as a string."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.date_string, "001-1105")
        model.add_day()
        self.assertEqual(model.date_string, "002-1105")

    def test_add_day(self) -> None:
        """Tests adding a day to the Model."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.date.day, 1)
        model.add_day()
        self.assertEqual(model.date.day, 2)

    def test_plus_week(self) -> None:
        """Tests advancing the curret date by a week."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.date_string, "001-1105")
        model.plus_week()
        self.assertEqual(model.date_string, "008-1105")

    def test_load_calendar(self) -> None:
        """Tests applying json data to the Model calendar."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.date_string, "001-1105")

        string = "111-1111"
        model.load_calendar(string)
        self.assertEqual(model.date_string, string)

        string = "1111"
        with self.assertRaises(ValueError) as context:
            model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "string must have both day and year values: '1111'")

        string = "1-111-1111"
        with self.assertRaises(ValueError) as context:
            model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "string must have only day and year values: '1-111-1111'")

        string = "m-1111"
        with self.assertRaises(ValueError) as context:
            model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "11-m"
        with self.assertRaises(ValueError) as context:
            model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")
