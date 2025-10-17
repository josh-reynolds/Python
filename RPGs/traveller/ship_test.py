"""Contains tests for the ship module."""
import unittest
from cargo import Freight
from financials import Credits
from mock import ObserverMock
from ship import Ship, Pilot, Engineer, Medic, Steward, FuelQuality, RepairStatus
from star_system import StarSystem, UWP

class ShipTestCase(unittest.TestCase):
    """Tests Ship class."""

    ship: Ship = Ship()

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class CargoMock:
        """Mocks a cargo interface for testing."""

        def __init__(self, quantity):
            """Create an instance of a CargoMock object."""
            self.quantity = quantity

        @property
        def tonnage(self):
            """Return the quantity of the CargoMock object."""
            return self.quantity

    # pylint: disable=R0903
    # R0903: Too few public methods (0/2)
    class FreightMock:
        """Mocks a freight interface for testing."""

        def __init__(self, destination):
            """Create an instance of a FreightMock object."""
            self.destination_world = destination

    # pylint: disable=R0903
    # R0903: Too few public methods (0/2)
    class PassengerMock:
        """Mocks a passenger interface for testing."""

        def __init__(self, destination):
            """Create an instance of a PassengerMock object."""
            self.destination = destination

    # pylint: disable=R0903
    # R0903: Too few public methods (0/2)
    class SystemMock(StarSystem):
        """Mocks a StarSystem interface for testing."""

        def __init__(self, name):
            """Create an instance of a SystemMock object."""
            super().__init__(name, (1,1,1),
                             UWP("A",1,1,1,1,1,1,1), True)

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class ControlsMock:
        """Mocks a controller for testing."""

        def __init__(self, commands):
            """Create an instance of a ControlsMock."""
            self.commands = commands
            self.invocations = 0

        def get_input(self, _constraint: str, _prompt: str) -> str:
            """Return the next command in the list."""
            # not safe if we call too many times...
            response = self.commands[self.invocations]
            self.invocations += 1
            return response

    def setUp(self):
        """Create a fixture for testing the Ship class."""
        ShipTestCase.ship = Ship()

    def test_ship_string(self):
        """Test the string representation of a Ship object."""
        self.assertEqual(f"{ShipTestCase.ship}",
                         "Weaselfish -- Type A Free Trader\n"
                         "200 tons : 1G : jump-1\n"
                         "4 crew, 6 passenger staterooms, 20 low berths\n"
                         "Cargo hold 82 tons, fuel tank 30 tons")

    def test_cargo_hold_reporting(self):
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

    def test_loading_cargo(self):
        """Test loading cargo into the hold."""
        cargo1 = ShipTestCase.CargoMock(1)
        cargo2 = ShipTestCase.CargoMock(1)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(ShipTestCase.ship.free_space(), 81)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(ShipTestCase.ship.free_space(), 80)
        self.assertEqual(len(ShipTestCase.ship.hold), 2)

    def test_unloading_cargo(self):
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

    def test_refuel(self):
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

    def test_recharge(self):
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

    def test_trade_skill(self):
        """Test retrieval of the Ship's trade skill value."""
        self.assertEqual(ShipTestCase.ship.trade_skill(), 1)

    def test_crew_salary(self):
        """Test paying the monthly crew salary."""
        self.assertEqual(ShipTestCase.ship.crew_salary(), Credits(15000))

    def test_loan_payment(self):
        """Test paying the monthly loan."""
        self.assertEqual(ShipTestCase.ship.loan_payment(), Credits(154500))

    def test_maintenance_cost(self):
        """Test paying the annual maintenance fee."""
        self.assertEqual(ShipTestCase.ship.maintenance_cost(), Credits(37080))

    def test_destination(self):
        """Test determination of contracted destination."""
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(ShipTestCase.CargoMock(20))
        self.assertEqual(ship.destination, None)

        ship.load_cargo(Freight(1, "Pluto", "Uranus"))
        ship.load_cargo(Freight(1, "Pluto", "Uranus"))
        self.assertEqual(ship.destination, "Uranus")

        ship.load_cargo(ShipTestCase.CargoMock(20))
        self.assertEqual(ship.destination, "Uranus")

        self.assertEqual(len(ship.hold), 4)

        ship.load_cargo(Freight(1, "Pluto", "Jupiter"))
        with self.assertRaises(ValueError) as context:
            _ = ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination between Freight and Passengers!")

    def test_sufficient_jump_fuel(self):
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

    def test_sufficient_life_support(self):
        """Test determination of sufficient life support to execute a jump."""
        ship = ShipTestCase.ship
        ship.life_support_level = 100

        self.assertTrue(ship.sufficient_life_support())

        ship.life_support_level = 99
        self.assertFalse(ship.sufficient_life_support())
        self.assertEqual(ship.insufficient_life_support_message(),
                         "Insufficient life support to survive jump.\n" +
                         "Life support is at 99%.")

    def test_invalid_freight_and_passengers(self):
        """Test trapping of invalid Freight/Passenger combinations."""
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(Freight(1, "Pluto", "Uranus"))
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

    def test_add_observer(self):
        """Test adding an observer to the Ship."""
        ship = ShipTestCase.ship
        observer = ObserverMock()

        ship.add_observer(observer)
        self.assertEqual(ship.observers[0], observer)

    def test_message_observers(self):
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


class PilotTestCase(unittest.TestCase):
    """Tests Pilot class."""

    def test_salary(self):
        """Test retrieval of Pilot salary value."""
        self.assertEqual(Pilot(1).salary(), Credits(6000))
        self.assertEqual(Pilot(2).salary(), Credits(6600))
        self.assertEqual(Pilot(3).salary(), Credits(7200))

class EngineerTestCase(unittest.TestCase):
    """Tests Engineer class."""

    def test_salary(self):
        """Test retrieval of Engineer salary value."""
        self.assertEqual(Engineer(1).salary(), Credits(4000))
        self.assertEqual(Engineer(2).salary(), Credits(4400))
        self.assertEqual(Engineer(3).salary(), Credits(4800))

class MedicTestCase(unittest.TestCase):
    """Tests Medic class."""

    def test_salary(self):
        """Test retrieval of Medic salary value."""
        self.assertEqual(Medic(1).salary(), Credits(2000))
        self.assertEqual(Medic(2).salary(), Credits(2200))
        self.assertEqual(Medic(3).salary(), Credits(2400))

class StewardTestCase(unittest.TestCase):
    """Tests Steward class."""

    def test_salary(self):
        """Test retrieval of Steward salary value."""
        self.assertEqual(Steward(1).salary(), Credits(3000))
        self.assertEqual(Steward(2).salary(), Credits(3300))
        self.assertEqual(Steward(3).salary(), Credits(3600))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
