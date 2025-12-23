"""Contains tests for the model module."""
import unittest
from src.calendar import Calendar
from src.model import Model

class ModelTestCase(unittest.TestCase):
    """Tests Model class."""

    def test_add_day(self) -> None:
        """Tests adding a day to the Model."""
        model = Model()
        model.date = Calendar()
        self.assertEqual(model.date.day, 1)
        model.add_day()
        self.assertEqual(model.date.day, 2)
