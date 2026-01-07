"""Contains tests for game state transitions."""
import unittest
from typing import cast
from test.mock import SystemMock, CalendarMock, FinancialsMock
from test.mock import ControlsMock, DeepSpaceMock, ShipMock, ObserverMock
from src.baggage import Baggage
from src.credits import Credits
from src.imperial_date import ImperialDate
from src.model import Model, GuardClauseFailure
from src.passengers import Passenger, Passage
from src.ship import RepairStatus
from src.utilities import BOLD_RED, END_FORMAT

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
        """Tests attempting to land with an unstreamlined ship."""
        model = LandTestCase.model
        model.ship.model.streamlined = False

        with self.assertRaises(GuardClauseFailure) as context:
            model.land()
        self.assertEqual(f"{context.exception}",
                         "Your ship is not streamlined and cannot land.")

    def test_landing_with_drive_failure(self) -> None:
        """Tests attempting to land when drives need repair."""
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

    def test_landing_with_no_passengers(self) -> None:
        """Tests successful landing with no passengers on board."""
        model = LandTestCase.model
        cast(SystemMock, model.map_hex).location = "orbit"
        model.financials.balance = Credits(500)
        view = ObserverMock()
        model.financials.add_view(view)
        # NOTE: transition does not check source location, should we?

        result = model.land()
        self.assertEqual(cast(SystemMock, model.map_hex).location, "starport")
        self.assertEqual(view.message, "Charging 100 Cr berthing fee.")
        self.assertEqual(model.balance, Credits(400))
        self.assertEqual(result, "\nLanded at the Uranus starport.")

    # pylint: disable=W0212
    # W0212: access to a protected member _add_passengers of a client class
    def test_landing_at_uncontracted_destination(self) -> None:
        """Tests successful landing with passengers for different destination."""
        model = LandTestCase.model
        cast(SystemMock, model.map_hex).location = "orbit"
        model.financials.balance = Credits(500)
        view = ObserverMock()
        model.financials.add_view(view)
        destination = SystemMock("Jupiter")
        passengers = [Passenger(Passage.MIDDLE, destination)]
        model._add_passengers(passengers)

        self.assertEqual(model.ship.destination, destination)
        self.assertEqual(model.ship.total_passenger_count, 1)

        result = model.land()
        self.assertEqual(model.ship.total_passenger_count, 1)
        self.assertEqual(cast(SystemMock, model.map_hex).location, "starport")
        self.assertEqual(view.message, "Charging 100 Cr berthing fee.")
        self.assertEqual(model.balance, Credits(400))
        self.assertEqual(result, "\nLanded at the Uranus starport.")

    # pylint: disable=W0212
    # W0212: access to a protected member _add_passengers of a client class
    # W0212: access to a protected member _load_cargo of a client class
    def test_landing_at_contracted_destination(self) -> None:
        """Tests successful landing with passengers for this destination."""
        model = LandTestCase.model
        cast(SystemMock, model.map_hex).location = "orbit"
        model.financials.balance = Credits(500)
        view = ObserverMock()
        model.financials.add_view(view)
        destination = SystemMock("Uranus")
        passengers = [Passenger(Passage.HIGH, destination)]
        model._add_passengers(passengers)
        model._load_cargo([Baggage(SystemMock("Neptune"), destination)])

        self.assertEqual(model.ship.destination, destination)
        self.assertEqual(model.ship.total_passenger_count, 1)
        self.assertEqual(model.free_cargo_space, 81)

        result = model.land()
        self.assertEqual(model.ship.total_passenger_count, 0)
        self.assertEqual(model.free_cargo_space, 82)
        self.assertEqual(cast(SystemMock, model.map_hex).location, "starport")
        self.assertEqual(view.message, "Charging 100 Cr berthing fee.")
        self.assertEqual(model.balance, Credits(10400))
        self.assertEqual(result, "Passengers disembarking on Uranus.\n" +
                                 "Receiving 10,000 Cr in passenger fares.\n" +
                                 "\nLanded at the Uranus starport.")

    # pylint: disable=W0212
    # W0212: access to a protected member _add_passengers of a client class
    def test_landing_with_low_passengers(self) -> None:
        """Tests successful landing with low passengers for this destination."""
        model = LandTestCase.model
        cast(SystemMock, model.map_hex).location = "orbit"
        model.financials.balance = Credits(500)
        view = ObserverMock()
        model.financials.add_view(view)
        destination = SystemMock("Uranus")
        passenger = Passenger(Passage.LOW, destination)
        passenger.endurance = 5    # guarantee this passenger survives
        passenger.guess = 1        # and they correctly guess the number of survivors
        model._add_passengers([passenger])

        self.assertEqual(model.ship.destination, destination)
        self.assertEqual(model.ship.total_passenger_count, 1)

        result = model.land()
        self.assertEqual(model.ship.total_passenger_count, 0)
        self.assertEqual(cast(SystemMock, model.map_hex).location, "starport")
        self.assertEqual(view.message, "Charging 100 Cr berthing fee.")
        self.assertEqual(model.balance, Credits(1390))
        self.assertEqual(result, "Passengers disembarking on Uranus.\n" +
                                 "Receiving 990 Cr in passenger fares.\n" +
                                 "1 of 1 low passengers survived revival.\n" +
                                 "Landed at the Uranus starport.")


