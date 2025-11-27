"""Contains tests for the ship module."""
import unittest
from typing import Any
from test.mock import ObserverMock, SystemMock
from src.cargo import Cargo
from src.coordinate import Coordinate
from src.credits import Credits
from src.freight import Freight
from src.passengers import Passenger
from src.ship import Ship, Pilot, Engineer, Medic, Steward, FuelQuality, RepairStatus
from src.ship import ship_from, ship_model_from, ShipModel, get_ship_models
from src.star_system import StarSystem, UWP

# pylint: disable=R0904
# R0904: Too many public methods
class ShipTestCase(unittest.TestCase):
    """Tests Ship class."""

    ship: Ship = Ship("Type A Free Trader")

    # pylint: disable=R0903,W0231
    # R0903: Too few public methods (1/2)
    # W0231: __init__ method from base class 'Cargo' is not called
    class CargoMock(Cargo):
        """Mocks a cargo interface for testing."""

        def __init__(self, quantity: int) -> None:
            """Create an instance of a CargoMock object."""
            self.quantity = quantity

        @property
        def tonnage(self) -> int:
            """Return the quantity of the CargoMock object."""
            return self.quantity

        def __eq__(self, other: Any) -> bool:
            """Test if two CargoMock objects are equal."""
            if type(other) is type(self):
                return self.quantity == other.quantity
            return NotImplemented

    # pylint: disable=R0903
    # R0903: Too few public methods (0/2)
    class FreightMock:
        """Mocks a freight interface for testing."""

        def __init__(self, destination: Any) -> None:
            """Create an instance of a FreightMock object."""
            self.destination_world = destination

    # pylint: disable=R0903,W0231
    # R0903: Too few public methods (1/2)
    # W0231: __init__ method from base class 'Passenger' is not called
    class PassengerMock(Passenger):
        """Mocks a passenger interface for testing."""

        def __init__(self, destination: Any) -> None:
            """Create an instance of a PassengerMock object."""
            self.destination = destination

    # pylint: disable=R0903
    # R0903: Too few public methods (0/2)
    class SystemMock(StarSystem):
        """Mocks a StarSystem interface for testing."""

        def __init__(self, name: str) -> None:
            """Create an instance of a SystemMock object."""
            super().__init__(name, Coordinate(1,1,1),
                             UWP("A",1,1,1,1,1,1,1), True)

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class ControlsMock:
        """Mocks a controller for testing."""

        def __init__(self, commands: Any) -> None:
            """Create an instance of a ControlsMock."""
            self.commands = commands
            self.invocations = 0

        def get_input(self, _constraint: str, _prompt: str) -> str:
            """Return the next command in the list."""
            # not safe if we call too many times...
            response = self.commands[self.invocations]
            self.invocations += 1
            return response

    def setUp(self) -> None:
        """Create a fixture for testing the Ship class."""
        ShipTestCase.ship = Ship("Type A Free Trader")

    def test_ship_string(self) -> None:
        """Test the string representation of a Ship object."""
        self.assertEqual(f"{ShipTestCase.ship}",
                         "Weaselfish -- Type A Free Trader\n"
                         "200 tons : 1G : jump-1\n"
                         "4 crew, 6 passenger staterooms, 20 low berths\n"
                         "Cargo hold 82 tons, fuel tank 30 tons")

    def test_cargo_hold_reporting(self) -> None:
        """Test reporting of cargo hold contents."""
        cargo1 = ShipTestCase.CargoMock(20)
        cargo2 = ShipTestCase.CargoMock(50)
        self.assertEqual(ShipTestCase.ship.cargo_hold(), [])
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 1)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[0], cargo1)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 2)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[1], cargo2)

    def test_loading_cargo(self) -> None:
        """Test loading cargo into the hold."""
        cargo1 = ShipTestCase.CargoMock(1)
        cargo2 = ShipTestCase.CargoMock(1)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(ShipTestCase.ship.free_space(), 81)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(ShipTestCase.ship.free_space(), 80)
        self.assertEqual(len(ShipTestCase.ship.hold), 2)

    def test_unloading_cargo(self) -> None:
        """Test unloading cargo from the hold."""
        cargo = ShipTestCase.CargoMock(20)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo)
        self.assertEqual(ShipTestCase.ship.free_space(), 62)
        self.assertEqual(len(ShipTestCase.ship.hold), 1)
        ShipTestCase.ship.unload_cargo(cargo, 10)
        self.assertEqual(ShipTestCase.ship.free_space(), 72)
        self.assertEqual(len(ShipTestCase.ship.hold), 1)
        ShipTestCase.ship.unload_cargo(cargo, 10)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        self.assertEqual(len(ShipTestCase.ship.hold), 0)

    def test_refuel(self) -> None:
        """Test refuelling the Ship."""
        ship = ShipTestCase.ship
        ship.controls = ShipTestCase.ControlsMock(['n', 'y'])
        self.assertEqual(ship.current_fuel, 0)

        cost = ship.refuel("A")
        self.assertEqual(ship.current_fuel, 0)
        self.assertEqual(cost, Credits(0))        # 'no' case

        self.assertEqual(ship.current_fuel, 0)
        cost = ship.refuel("A")
        self.assertEqual(ship.current_fuel, 30)
        self.assertEqual(cost, Credits(15000))    # 'yes' case

        cost = ship.refuel("A")
        self.assertEqual(cost, Credits(0))        # full tank case

    def test_recharge(self) -> None:
        """Test recharging the Ship's life support."""
        ship = ShipTestCase.ship
        ship.controls = ShipTestCase.ControlsMock(['n', 'y'])
        self.assertEqual(ShipTestCase.ship.life_support_level, 0)

        cost = ShipTestCase.ship.recharge()
        self.assertEqual(ShipTestCase.ship.life_support_level, 0)
        self.assertEqual(cost, Credits(0))        # 'no' case

        cost = ShipTestCase.ship.recharge()
        self.assertEqual(ShipTestCase.ship.life_support_level, 100)
        self.assertEqual(cost, Credits(22000))    # 'yes' case

        cost = ShipTestCase.ship.recharge()
        self.assertEqual(cost, Credits(0))        # full life support case

    def test_trade_skill(self) -> None:
        """Test retrieval of the Ship's trade skill value."""
        self.assertEqual(ShipTestCase.ship.trade_skill(), 0)

    def test_crew_salary(self) -> None:
        """Test paying the monthly crew salary."""
        self.assertEqual(ShipTestCase.ship.crew_salary(), Credits(15000))

    def test_loan_payment(self) -> None:
        """Test paying the monthly loan."""
        self.assertEqual(ShipTestCase.ship.loan_payment(), Credits(154500))

    def test_maintenance_cost(self) -> None:
        """Test paying the annual maintenance fee."""
        self.assertEqual(ShipTestCase.ship.maintenance_cost(), Credits(37080))

    def test_destination(self) -> None:
        """Test determination of contracted destination."""
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(ShipTestCase.CargoMock(20))
        self.assertEqual(ship.destination, None)

        ship.load_cargo(Freight(1, SystemMock("Pluto"), SystemMock("Uranus")))
        ship.load_cargo(Freight(1, SystemMock("Pluto"), SystemMock("Uranus")))
        self.assertEqual(ship.destination, SystemMock("Uranus"))

        ship.load_cargo(ShipTestCase.CargoMock(20))
        self.assertEqual(ship.destination, SystemMock("Uranus"))

        self.assertEqual(len(ship.hold), 4)

        ship.load_cargo(Freight(1, SystemMock("Pluto"), SystemMock("Jupiter")))
        with self.assertRaises(ValueError) as context:
            _ = ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination between Freight and Passengers!")

    def test_sufficient_jump_fuel(self) -> None:
        """Test determination of sufficient fuel to execute a jump."""
        ship = ShipTestCase.ship
        ship.current_fuel = 30

        self.assertTrue(ship.sufficient_jump_fuel())

        ship.current_fuel = 19
        self.assertFalse(ship.sufficient_jump_fuel())
        self.assertEqual(ship.insufficient_jump_fuel_message(),
                         "Insufficient fuel. Jump requires 20 tons, only 19 tons in tanks.")

        ship.current_fuel = 20
        self.assertTrue(ship.sufficient_jump_fuel())

    def test_sufficient_life_support(self) -> None:
        """Test determination of sufficient life support to execute a jump."""
        ship = ShipTestCase.ship
        ship.life_support_level = 100

        self.assertTrue(ship.sufficient_life_support())

        ship.life_support_level = 99
        self.assertFalse(ship.sufficient_life_support())
        self.assertEqual(ship.insufficient_life_support_message(),
                         "Insufficient life support to survive jump.\n" +
                         "Life support is at 99%.")

    def test_invalid_freight_and_passengers(self) -> None:
        """Test trapping of invalid Freight/Passenger combinations."""
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(Freight(1, SystemMock("Pluto"), SystemMock("Uranus")))
        ship.passengers += [ShipTestCase.PassengerMock("Jupiter")]
        with self.assertRaises(ValueError) as context:
            _ = ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination " +
                         "between Freight and Passengers!")

    def test_warn_if_not_contracted(self) -> None:
        """Test warning message if destination does not match the contract."""
        ship = ShipTestCase.ship
        observer = ObserverMock()
        ship.add_observer(observer)

        source = ShipTestCase.SystemMock("Pluto")
        contract = ShipTestCase.SystemMock("Uranus")
        destination = ShipTestCase.SystemMock("Jupiter")

        ship.load_cargo(Freight(1, source, contract))
        self.assertEqual(ship.destination, contract)

        ship.warn_if_not_contracted(destination)
        self.assertEqual(observer.message,
                         "Warning: your contracted destination is Uranus not Jupiter.")
        self.assertEqual(observer.priority, "red")

    def test_check_failure_post_jump(self) -> None:
        """Test drive failure check after jump."""
        ship = ShipTestCase.ship
        observer = ObserverMock()
        ship.add_observer(observer)

        ship.fuel_quality = FuelQuality.UNREFINED
        ship.unrefined_jump_counter = 10
        ship.check_failure_post_jump()
        self.assertEqual(ship.repair_status, RepairStatus.BROKEN)
        self.assertEqual(observer.message, "Warning: drive failure!")
        self.assertEqual(observer.priority, "red")

    def test_check_failure_pre_jump(self) -> None:
        """Test drive failure check before jump."""
        ship = ShipTestCase.ship
        observer = ObserverMock()
        ship.add_observer(observer)

        for _ in range(144):                         # 1 in 36 chance of failure
            ship.check_failure_pre_jump("red")
        self.assertEqual(ship.repair_status, RepairStatus.BROKEN)
        self.assertEqual(observer.message, "Warning: drive failure! Unable to jump.")
        self.assertEqual(observer.priority, "red")

    def test_add_observer(self) -> None:
        """Test adding an observer to the Ship."""
        ship = ShipTestCase.ship
        observer = ObserverMock()

        ship.add_observer(observer)
        self.assertEqual(ship.observers[0], observer)

    def test_message_observers(self) -> None:
        """Test sending messages to observers."""
        ship = ShipTestCase.ship
        observer = ObserverMock()
        ship.add_observer(observer)

        ship.message_observers("This is a test")
        self.assertEqual(observer.message, "This is a test")
        self.assertEqual(observer.priority, "")

        ship.message_observers("This is another test", "yellow")
        self.assertEqual(observer.message, "This is another test")
        self.assertEqual(observer.priority, "yellow")

        ship.message_observers("Yet another test", "red")
        self.assertEqual(observer.message, "Yet another test")
        self.assertEqual(observer.priority, "red")

    # pylint: disable=R0915
    # R0915: Too many statements (88/50)
    def test_ship_from(self) -> None:
        """Test importing a Ship from a string."""
        string = "Weaselfish - 0 - R - 0 - R - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        self.assertEqual(actual, expected)

        string = "Funkstar - 0 - R - 0 - R - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.name = "Funkstar"
        self.assertEqual(actual, expected)

        string = "Weaselfish - 30 - R - 0 - R - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.fuel = 30
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - U - 0 - R - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.fuel_quality = FuelQuality.UNREFINED
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - R - 1 - R - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.unrefined_jump_counter = 1
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - R - 0 - P - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.repair_status = RepairStatus.PATCHED
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - R - 0 - B - 0"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.repair_status = RepairStatus.BROKEN
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - R - 0 - R - 100"
        actual = ship_from(string, "Type A Free Trader")
        expected = Ship("Type A Free Trader")
        expected.life_support_level = 100
        self.assertEqual(actual, expected)

        string = "Weaselfish - 0 - R - 0 - R - 0 - extra"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "input string has extra data: 'Weaselfish - 0 - R - 0 - R - 0 - extra'")

        string = "Weaselfish - 0 - R - 0 - R"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "input string is missing data: 'Weaselfish - 0 - R - 0 - R'")

        string = "Weaselfish - 31 - R - 0 - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "fuel level in input string is larger than the fuel tank: '31'")

        string = "Weaselfish - -1 - R - 0 - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "fuel level must be a positive integer: '-1'")

        string = "Weaselfish - m - R - 0 - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "Weaselfish - 0 - X - 0 - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "unknown fuel quality in saved data: 'X'")

        string = "Weaselfish - 0 - R - -1 - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "jump counter must be a positive integer: '-1'")

        string = "Weaselfish - 0 - R - m - R - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "Weaselfish - 0 - R - 0 - X - 0"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "unknown repair status in saved data: 'X'")

        string = "Weaselfish - 0 - R - 0 - R - -1"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "life support must be in the range 0-100: '-1'")

        string = "Weaselfish - 0 - R - 0 - R - 101"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "life support must be in the range 0-100: '101'")

        string = "Weaselfish - 0 - R - 0 - R - m"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

    def test_encode(self) -> None:
        """Test exporting a Ship to a string."""
        ship = Ship("Type A Free Trader")

        actual = ship.encode()
        expected = "Weaselfish - 0 - R - 0 - R - 0"
        self.assertEqual(actual, expected)

        ship.fuel_quality = FuelQuality.UNREFINED
        actual = ship.encode()
        expected = "Weaselfish - 0 - U - 0 - R - 0"
        self.assertEqual(actual, expected)

        ship.repair_status = RepairStatus.PATCHED
        actual = ship.encode()
        expected = "Weaselfish - 0 - U - 0 - P - 0"
        self.assertEqual(actual, expected)

        ship.repair_status = RepairStatus.BROKEN
        actual = ship.encode()
        expected = "Weaselfish - 0 - U - 0 - B - 0"
        self.assertEqual(actual, expected)

        ship2 = ship_from(actual, "Type A Free Trader")
        self.assertEqual(ship, ship2)


