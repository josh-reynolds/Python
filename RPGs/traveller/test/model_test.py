"""Contains tests for the model module."""
import unittest
from src.calendar import Calendar
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate
from src.financials import Financials
from src.imperial_date import ImperialDate
from src.model import Model
from src.ship import Ship
from src.star_system import StarSystem
from src.uwp import UWP

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

    def test_attach_date_observers(self) -> None:
        """Tests attaching observers to the Model calendar."""
        model = Model()
        model.date = Calendar()
        model.map_hex = StarSystem("TEST", Coordinate(1,1,1), UWP('A',1,1,1,1,1,1,1))
        model.depot = CargoDepot(model.get_star_system(), model.get_current_date())
        model.financials = Financials(1, model.get_current_date(),
                                      Ship("Type A Free Trader"), model.get_star_system())
        self.assertEqual(model.date_string, "001-1105")

        model.attach_date_observers()
        self.assertEqual(len(model.date.observers), 2)
        self.assertTrue(isinstance(model.date.observers[0], CargoDepot))
        self.assertTrue(isinstance(model.date.observers[1], Financials))
