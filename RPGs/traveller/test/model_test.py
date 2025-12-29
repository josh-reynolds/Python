"""Contains tests for the model module."""
import unittest
from test.mock import SystemMock, CalendarMock, CargoDepotMock, FinancialsMock
from test.mock import ControlsMock
from src.imperial_date import ImperialDate
from src.model import Model

class ModelTestCase(unittest.TestCase):
    """Tests Model class."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        ModelTestCase.model = Model(ControlsMock([]))
        ModelTestCase.model.date = CalendarMock()

    def test_get_current_date(self) -> None:
        """Tests querying current date from the Model."""
        self.assertEqual(ModelTestCase.model.get_current_date(), ImperialDate(1,1105))
        ModelTestCase.model.add_day()
        self.assertEqual(ModelTestCase.model.get_current_date(), ImperialDate(2,1105))

    def test_date_string(self) -> None:
        """Tests retrieval of the current date from the Model as a string."""
        self.assertEqual(ModelTestCase.model.date_string, "001-1105")
        ModelTestCase.model.add_day()
        self.assertEqual(ModelTestCase.model.date_string, "002-1105")

    def test_add_day(self) -> None:
        """Tests adding a day to the Model."""
        self.assertEqual(ModelTestCase.model.date.day, 1)
        ModelTestCase.model.add_day()
        self.assertEqual(ModelTestCase.model.date.day, 2)

    def test_plus_week(self) -> None:
        """Tests advancing the curret date by a week."""
        self.assertEqual(ModelTestCase.model.date_string, "001-1105")
        ModelTestCase.model.plus_week()
        self.assertEqual(ModelTestCase.model.date_string, "008-1105")

    def test_load_calendar(self) -> None:
        """Tests applying json data to the Model calendar."""
        self.assertEqual(ModelTestCase.model.date_string, "001-1105")

        string = "111-1111"
        ModelTestCase.model.load_calendar(string)
        self.assertEqual(ModelTestCase.model.date_string, string)

        string = "1111"
        with self.assertRaises(ValueError) as context:
            ModelTestCase.model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "string must have both day and year values: '1111'")

        string = "1-111-1111"
        with self.assertRaises(ValueError) as context:
            ModelTestCase.model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "string must have only day and year values: '1-111-1111'")

        string = "m-1111"
        with self.assertRaises(ValueError) as context:
            ModelTestCase.model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "11-m"
        with self.assertRaises(ValueError) as context:
            ModelTestCase.model.load_calendar(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

    def test_attach_date_observers(self) -> None:
        """Tests attaching observers to the Model calendar."""
        ModelTestCase.model.map_hex = SystemMock()
        ModelTestCase.model.depot = CargoDepotMock()
        ModelTestCase.model.financials = FinancialsMock()
        self.assertEqual(ModelTestCase.model.date_string, "001-1105")

        ModelTestCase.model.attach_date_observers()
        self.assertEqual(len(ModelTestCase.model.date.observers), 2)
        self.assertTrue(isinstance(ModelTestCase.model.date.observers[0], CargoDepotMock))
        self.assertTrue(isinstance(ModelTestCase.model.date.observers[1], FinancialsMock))