class PilotTestCase(unittest.TestCase):
    """Tests Pilot class."""

    def test_salary(self) -> None:
        """Test retrieval of Pilot salary value."""
        self.assertEqual(Pilot(1).salary(), Credits(6000))
        self.assertEqual(Pilot(2).salary(), Credits(6600))
        self.assertEqual(Pilot(3).salary(), Credits(7200))

class EngineerTestCase(unittest.TestCase):
    """Tests Engineer class."""

    def test_salary(self) -> None:
        """Test retrieval of Engineer salary value."""
        self.assertEqual(Engineer(1).salary(), Credits(4000))
        self.assertEqual(Engineer(2).salary(), Credits(4400))
        self.assertEqual(Engineer(3).salary(), Credits(4800))

class MedicTestCase(unittest.TestCase):
    """Tests Medic class."""

    def test_salary(self) -> None:
        """Test retrieval of Medic salary value."""
        self.assertEqual(Medic(1).salary(), Credits(2000))
        self.assertEqual(Medic(2).salary(), Credits(2200))
        self.assertEqual(Medic(3).salary(), Credits(2400))

class StewardTestCase(unittest.TestCase):
    """Tests Steward class."""

    def test_salary(self) -> None:
        """Test retrieval of Steward salary value."""
        self.assertEqual(Steward(1).salary(), Credits(3000))
        self.assertEqual(Steward(2).salary(), Credits(3300))
        self.assertEqual(Steward(3).salary(), Credits(3600))

class ShipModelTestCase(unittest.TestCase):
    """Tests ShipModel class."""

    def test_ship_model_from(self) -> None:
        """Test creation of a ShipModel from a name string."""
        actual = ship_model_from("Type A Free Trader")
        expected = ShipModel()
        self.assertEqual(actual, expected)

        actual = ship_model_from("Type S Scout/Courier")
        expected = ShipModel()
        expected.name = "Type S Scout/Courier"
        expected.hull = 100
        expected.passenger_berths = 3
        expected.low_berths = 0
        expected.acceleration = 2
        expected.streamlined = True
        expected.hold_size = 3
        expected.fuel_tank = 40
        expected.jump_range = 2
        expected.jump_fuel_cost = 20
        expected.trip_fuel_cost = 20
        expected.base_price = Credits(29_430_000)
        self.assertEqual(actual, expected)

    def test_get_ship_models(self) -> None:
        """Test retrieval of available ship models."""
        actual = get_ship_models()
        expected = ["Type A Free Trader", "Type S Scout/Courier", "Type Y Yacht"]
        self.assertEqual(actual, expected)
