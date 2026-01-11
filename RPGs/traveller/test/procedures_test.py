"""Contains tests for game procedures."""
import unittest
from typing import cast
from test.mock import ControlsMock, ShipMock, CalendarMock, SystemMock
from test.mock import ObserverMock, FinancialsMock, DeepSpaceMock
from src.credits import Credits
from src.format import BOLD_RED, END_FORMAT
from src.imperial_date import ImperialDate
from src.model import Model, GuardClauseFailure
from src.ship import RepairStatus, FuelQuality

class DamageControlTestCase(unittest.TestCase):
    """Tests Model.damage_control() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        DamageControlTestCase.model = Model(ControlsMock([]))
        DamageControlTestCase.model.ship = ShipMock()
        DamageControlTestCase.model.date = CalendarMock()

    def test_damage_control_with_repaired_ship(self) -> None:
        """Tests attempting to perform damage control when the ship is fully repaired."""
        model = DamageControlTestCase.model

        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)

        result = model.damage_control()

        self.assertEqual(result, "Your ship is not damaged.")

    def test_damage_control_with_patched_ship(self) -> None:
        """Tests attempting to perform damage control when the ship is partially repaired."""
        model = DamageControlTestCase.model
        model.ship.repair_status = RepairStatus.PATCHED

        result = model.damage_control()

        self.assertEqual(result, "Further repairs require starport facilities.")

    def test_damage_control_success(self) -> None:
        """Tests successful damage control."""
        model = DamageControlTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN
        for crewmember in model.ship.crew:
            crewmember.engineer_skill = 8                     # guarantee the repair succeeds

        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.damage_control()

        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        model.ship.repair_status = RepairStatus.PATCHED
        self.assertEqual(result, "Ship partially repaired. Visit a starport for further work.")

    def test_damage_control_failure(self) -> None:
        """Tests failed damage control."""
        model = DamageControlTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN
        for crewmember in model.ship.crew:
            crewmember.engineer_skill = -4                     # guarantee the repair fails

        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.damage_control()

        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        model.ship.repair_status = RepairStatus.PATCHED
        self.assertEqual(result, "No progress today. Drives are still out of commission.")


class RepairShipTestCase(unittest.TestCase):
    """Tests Model.repair_ship() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        RepairShipTestCase.model = Model(ControlsMock([]))
        RepairShipTestCase.model.ship = ShipMock()
        RepairShipTestCase.model.map_hex = SystemMock()
        RepairShipTestCase.model.date = CalendarMock()

    # TO_DO: should shift the failure cases here to use GuardClauseFailure
    # pylint: disable=W0212
    # W0212: access to a protected member _starport of a client class
    def test_repair_with_no_facilities(self) -> None:
        """Tests attempting to perform repairs at a low-grade starport."""
        model = RepairShipTestCase.model

        cast(SystemMock, model.map_hex)._starport = "D"
        result = model.repair_ship()
        self.assertEqual(result, "No repair facilities available at starport D.")

        cast(SystemMock, model.map_hex)._starport = "E"
        result = model.repair_ship()
        self.assertEqual(result, "No repair facilities available at starport E.")

        cast(SystemMock, model.map_hex)._starport = "X"
        result = model.repair_ship()
        self.assertEqual(result, "No repair facilities available at starport X.")

    def test_repair_with_repaired_ship(self) -> None:
        """Tests attempting to perform repairs when ship is not damaged."""
        model = RepairShipTestCase.model

        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)

        result = model.repair_ship()
        self.assertEqual(result, "Your ship is not damaged.")

    def test_repair_with_damaged_ship(self) -> None:
        """Tests successful repairs when ship is damaged."""
        model = RepairShipTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.repair_ship()
        self.assertEqual(result, "Your ship is fully repaired and decontaminated.")
        self.assertEqual(model.date.current_date, ImperialDate(8, 1105))
        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)

        model.ship.repair_status = RepairStatus.PATCHED
        result = model.repair_ship()
        self.assertEqual(result, "Your ship is fully repaired and decontaminated.")
        self.assertEqual(model.date.current_date, ImperialDate(15, 1105))
        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)

    def test_repair_with_polluted_tanks(self) -> None:
        """Tests successful repairs when fuel tanks are polluted."""
        model = RepairShipTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN
        model.ship.fuel_quality = FuelQuality.UNREFINED

        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.repair_ship()
        self.assertEqual(result, "Your ship is fully repaired and decontaminated.")
        self.assertEqual(model.date.current_date, ImperialDate(8, 1105))
        self.assertEqual(model.ship.fuel_quality, FuelQuality.REFINED)
        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)