class WildernessTestCase(unittest.TestCase):
    """Tests Model.wilderness() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        WildernessTestCase.model = Model(ControlsMock([]))
        WildernessTestCase.model.ship = ShipMock()
        WildernessTestCase.model.map_hex = SystemMock()

    def test_unstreamlined_landing(self) -> None:
        """Tests attempting to land in the wilderness with an unstreamlined ship."""
        model = WildernessTestCase.model
        model.ship.model.streamlined = False

        with self.assertRaises(GuardClauseFailure) as context:
            model.wilderness()
        self.assertEqual(f"{context.exception}",
                         "Your ship is not streamlined and cannot land.")

    def test_landing_with_drive_failure(self) -> None:
        """Tests attempting to land in the wilderness when drives need repair."""
        model = WildernessTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.wilderness()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")

        model.ship.repair_status = RepairStatus.PATCHED
        result = model.wilderness()
        self.assertEqual(result, "\nLanded on the surface of Uranus.")

        cast(SystemMock, model.map_hex).location = "orbit"
        model.ship.repair_status = RepairStatus.REPAIRED
        result = model.wilderness()
        self.assertEqual(result, "\nLanded on the surface of Uranus.")

    def test_wilderness_landing(self) -> None:
        """Tests a successful wilderness landing."""
        model = WildernessTestCase.model
        result = model.wilderness()
        self.assertEqual(result, "\nLanded on the surface of Uranus.")
        self.assertEqual(cast(SystemMock, model.map_hex).location, "wilderness")


class ToDepotTestCase(unittest.TestCase):
    """Tests Model.to_depot() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        ToDepotTestCase.model = Model(ControlsMock([]))
        ToDepotTestCase.model.map_hex = SystemMock()

    def test_to_depot(self) -> None:
        """Tests successfully moving to the trade depot."""
        model = ToDepotTestCase.model
        result = model.to_depot()
        self.assertEqual(result, "Entered the Uranus cargo depot.")
        self.assertEqual(cast(SystemMock, model.map_hex).location, "trade")


class ToTerminalTestCase(unittest.TestCase):
    """Tests Model.to_terminal() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        ToTerminalTestCase.model = Model(ControlsMock([]))
        ToTerminalTestCase.model.map_hex = SystemMock()

    def test_to_depot(self) -> None:
        """Tests successfully moving to the trade depot."""
        model = ToTerminalTestCase.model
        result = model.to_terminal()
        self.assertEqual(result, "Entered the Uranus passenger terminal.")
        self.assertEqual(cast(SystemMock, model.map_hex).location, "terminal")


class ToStarportTestCase(unittest.TestCase):
    """Tests Model.to_starport() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        ToStarportTestCase.model = Model(ControlsMock([]))
        ToStarportTestCase.model.map_hex = SystemMock()

    def test_to_depot(self) -> None:
        """Tests successfully moving to the trade depot."""
        model = ToStarportTestCase.model
        result = model.to_starport()
        self.assertEqual(result, "Entered the Uranus starport.")
        self.assertEqual(cast(SystemMock, model.map_hex).location, "starport")


class LiftoffTestCase(unittest.TestCase):
    """Tests Model.liftoff() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        LiftoffTestCase.model = Model(ControlsMock([]))
        LiftoffTestCase.model.ship = ShipMock()
        LiftoffTestCase.model.map_hex = SystemMock()

    def test_liftoff_with_drive_failure(self) -> None:
        """Tests attempting to lift off from the starport when drives need repair."""
        model = LiftoffTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.liftoff()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")

        model.ship.repair_status = RepairStatus.PATCHED
        result = model.liftoff()
        self.assertEqual(result, "Successfully lifted off to orbit from Uranus.")

        cast(SystemMock, model.map_hex).location = "starport"
        model.ship.repair_status = RepairStatus.REPAIRED
        result = model.liftoff()
        self.assertEqual(result, "Successfully lifted off to orbit from Uranus.")

    def test_liftoff_with_no_passengers(self) -> None:
        """Tests successful lift off from the starport with no booked passengers."""
        model = LiftoffTestCase.model

        self.assertEqual(model.ship.total_passenger_count, 0)

        result = model.liftoff()
        self.assertEqual(result, "Successfully lifted off to orbit from Uranus.")

    # pylint: disable=W0212
    # W0212: access to a protected member _add_passengers of a client class
    def test_liftoff_with_passengers(self) -> None:
        """Tests successful lift off from the starport with booked passengers."""
        model = LiftoffTestCase.model
        destination = SystemMock("Jupiter")
        passengers = [Passenger(Passage.MIDDLE, destination)]
        model._add_passengers(passengers)

        self.assertEqual(model.ship.total_passenger_count, 1)

        result = model.liftoff()
        self.assertEqual(result, "Boarding 1 passenger for Jupiter." +
                                 "\nSuccessfully lifted off to orbit from Uranus.")

        passengers = [Passenger(Passage.MIDDLE, destination)]
        model._add_passengers(passengers)

        self.assertEqual(model.ship.total_passenger_count, 2)

        result = model.liftoff()
        self.assertEqual(result, "Boarding 2 passengers for Jupiter." +
                                 "\nSuccessfully lifted off to orbit from Uranus.")

    # low passengers
