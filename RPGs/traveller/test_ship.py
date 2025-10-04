"""Contains tests for the ship module."""
import unittest
from ship import Ship, Pilot, Engineer, Medic, Steward
from financials import Credits
from cargo import Freight

class ShipTestCase(unittest.TestCase):
    """Tests Ship class."""

    class CargoMock:
        """Mocks a cargo interface for testing."""

        def __init__(self, quantity):
            self.quantity = quantity
        @property
        def tonnage(self):
            return self.quantity

    class FreightMock:
        """Mocks a freight interface for testing."""

        def __init__(self, destination):
            self.destination_world = destination

    class PassengerMock:
        """Mocks a passenger interface for testing."""

        def __init__(self, destination):
            self.destination = destination

    def setUp(self):
        ShipTestCase.ship = Ship()

    def test_ship_string(self):
        self.assertEqual(f"{ShipTestCase.ship}",
                         "Weaselfish -- Type A Free Trader\n"
                         "200 tons : 1G : jump-1\n"
                         "4 crew, 6 passenger staterooms, 20 low berths\n"
                         "Cargo hold 82 tons, fuel tank 30 tons")

    def test_cargo_hold_reporting(self):
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
        cargo1 = ShipTestCase.CargoMock(1)
        cargo2 = ShipTestCase.CargoMock(1)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(ShipTestCase.ship.free_space(), 81)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(ShipTestCase.ship.free_space(), 80)
        self.assertEqual(len(ShipTestCase.ship.hold), 2)

    def test_unloading_cargo(self):
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

    @unittest.skip("test has side effects: input & printing")
    def test_refuel(self):
        self.assertEqual(ShipTestCase.ship.current_fuel, 0)
        cost = ShipTestCase.ship.refuel("A")
        self.assertEqual(ShipTestCase.ship.current_fuel, 30)
        self.assertEqual(cost, Credits(15000))    # 'yes' case
        cost = ShipTestCase.ship.refuel("A")
        self.assertEqual(cost, Credits(0))        # full tank case

    @unittest.skip("test has side effects: input & printing")
    def test_recharge(self):
        self.assertEqual(ShipTestCase.ship.life_support_level, 0)
        cost = ShipTestCase.ship.recharge()
        self.assertEqual(ShipTestCase.ship.life_support_level, 100)
        self.assertEqual(cost, Credits(22000))    # 'yes' case
        cost = ShipTestCase.ship.recharge()
        self.assertEqual(cost, Credits(0))        # full life support case

    def test_trade_skill(self):
        self.assertEqual(ShipTestCase.ship.trade_skill(), 1)

    def test_crew_salary(self):
        self.assertEqual(ShipTestCase.ship.crew_salary(), Credits(15000))

    def test_loan_payment(self):
        self.assertEqual(ShipTestCase.ship.loan_payment(), Credits(154500))

    def test_maintenance_cost(self):
        self.assertEqual(ShipTestCase.ship.maintenance_cost(), Credits(37080))

    def test_destination(self):
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
            ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination between Freight and Passengers!")

    def test_sufficient_jump_fuel(self):
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
        ship = ShipTestCase.ship
        ship.life_support_level = 100

        self.assertTrue(ship.sufficient_life_support())

        ship.life_support_level = 99
        self.assertFalse(ship.sufficient_life_support())
        self.assertEqual(ship.insufficient_life_support_message(),
                         "Insufficient life support to survive jump.\n" +
                         "Life support is at 99%.")

    def test_invalid_freight_and_passengers(self):
        ship = ShipTestCase.ship
        self.assertEqual(ship.destination, None)

        ship.load_cargo(Freight(1, "Pluto", "Uranus"))
        ship.passengers += [ShipTestCase.PassengerMock("Jupiter")]
        with self.assertRaises(ValueError) as context:
            ship.destination
        self.assertEqual(f"{context.exception}",
                         "More than one destination " +
                         "between Freight and Passengers!")

class PilotTestCase(unittest.TestCase):
    """Tests Pilot class."""

    def test_salary(self):
        self.assertEqual(Pilot(1).salary(), Credits(6000))
        self.assertEqual(Pilot(2).salary(), Credits(6600))
        self.assertEqual(Pilot(3).salary(), Credits(7200))

class EngineerTestCase(unittest.TestCase):
    """Tests Engineer class."""

    def test_salary(self):
        self.assertEqual(Engineer(1).salary(), Credits(4000))
        self.assertEqual(Engineer(2).salary(), Credits(4400))
        self.assertEqual(Engineer(3).salary(), Credits(4800))

class MedicTestCase(unittest.TestCase):
    """Tests Medic class."""

    def test_salary(self):
        self.assertEqual(Medic(1).salary(), Credits(2000))
        self.assertEqual(Medic(2).salary(), Credits(2200))
        self.assertEqual(Medic(3).salary(), Credits(2400))

class StewardTestCase(unittest.TestCase):
    """Tests Steward class."""

    def test_salary(self):
        self.assertEqual(Steward(1).salary(), Credits(3000))
        self.assertEqual(Steward(2).salary(), Credits(3300))
        self.assertEqual(Steward(3).salary(), Credits(3600))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