class RefuelTestCase(unittest.TestCase):
    """Tests Model.refuel() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        RefuelTestCase.model = Model(ControlsMock([]))
        RefuelTestCase.model.ship = ShipMock()
        RefuelTestCase.model.map_hex = SystemMock()
        RefuelTestCase.model.financials = FinancialsMock()

    # pylint: disable=W0212
    # W0212: access to a protected member _starport of a client class
    def test_refuel_with_no_facilities(self) -> None:
        """Tests attempting to refuel at a low-grade starport."""
        model = RefuelTestCase.model

        cast(SystemMock, model.map_hex)._starport = "E"
        with self.assertRaises(GuardClauseFailure) as context:
            model.refuel()
        self.assertEqual(f"{context.exception}",
                         "No fuel is available at starport E.")

        cast(SystemMock, model.map_hex)._starport = "X"
        with self.assertRaises(GuardClauseFailure) as context:
            model.refuel()
        self.assertEqual(f"{context.exception}",
                         "No fuel is available at starport X.")

    # pylint: disable=W0212
    # W0212: access to a protected member _starport of a client class
    def test_refuel_with_mid_facilities(self) -> None:
        """Tests attempting to refuel at a medium-grade starport."""
        model = RefuelTestCase.model
        view = ObserverMock()
        model.views = [view]
        model.controls = ControlsMock(['y', 'y', 'y', 'n', 'n'])
        model.financials.balance = Credits(5000)

        self.assertEqual(model.fuel_level(), 0)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.REFINED)
        self.assertEqual(len(model.financials.ledger), 0)

        cast(SystemMock, model.map_hex)._starport = "C"
        result = model.refuel()
        self.assertEqual(view.message, "Note: only unrefined fuel available at this facility.")
        self.assertEqual(model.controls.invocations, 1)

        cast(SystemMock, model.map_hex)._starport = "D"
        result = model.refuel()
        self.assertEqual(view.message, "Note: only unrefined fuel available at this facility.")
        self.assertEqual(model.controls.invocations, 2)

        cast(SystemMock, model.map_hex)._starport = "C"
        result = model.refuel()
        # TO_DO: ObserverMock only keeps the last messsage, should accumulate a list
        self.assertEqual(view.message, "Charging 3,000 Cr for refuelling.")
        self.assertEqual(model.controls.invocations, 3)
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.UNREFINED)
        self.assertEqual(model.balance, Credits(2000))
        self.assertEqual(len(model.financials.ledger), 1)
        self.assertEqual(model.financials.ledger[0],
                         "1\t - 3,000 Cr\t - \t\t - 2,000 Cr\t - Uranus\t - refuelling")
        self.assertEqual(result, "Your ship is fully refuelled.")

        cast(SystemMock, model.map_hex)._starport = "D"
        model.ship.current_fuel = 20
        model.ship.fuel_quality = FuelQuality.REFINED
        result = model.refuel()
        self.assertEqual(view.message, "Charging 1,000 Cr for refuelling.")
        self.assertEqual(model.controls.invocations, 4)
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.UNREFINED)
        self.assertEqual(model.balance, Credits(1000))
        self.assertEqual(len(model.financials.ledger), 2)
        self.assertEqual(model.financials.ledger[1],
                         "1\t - 1,000 Cr\t - \t\t - 1,000 Cr\t - Uranus\t - refuelling")
        self.assertEqual(result, "Your ship is fully refuelled.")

        with self.assertRaises(GuardClauseFailure) as context:
            model.refuel()
        self.assertEqual(f"{context.exception}",
                         "Fuel tank is already full.")

    # pylint: disable=W0212
    # W0212: access to a protected member _starport of a client class
    def test_refuel_with_high_facilities(self) -> None:
        """Tests attempting to refuel at a high-grade starport."""
        model = RefuelTestCase.model
        view = ObserverMock()
        model.views = [view]
        model.controls = ControlsMock(['y', 'y', 'y', 'n', 'n'])
        model.financials.balance = Credits(20000)

        self.assertEqual(model.fuel_level(), 0)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.REFINED)
        self.assertEqual(len(model.financials.ledger), 0)

        cast(SystemMock, model.map_hex)._starport = "A"
        result = model.refuel()
        self.assertEqual(view.message, "")
        self.assertEqual(model.controls.invocations, 1)

        cast(SystemMock, model.map_hex)._starport = "B"
        result = model.refuel()
        self.assertEqual(view.message, "")
        self.assertEqual(model.controls.invocations, 2)

        cast(SystemMock, model.map_hex)._starport = "A"
        result = model.refuel()
        # TO_DO: ObserverMock only keeps the last messsage, should accumulate a list
        self.assertEqual(view.message, "Charging 15,000 Cr for refuelling.")
        self.assertEqual(model.controls.invocations, 3)
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.REFINED)
        self.assertEqual(model.balance, Credits(5000))
        self.assertEqual(len(model.financials.ledger), 1)
        self.assertEqual(model.financials.ledger[0],
                         "1\t - 15,000 Cr\t - \t\t - 5,000 Cr\t - Uranus\t - refuelling")
        self.assertEqual(result, "Your ship is fully refuelled.")

        cast(SystemMock, model.map_hex)._starport = "B"
        model.ship.current_fuel = 20
        result = model.refuel()
        self.assertEqual(view.message, "Charging 5,000 Cr for refuelling.")
        self.assertEqual(model.controls.invocations, 4)
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.REFINED)
        self.assertEqual(model.balance, Credits(0))
        self.assertEqual(len(model.financials.ledger), 2)
        self.assertEqual(model.financials.ledger[1],
                         "1\t - 5,000 Cr\t - \t\t - 0 Cr\t - Uranus\t - refuelling")
        self.assertEqual(result, "Your ship is fully refuelled.")

        with self.assertRaises(GuardClauseFailure) as context:
            model.refuel()
        self.assertEqual(f"{context.exception}",
                         "Fuel tank is already full.")


class SkimTestCase(unittest.TestCase):
    """Tests Model.skim() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        SkimTestCase.model = Model(ControlsMock([]))
        SkimTestCase.model.ship = ShipMock()
        SkimTestCase.model.map_hex = SystemMock()
        SkimTestCase.model.date = CalendarMock()

    def test_skim_in_deep_space(self) -> None:
        """Tests attempting to skim in deep space."""
        model = SkimTestCase.model
        SkimTestCase.model.map_hex = DeepSpaceMock()

        with self.assertRaises(GuardClauseFailure) as context:
            model.skim()
        self.assertEqual(f"{context.exception}",
                         "You are stranded in deep space. No fuel skimming possible.")

    def test_skim_no_gas_giant(self) -> None:
        """Tests attempting to skim in StarSystem with no gas giant."""
        model = SkimTestCase.model
        cast(SystemMock, model.map_hex).gas_giant = False

        with self.assertRaises(GuardClauseFailure) as context:
            model.skim()
        self.assertEqual(f"{context.exception}",
                         "There is no gas giant in this system. No fuel skimming possible.")

    def test_skim_unstreamlined(self) -> None:
        """Tests attempting to skim in an unstreamlined ship."""
        model = SkimTestCase.model
        model.ship.model.streamlined = False

        with self.assertRaises(GuardClauseFailure) as context:
            model.skim()
        self.assertEqual(f"{context.exception}",
                         "Your ship is not streamlined and cannot skim fuel.")

    def test_skim_unmaneuverable(self) -> None:
        """Tests attempting to skim in a Ship that needs repairs."""
        model = SkimTestCase.model
        model.ship.repair_status = RepairStatus.BROKEN

        with self.assertRaises(GuardClauseFailure) as context:
            model.skim()
        self.assertEqual(f"{context.exception}",
                         f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")

    def test_skim_with_repaired_ship(self) -> None:
        """Tests successful fuel skimming from a gas giant in a fully-repaired Ship."""
        model = SkimTestCase.model
        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)
        self.assertEqual(model.fuel_level(), 0)
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.skim()
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.UNREFINED)
        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        self.assertEqual(result, "Your ship is fully refuelled.")

    def test_skim_with_patched_ship(self) -> None:
        """Tests successful fuel skimming from a gas giant in a partially-repaired Ship."""
        model = SkimTestCase.model
        model.ship.repair_status = RepairStatus.PATCHED
        self.assertEqual(model.fuel_level(), 0)
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        result = model.skim()
        self.assertEqual(model.fuel_level(), 30)
        self.assertEqual(model.ship.fuel_quality, FuelQuality.UNREFINED)
        self.assertEqual(model.date.current_date, ImperialDate(2, 1105))
        self.assertEqual(result, "Your ship is fully refuelled.")

    def test_skim_with_full_tanks(self) -> None:
        """Tests attempting to skim fuel from a gas giant when fuel tanks are full."""
        model = SkimTestCase.model
        model.ship.current_fuel = 30
        self.assertEqual(model.ship.repair_status, RepairStatus.REPAIRED)
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))

        with self.assertRaises(GuardClauseFailure) as context:
            model.skim()
        self.assertEqual(f"{context.exception}",
                         "Fuel tank is already full.")
        self.assertEqual(model.date.current_date, ImperialDate(1, 1105))


class WildernessRefuelTestCase(unittest.TestCase):
    """Tests Model.wilderness_refuel() method."""

    model: Model

    def setUp(self) -> None:
        """Create fixtures for testing."""
        WildernessRefuelTestCase.model = Model(ControlsMock([]))
        WildernessRefuelTestCase.model.ship = ShipMock()
        WildernessRefuelTestCase.model.map_hex = SystemMock()

    # pylint: disable=W0212
    # W0212: access to a protected member _hydrographics of a client class
    def test_wilderness_refuel_on_desert_world(self) -> None:
        """Tests attempting to wilderness refuel on a world with no water."""
        model = WildernessRefuelTestCase.model
        cast(SystemMock, model.map_hex)._hydrographics = 0

        with self.assertRaises(GuardClauseFailure) as context:
            model.wilderness_refuel()
        self.assertEqual(f"{context.exception}",
                         "No water available on this planet.")

    # success
    # full tanks
