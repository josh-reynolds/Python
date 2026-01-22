"""Contains tests for the ship module."""
import unittest
from test.mock import ObserverMock, SystemMock, CargoMock, FreightMock
from test.mock import PassengerMock, ControlsMock
from src.credits import Credits
from src.ship import Ship, FuelQuality, RepairStatus, ship_from

# pylint: disable=R0904
# R0904: Too many public methods
class ShipTestCase(unittest.TestCase):
    """Tests Ship class."""

    ship: Ship = Ship("Type A Free Trader")

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
        cargo1 = CargoMock(20)
        cargo2 = CargoMock(50)
        self.assertEqual(ShipTestCase.ship.cargo_hold(), [])
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 1)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[0], cargo1)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 2)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[1], cargo2)

    def test_loading_cargo(self) -> None:
        """Test loading cargo into the hold."""
        cargo1 = CargoMock(1)
        cargo2 = CargoMock(1)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(ShipTestCase.ship.free_space(), 81)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(ShipTestCase.ship.free_space(), 80)
        self.assertEqual(len(ShipTestCase.ship.hold), 2)

    def test_unloading_cargo(self) -> None:
        """Test unloading cargo from the hold."""
        cargo = CargoMock(20)
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

    def test_recharge(self) -> None:
        """Test recharging the Ship's life support."""
        ship = ShipTestCase.ship
        ship.controls = ControlsMock(['y', 'n'])
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

        ship.load_cargo(CargoMock(20))
        self.assertEqual(ship.destination, None)

        ship.load_cargo(FreightMock(SystemMock("Uranus")))
        ship.load_cargo(FreightMock(SystemMock("Uranus")))
        self.assertEqual(ship.destination, SystemMock("Uranus"))

        ship.load_cargo(CargoMock(20))
        self.assertEqual(ship.destination, SystemMock("Uranus"))

        self.assertEqual(len(ship.hold), 4)

        ship.load_cargo(FreightMock(SystemMock("Jupiter")))
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
        ship.current_life_support = 140
        print(ship.life_support_level)

        self.assertTrue(ship.sufficient_life_support())

        ship.current_life_support = 139
        self.assertFalse(ship.sufficient_life_support())
        self.assertEqual(ship.insufficient_life_support_message(),
                         "Insufficient life support to survive jump.\n" +
                         "Life support is at 99%.")

    def test_invalid_freight_and_passengers(self) -> None:
        """Test trapping of invalid Freight/Passenger combinations."""
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(FreightMock(SystemMock("Uranus")))
        ship.passengers += [PassengerMock("Jupiter")]
        with self.assertRaises(ValueError) as context:
            _ = ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination " +
                         "between Freight and Passengers!")

    def test_warn_if_not_contracted(self) -> None:
        """Test warning message if destination does not match the contract."""
        ship = ShipTestCase.ship
        view = ObserverMock()
        ship.add_view(view)

        contract = SystemMock("Uranus")
        destination = SystemMock("Jupiter")

        ship.load_cargo(FreightMock(contract))
        self.assertEqual(ship.destination, contract)

        ship.warn_if_not_contracted(destination)
        self.assertEqual(view.message,
                         "Warning: your contracted destination is Uranus not Jupiter.")
        self.assertEqual(view.priority, "red")

    def test_check_failure_post_jump(self) -> None:
        """Test drive failure check after jump."""
        ship = ShipTestCase.ship
        view = ObserverMock()
        ship.add_view(view)

        ship.fuel_quality = FuelQuality.UNREFINED
        ship.unrefined_jump_counter = 10
        ship.check_failure_post_jump()
        self.assertEqual(ship.repair_status, RepairStatus.BROKEN)
        self.assertEqual(view.message, "Warning: drive failure!")
        self.assertEqual(view.priority, "red")

    def test_check_failure_pre_jump(self) -> None:
        """Test drive failure check before jump."""
        ship = ShipTestCase.ship
        view = ObserverMock()
        ship.add_view(view)

        for _ in range(144):                         # 1 in 36 chance of failure
            ship.check_failure_pre_jump("red")
        self.assertEqual(ship.repair_status, RepairStatus.BROKEN)
        self.assertEqual(view.message, "Warning: drive failure! Unable to jump.")
        self.assertEqual(view.priority, "red")

    def test_add_view(self) -> None:
        """Test adding an view to the Ship."""
        ship = ShipTestCase.ship
        view = ObserverMock()

        ship.add_view(view)
        self.assertEqual(ship.views[0], view)

    def test_message_views(self) -> None:
        """Test sending messages to views."""
        ship = ShipTestCase.ship
        view = ObserverMock()
        ship.add_view(view)

        ship.message_views("This is a test")
        self.assertEqual(view.message, "This is a test")
        self.assertEqual(view.priority, "")

        ship.message_views("This is another test", "yellow")
        self.assertEqual(view.message, "This is another test")
        self.assertEqual(view.priority, "yellow")

        ship.message_views("Yet another test", "red")
        self.assertEqual(view.message, "Yet another test")
        self.assertEqual(view.priority, "red")

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
        expected.current_life_support = 100
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
                         "life support must be in the range 0-140: '-1'")

        string = "Weaselfish - 0 - R - 0 - R - 141"
        with self.assertRaises(ValueError) as context:
            _ = ship_from(string, "Type A Free Trader")
        self.assertEqual(f"{context.exception}",
                         "life support must be in the range 0-140: '141'")

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
