"""Contains tests for the model module."""
import unittest
from typing import cast
from test.mock import SystemMock, CalendarMock, CargoDepotMock, FinancialsMock
from test.mock import ControlsMock, DeepSpaceMock, ShipMock
from src.imperial_date import ImperialDate
from src.model import Model, GuardClauseFailure
from src.ship import RepairStatus
from src.utilities import BOLD_RED, END_FORMAT

class ModelTestCase(unittest.TestCase):
    """Tests Model class."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        ModelTestCase.model = Model(ControlsMock([]))
        ModelTestCase.model.date = CalendarMock()

    # pylint: disable=W0212
    # W0212: access to a protected member _add_day of a client class
    def test_get_current_date(self) -> None:
        """Tests querying current date from the Model."""
        self.assertEqual(ModelTestCase.model.date.current_date, ImperialDate(1,1105))
        ModelTestCase.model._add_day()
        self.assertEqual(ModelTestCase.model.date.current_date, ImperialDate(2,1105))

    # pylint: disable=W0212
    # W0212: access to a protected member _add_day of a client class
    def test_date_string(self) -> None:
        """Tests retrieval of the current date from the Model as a string."""
        self.assertEqual(ModelTestCase.model.date_string, "001-1105")
        ModelTestCase.model._add_day()
        self.assertEqual(ModelTestCase.model.date_string, "002-1105")

    # pylint: disable=W0212
    # W0212: access to a protected member _add_day of a client class
    def test_add_day(self) -> None:
        """Tests adding a day to the Model."""
        self.assertEqual(ModelTestCase.model.date.day, 1)
        ModelTestCase.model._add_day()
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


class InboundFromJumpTestCase(unittest.TestCase):
    """Tests Model.inbound_from_jump() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        InboundFromJumpTestCase.model = Model(ControlsMock([]))
        InboundFromJumpTestCase.model.date = CalendarMock()
        InboundFromJumpTestCase.model.map_hex = SystemMock()
        InboundFromJumpTestCase.model.ship = ShipMock()

    def test_inbound_from_deep_space(self) -> None:
        """Tests attempting to travel to inner system while in Deep Space."""
        model = InboundFromJumpTestCase.model
        model.map_hex = DeepSpaceMock()

        with self.assertRaises(GuardClauseFailure) as context:
            model.inbound_from_jump()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}You are in deep space. There is no " +\
                         f"inner system to travel to.{END_FORMAT}")

    def test_inbound_with_drive_failure(self) -> None:
        """Tests attempting to travel to inner system when drives need repair."""
        model = InboundFromJumpTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.inbound_from_jump()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")

        model.ship.repair_status = RepairStatus.PATCHED
        with self.assertRaises(GuardClauseFailure) as context:
            model.inbound_from_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel in from the jump point.")

        model.ship.repair_status = RepairStatus.REPAIRED
        with self.assertRaises(GuardClauseFailure) as context:
            model.inbound_from_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel in from the jump point.")

    def test_inbound_with_insufficient_fuel(self) -> None:
        """Tests attempting to travel to inner system when there is not enough fuel in the tanks."""
        model = InboundFromJumpTestCase.model

        self.assertEqual(model.fuel_level(), 0)

        with self.assertRaises(GuardClauseFailure) as context:
            model.inbound_from_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel in from the jump point.")

    def test_inbound_to_orbit(self) -> None:
        """Tests successful travel from the jump point to orbit of the mainworld."""
        model = InboundFromJumpTestCase.model
        model.ship.current_fuel = model.fuel_tank_size()

        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))
        self.assertEqual(cast(SystemMock, model.map_hex).location, "jump")

        result = model.inbound_from_jump()

        self.assertEqual(model.fuel_level(), 25)
        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        self.assertEqual(cast(SystemMock, model.map_hex).location, "orbit")
        self.assertEqual(result, "Successfully travelled in to orbit.")


class OutboundToJumpTestCase(unittest.TestCase):
    """Tests Model.outbound_from_jump() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        OutboundToJumpTestCase.model = Model(ControlsMock([]))
        OutboundToJumpTestCase.model.date = CalendarMock()
        OutboundToJumpTestCase.model.map_hex = SystemMock()
        OutboundToJumpTestCase.model.ship = ShipMock()

    def test_outbound_with_drive_failure(self) -> None:
        """Tests attempting to travel to jump point when drives need repair."""
        model = OutboundToJumpTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.outbound_to_jump()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot travel to the jump point.{END_FORMAT}")

        model.ship.repair_status = RepairStatus.PATCHED
        with self.assertRaises(GuardClauseFailure) as context:
            model.outbound_to_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel out to the jump point.")

        model.ship.repair_status = RepairStatus.REPAIRED
        with self.assertRaises(GuardClauseFailure) as context:
            model.outbound_to_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel out to the jump point.")

    def test_outbound_with_insufficient_fuel(self) -> None:
        """Tests attempting to travel to jump point when there is not enough fuel in the tanks."""
        model = OutboundToJumpTestCase.model

        self.assertEqual(model.fuel_level(), 0)

        with self.assertRaises(GuardClauseFailure) as context:
            model.outbound_to_jump()
        self.assertEqual(f"{context.exception}",
                         "Insufficient fuel to travel out to the jump point.")

    def test_outbound_to_orbit(self) -> None:
        """Tests successful travel from orbit to the jump point."""
        model = OutboundToJumpTestCase.model
        model.ship.current_fuel = model.fuel_tank_size()
        cast(SystemMock, model.map_hex).location = "orbit"

        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))
        self.assertEqual(cast(SystemMock, model.map_hex).location, "orbit")

        result = model.outbound_to_jump()

        self.assertEqual(model.fuel_level(), 25)
        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        self.assertEqual(cast(SystemMock, model.map_hex).location, "jump")
        self.assertEqual(result, "Successfully travelled out to the jump point.")


class LandTestCase(unittest.TestCase):
    """Tests Model.land() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        LandTestCase.model = Model(ControlsMock([]))
        LandTestCase.model.ship = ShipMock()
        LandTestCase.model.map_hex = SystemMock()
        LandTestCase.model.financials = FinancialsMock()

    def test_unstreamlined_landing(self) -> None:
        """Tests successful travel from orbit to the jump point."""
        model = LandTestCase.model
        model.ship.model.streamlined = False

        with self.assertRaises(GuardClauseFailure) as context:
            model.land()
        self.assertEqual(f"{context.exception}",
                         "Your ship is not streamlined and cannot land.")

    def test_landing_with_drive_failure(self) -> None:
        """Tests attempting to travel land when drives need repair."""
        model = LandTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.land()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")

        model.ship.repair_status = RepairStatus.PATCHED
        result = model.land()
        self.assertEqual(result, "\nLanded at the Uranus starport.")

        cast(SystemMock, model.map_hex).location = "orbit"
        model.ship.repair_status = RepairStatus.REPAIRED
        result = model.land()
        self.assertEqual(result, "\nLanded at the Uranus starport.")

    # disembark passengers on landing
    # don't disembark if not destination
    # collect passenger fares
    # run low lottery
    # remove all passengers
    # remove all baggage
    # set location to starport
    # charge berthing fee
    # return success message
