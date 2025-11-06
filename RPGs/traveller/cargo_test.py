"""Contains tests for the cargo module."""
import unittest
from typing import List, Any
from cargo import Cargo, CargoDepot, Freight, Baggage, Passenger, PassageClass
from cargo import passenger_from, freight_from, baggage_from, cargo_from
from coordinate import Coordinate
from financials import Credits
from mock import ObserverMock, DateMock, SystemMock
from star_system import StarSystem
from utilities import dictionary_from

class CargoTestCase(unittest.TestCase):
    """Tests Cargo class."""

    def test_cargo_quantity(self) -> None:
        """Test whether cargo quantity is determined correctly."""
        cargo1 = Cargo("Foo", '10', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity, 10)

        cargo2 = Cargo("Bar", "1Dx1", Credits(10), 1, {}, {})
        self.assertGreater(cargo2.quantity, 0)
        self.assertLess(cargo2.quantity, 7)

        cargo3 = Cargo("Baz", "1Dx10", Credits(10), 1, {}, {})
        self.assertEqual(cargo3.quantity % 10, 0)
        self.assertGreater(cargo3.quantity, 9)
        self.assertLess(cargo3.quantity, 61)

    def test_cargo_quantity_string(self) -> None:
        """Test the string representation of cargo quantity."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity_string(1), "1 ton")
        self.assertEqual(cargo1.quantity_string(5), "5 tons")

        cargo2 = Cargo("Bar", '1', Credits(10), 5, {}, {})
        self.assertEqual(cargo2.quantity_string(1), "1 (5 tons/item)")

    def test_cargo_tonnage(self) -> None:
        """Test whether cargo tonnage is calculated correctly."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.tonnage, 1)

        cargo2 = Cargo("Bar", '1', Credits(10), 5, {}, {})
        self.assertEqual(cargo2.tonnage, 5)

        cargo3 = Cargo("Baz", '20', Credits(10), 1, {}, {})
        self.assertEqual(cargo3.tonnage, 20)

        cargo4 = Cargo("Boo", '20', Credits(10), 10, {}, {})
        self.assertEqual(cargo4.tonnage, 200)

    def test_cargo_string(self) -> None:
        """Test a Cargo's string representation."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo1}", "Foo - 1 ton - 10 Cr/ton")

        cargo2 = Cargo("Bar", '5', Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo2}", "Bar - 5 tons - 10 Cr/ton")

        cargo3 = Cargo("Baz", '5', Credits(10), 5, {}, {})
        self.assertEqual(f"{cargo3}", "Baz - 5 (5 tons/item) - 10 Cr/item")

        # pylint: disable=R0903
        # R0903: Too few public methods (0/2)
        class Location(StarSystem):
            """Mocks a location interface for testing."""

            # pylint: disable=W0231
            # W0231: __init__ method from base class 'StarSystem' is not called
            def __init__(self, name: str) -> None:
                self.name = name

        location = Location("Uranus")
        cargo4 = Cargo("Boo", '100', Credits(10), 1, {}, {}, location)
        self.assertEqual(f"{cargo4}", "Boo - 100 tons - 10 Cr/ton (Uranus)")

    def test_cargo_from(self) -> None:
        """Test importing Cargo from a parsed string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source}

        actual = cargo_from("Meat", 10, "(0, 0, 0)", systems)
        expected = Cargo("Meat", "10", Credits(1500), 1,
                         dictionary_from("{Ag:-2,Na:2,In:3}"),
                         dictionary_from("{Ag:-2,In:2,Po:1}"))
        self.assertEqual(actual, expected)


class CargoDepotTestCase(unittest.TestCase):
    """Tests CargoDepot class."""

    depot = CargoDepot(SystemMock(), DateMock(1))

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class ControlsMock:
        """Mocks a controller for testing."""

        def __init__(self, commands: List[Any]) -> None:
            """Create an instance of a ControlsMock."""
            self.commands = commands

        def get_input(self, _constraint: str, _prompt: str) -> str:
            """Return the next command in the list."""
            # not safe if we call too many times...
            return self.commands.pop()

    def setUp(self) -> None:
        """Create a test fixture for testing CargoDepots."""
        CargoDepotTestCase.depot = CargoDepot(SystemMock(), DateMock(1))

    def test_on_notify(self) -> None:
        """Test notification behavior of a CargoDepot."""
        depot = CargoDepotTestCase.depot
        cargo = depot.cargo
        self.assertEqual(depot.refresh_date.value, 1)   #type: ignore[attr-defined]

        date = DateMock(7)
        depot.on_notify(date)
        self.assertEqual(depot.refresh_date.value, 1)   #type: ignore[attr-defined]
        self.assertEqual(cargo, depot.cargo)

        date = DateMock(8)
        depot.on_notify(date)
        self.assertEqual(depot.refresh_date.value, 8)   #type: ignore[attr-defined]
        self.assertNotEqual(cargo, depot.cargo)

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_price_modifiers of a client class
    def test_get_price_modifiers(self) -> None:
        """Test lookup of price modifiers."""
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", "1", Credits(1), 1, {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1},
                                                  {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1})

        modifier = depot._get_price_modifiers(cargo, "purchase")
        self.assertEqual(modifier, 6)

        modifier = depot._get_price_modifiers(cargo, "sale")
        self.assertEqual(modifier, 6)

    def test_get_cargo_lot(self) -> None:
        """Test selection of cargo lots."""
        depot = CargoDepotTestCase.depot
        depot.controls = CargoDepotTestCase.ControlsMock([2, 1, 0, 7])
        observer = ObserverMock()
        depot.add_observer(observer)
        cargo_list = ["a", "b", "c"]

        item = depot.get_cargo_lot(cargo_list, "buy")    #type: ignore[arg-type]
        self.assertEqual(observer.message, "That is not a valid cargo ID.")
        self.assertEqual(observer.priority, "")

        item = depot.get_cargo_lot(cargo_list, "buy")    #type: ignore[arg-type]
        self.assertEqual(item, "a")

        item = depot.get_cargo_lot(cargo_list, "buy")    #type: ignore[arg-type]
        self.assertEqual(item, "b")

        item = depot.get_cargo_lot(cargo_list, "buy")    #type: ignore[arg-type]
        self.assertEqual(item, "c")

    def test_get_cargo_quantity(self) -> None:
        """Test selection of cargo quantity."""
        depot = CargoDepotTestCase.depot
        depot.controls = CargoDepotTestCase.ControlsMock([9, 1, 0, -1, 11])
        observer = ObserverMock()
        depot.add_observer(observer)
        cargo = Cargo("Test", '10', Credits(1), 1, {}, {})

        amount = depot.get_cargo_quantity("buy", cargo)
        self.assertEqual(amount, None)
        self.assertEqual(observer.message,
                         "There is not enough available. Specify a lower quantity.")
        self.assertEqual(observer.priority, "")

        amount = depot.get_cargo_quantity("buy", cargo)
        self.assertEqual(amount, None)
        self.assertEqual(observer.message, "Quantity needs to be a positive number.")
        self.assertEqual(observer.priority, "")

        amount = depot.get_cargo_quantity("buy", cargo)
        self.assertEqual(amount, None)
        self.assertEqual(observer.message, "Quantity needs to be a positive number.")
        self.assertEqual(observer.priority, "")

        amount = depot.get_cargo_quantity("buy", cargo)
        self.assertEqual(amount, 1)

        amount = depot.get_cargo_quantity("buy", cargo)
        self.assertEqual(amount, 9)

    def test_invalid_cargo_origin(self) -> None:
        """Test validation of cargo origin."""
        depot = CargoDepotTestCase.depot
        self.assertEqual(depot.system.name, "Uranus")
        observer = ObserverMock()
        depot.add_observer(observer)

        # pylint: disable=R0903
        # R0903: Too few public methods (1/2)
        class Location(StarSystem):
            """Mocks a location interface for testing."""

            # pylint: disable=W0231
            # W0231: __init__ method from base class 'StarSystem' is not called
            def __init__(self, name):
                self.name = name

            def __eq__(self, other):
                return self.name == other.name

        location1 = Location("Jupiter")
        cargo1 = Cargo("Test", '10', Credits(1), 1, {}, {}, location1)
        self.assertFalse(depot.invalid_cargo_origin(cargo1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        cargo2 = Cargo("Test", '10', Credits(1), 1, {}, {})
        self.assertFalse(depot.invalid_cargo_origin(cargo2))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        location2 = Location("Uranus")
        cargo3 = Cargo("Test", '10', Credits(1), 1, {}, {}, location2)
        self.assertTrue(depot.invalid_cargo_origin(cargo3))
        self.assertEqual(observer.message,
                         "You cannot resell cargo on the world where it was purchased.")
        self.assertEqual(observer.priority, "")

    def test_get_broker(self) -> None:
        """Test choosing a broker."""
        depot = CargoDepotTestCase.depot
        scenarios = ['n', 4, 5, 'y', 'y', 4, 5, 'y', 'n', 1, 'y', 'y', 1, 0, 'y', 'n']
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = ObserverMock()
        depot.add_observer(observer)

        # n
        result = depot.get_broker()
        self.assertEqual(result, 0)

        # y 0 1 y
        result = depot.get_broker()
        self.assertEqual(result, 1)

        # y 1 n
        result = depot.get_broker()
        self.assertEqual(result, 0)

        # y 5 4 y
        result = depot.get_broker()
        self.assertEqual(result, 4)

        # y 5 4 n
        result = depot.get_broker()
        self.assertEqual(result, 0)

    def test_insufficient_hold_space(self) -> None:
        """Test validation of cargo hold space."""
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", '10', Credits(1), 1, {}, {})
        observer = ObserverMock()
        depot.add_observer(observer)

        self.assertFalse(depot.insufficient_hold_space(cargo, 10, 10))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        self.assertTrue(depot.insufficient_hold_space(cargo, 10, 0))
        self.assertEqual(observer.message, "You only have 0 tons free.")
        self.assertEqual(observer.priority, "")

    def test_determine_price(self) -> None:
        """Test calculation of sale & purchase prices.

        Since the prices are randomly determined, the tests below need
        to account for variable output. Also, the determine_price()
        method will set a priority based on whether the price is good
        or bad - so validating the observer.priority field is tricky.
        """
        # TO_DO: monkeypatch die_roll() so we can get deterministic
        #        results for testing
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", '10', Credits(1), 1, {}, {})
        observer = ObserverMock()
        depot.add_observer(observer)

        price = depot.determine_price("sale", cargo, 10, 0)
        self.assertTrue(isinstance(price, Credits))
        self.assertGreaterEqual(price, Credits(4))
        self.assertLessEqual(price, Credits(40))
        self.assertEqual(observer.message[:31], "Sale price of that quantity is ")
        #self.assertEqual(observer.priority, "")

        self.assertEqual(cargo.price_adjustment, 0)
        price = depot.determine_price("purchase", cargo, 10, 0)
        self.assertTrue(isinstance(price, Credits))
        self.assertGreaterEqual(price, Credits(4))
        self.assertLessEqual(price, Credits(40))
        self.assertGreater(cargo.price_adjustment, 0)
        self.assertEqual(observer.message[:35], "Purchase price of that quantity is ")
        #self.assertEqual(observer.priority, "")

        price2 = depot.determine_price("purchase", cargo, 10, 0)
        self.assertEqual(price2, price)
        self.assertEqual(observer.message[:35], "Purchase price of that quantity is ")
        #self.assertEqual(observer.priority, "")

    def test_insufficient_funds(self) -> None:
        """Test validation of bank balance."""
        depot = CargoDepotTestCase.depot
        observer = ObserverMock()
        depot.add_observer(observer)

        result = depot.insufficient_funds(Credits(1), Credits(1))
        self.assertFalse(result)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        result = depot.insufficient_funds(Credits(1), Credits(2))
        self.assertFalse(result)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        result = depot.insufficient_funds(Credits(2), Credits(1))
        self.assertTrue(result)
        self.assertEqual(observer.message, "Your available balance is 1 Cr.")
        self.assertEqual(observer.priority, "")

    def test_broker_fee(self) -> None:
        """Test calculation of broker fees."""
        depot = CargoDepotTestCase.depot
        observer = ObserverMock()
        depot.add_observer(observer)

        fee = depot.broker_fee(0, Credits(100))
        self.assertEqual(fee, Credits(0))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        fee = depot.broker_fee(1, Credits(100))
        self.assertEqual(fee, Credits(5))
        self.assertEqual(observer.message, "Deducting 5 Cr broker fee for skill 1.")
        self.assertEqual(observer.priority, "")

        fee = depot.broker_fee(4, Credits(100))
        self.assertEqual(fee, Credits(20))
        self.assertEqual(observer.message, "Deducting 20 Cr broker fee for skill 4.")
        self.assertEqual(observer.priority, "")

    def test_confirm_transaction(self) -> None:
        """Test transaction confirmation."""
        depot = CargoDepotTestCase.depot
        scenarios = ['n', 'y']
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = ObserverMock()
        depot.add_observer(observer)
        cargo = Cargo("Test", '10', Credits(1), 1, {}, {})

        result = depot.confirm_transaction("purchase", cargo, 1, Credits(1))
        self.assertTrue(result)

        result = depot.confirm_transaction("purchase", cargo, 1, Credits(1))
        self.assertFalse(result)
        self.assertEqual(observer.message, "Cancelling purchase.")
        self.assertEqual(observer.priority, "")

    def test_remove_cargo(self) -> None:
        """Test removal of cargo from the depot or cargo hold."""
        depot = CargoDepotTestCase.depot
        cargo1 = Cargo("Test", '10', Credits(1), 1, {}, {})
        cargo2 = Cargo("Test", '20', Credits(1), 1, {}, {})
        cargo3 = Cargo("Test", '30', Credits(1), 1, {}, {})
        source = [cargo1, cargo2]

        depot.remove_cargo(source, cargo3, 10)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 0)
        self.assertEqual(source[1].quantity, 20)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 1)
        self.assertEqual(source[1].quantity, 19)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 19)
        self.assertEqual(len(source), 1)

        depot.remove_cargo(source, cargo1, 11)
        self.assertEqual(len(source), 0)

    # pylint: disable=W0212
    # W0212: Access to a protected member _determine_cargo of a client class
    def test_determine_cargo(self) -> None:
        """Test random determination of cargo lots."""
        depot = CargoDepotTestCase.depot

        cargo = depot._determine_cargo()
        self.assertEqual(len(cargo), 1)
        self.assertTrue(isinstance(cargo[0], Cargo))

    def test_get_available_freight(self) -> None:
        """Test listing of freight in the depot."""
        depot = CargoDepotTestCase.depot
        scenarios = [2, 1, 0]
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = ObserverMock()
        depot.add_observer(observer)
        world1 = SystemMock()
        world1.name = "Pluto"
        world1.coordinate = Coordinate(2,2,2)
        world2 = SystemMock()
        world2.name = "Jupiter"
        world2.coordinate = Coordinate(1,1,1)
        destinations = [world1, world2]

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, Coordinate(2,2,2))
        self.assertTrue(isinstance(freight, list))

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, Coordinate(1,1,1))
        self.assertTrue(isinstance(freight, list))

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, None)
        self.assertTrue(freight is None)
        self.assertEqual(observer.message, "That is not a valid destination number.")

    # pylint: disable=W0212, R0915
    # W0212: Access to a protected member _passenger_origin_table of a client class
    # R0915: Too many statements (58/50)
    def test_passenger_origin_table(self) -> None:
        """Test calculation of passengers by origin world."""
        depot = CargoDepotTestCase.depot

        self.assertEqual(depot._passenger_origin_table(0), (0,0,0))
        self.assertEqual(depot._passenger_origin_table(1), (0,0,0))

        self.assertGreater(depot._passenger_origin_table(2)[0], -6)
        self.assertLess(depot._passenger_origin_table(2)[0], 6)
        self.assertGreater(depot._passenger_origin_table(2)[1], -6)
        self.assertLess(depot._passenger_origin_table(2)[1], 6)
        self.assertGreater(depot._passenger_origin_table(2)[2], -4)
        self.assertLess(depot._passenger_origin_table(2)[2], 18)

        self.assertGreater(depot._passenger_origin_table(3)[0], -10)
        self.assertLess(depot._passenger_origin_table(3)[0], 17)
        self.assertGreater(depot._passenger_origin_table(3)[1], -11)
        self.assertLess(depot._passenger_origin_table(3)[1], 11)
        self.assertGreater(depot._passenger_origin_table(3)[2], -4)
        self.assertLess(depot._passenger_origin_table(3)[2], 18)

        self.assertGreater(depot._passenger_origin_table(4)[0], -16)
        self.assertLess(depot._passenger_origin_table(4)[0], 16)
        self.assertGreater(depot._passenger_origin_table(4)[1], -16)
        self.assertLess(depot._passenger_origin_table(4)[1], 16)
        self.assertGreater(depot._passenger_origin_table(4)[2], -3)
        self.assertLess(depot._passenger_origin_table(4)[2], 24)

        self.assertGreater(depot._passenger_origin_table(5)[0], -10)
        self.assertLess(depot._passenger_origin_table(5)[0], 17)
        self.assertGreater(depot._passenger_origin_table(5)[1], -10)
        self.assertLess(depot._passenger_origin_table(5)[1], 17)
        self.assertGreater(depot._passenger_origin_table(5)[2], -3)
        self.assertLess(depot._passenger_origin_table(5)[2], 24)

        self.assertGreater(depot._passenger_origin_table(6)[0], -10)
        self.assertLess(depot._passenger_origin_table(6)[0], 17)
        self.assertGreater(depot._passenger_origin_table(6)[1], -10)
        self.assertLess(depot._passenger_origin_table(6)[1], 17)
        self.assertGreater(depot._passenger_origin_table(6)[2], 2)
        self.assertLess(depot._passenger_origin_table(6)[2], 19)

        self.assertGreater(depot._passenger_origin_table(7)[0], -10)
        self.assertLess(depot._passenger_origin_table(7)[0], 17)
        self.assertGreater(depot._passenger_origin_table(7)[1], -10)
        self.assertLess(depot._passenger_origin_table(7)[1], 17)
        self.assertGreater(depot._passenger_origin_table(7)[2], 2)
        self.assertLess(depot._passenger_origin_table(7)[2], 19)

        self.assertGreater(depot._passenger_origin_table(8)[0], -5)
        self.assertLess(depot._passenger_origin_table(8)[0], 12)
        self.assertGreater(depot._passenger_origin_table(8)[1], -10)
        self.assertLess(depot._passenger_origin_table(8)[1], 17)
        self.assertGreater(depot._passenger_origin_table(8)[2], 3)
        self.assertLess(depot._passenger_origin_table(8)[2], 25)

        self.assertGreater(depot._passenger_origin_table(9)[0], -5)
        self.assertLess(depot._passenger_origin_table(9)[0], 12)
        self.assertGreater(depot._passenger_origin_table(9)[1], -5)
        self.assertLess(depot._passenger_origin_table(9)[1], 12)
        self.assertGreater(depot._passenger_origin_table(9)[2], 3)
        self.assertLess(depot._passenger_origin_table(9)[2], 25)

        self.assertGreater(depot._passenger_origin_table(10)[0], -5)
        self.assertLess(depot._passenger_origin_table(10)[0], 12)
        self.assertGreater(depot._passenger_origin_table(10)[1], -5)
        self.assertLess(depot._passenger_origin_table(10)[1], 12)
        self.assertGreater(depot._passenger_origin_table(10)[2], 3)
        self.assertLess(depot._passenger_origin_table(10)[2], 25)

    def test_passenger_destination_table(self) -> None:
        """Test determination of passenger count modifiers by destination world."""
        depot = CargoDepotTestCase.depot

        counts = (4,4,4)
        self.assertEqual(depot._passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(depot._passenger_destination_table(1, counts), (0,0,0))
        self.assertEqual(depot._passenger_destination_table(2, counts), (3,2,0))
        self.assertEqual(depot._passenger_destination_table(3, counts), (3,3,1))
        self.assertEqual(depot._passenger_destination_table(4, counts), (3,3,2))
        self.assertEqual(depot._passenger_destination_table(5, counts), (4,3,3))
        self.assertEqual(depot._passenger_destination_table(6, counts), (4,4,3))
        self.assertEqual(depot._passenger_destination_table(7, counts), (4,4,4))
        self.assertEqual(depot._passenger_destination_table(8, counts), (5,4,4))
        self.assertEqual(depot._passenger_destination_table(9, counts), (5,5,4))
        self.assertEqual(depot._passenger_destination_table(10, counts), (5,5,6))

        counts = (0,0,0)
        self.assertEqual(depot._passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(depot._passenger_destination_table(2, counts), (0,0,0))

        counts = (50,50,50)
        self.assertEqual(depot._passenger_destination_table(7, counts), (40,40,40))

    # pylint: disable=W0212
    # W0212: Access to a protected member _refresh_freight of a client class
    def test_refresh_freight(self) -> None:
        """Test refreshing freight allotments."""
        depot = CargoDepotTestCase.depot
        freight = depot.freight
        depot._refresh_freight([SystemMock()])
        self.assertNotEqual(depot.freight, freight)

    # pylint: disable=W0212
    # W0212: Access to a protected member _refresh_passengers of a client class
    def test_refresh_passengers(self) -> None:
        """Test refreshing prospective passengers."""
        depot = CargoDepotTestCase.depot
        passengers = depot.passengers
        depot._refresh_passengers([SystemMock()])
        self.assertNotEqual(depot.passengers, passengers)

    def test_get_available_passengers(self) -> None:
        """Test listing of passengers in the terminal."""
        depot = CargoDepotTestCase.depot
        scenarios = [2, 1, 0]
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = ObserverMock()
        depot.add_observer(observer)
        world1 = SystemMock()
        world1.name = "Pluto"
        world1.coordinate = Coordinate(2,2,2)
        world2 = SystemMock()
        world2.name = "Jupiter"
        world2.coordinate = Coordinate(1,1,1)
        destinations = [world1, world2]

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, Coordinate(2,2,2))
        self.assertTrue(isinstance(passengers, tuple))

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, Coordinate(1,1,1))
        self.assertTrue(isinstance(passengers, tuple))

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, None)
        self.assertTrue(passengers is None)
        self.assertEqual(observer.message, "That is not a valid destination number.")


class FreightTestCase(unittest.TestCase):
    """Tests Freight class."""

    def test_freight_string(self) -> None:
        """Test the string representation of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight}",
                         "Freight : 10 tons : Pluto -> Uranus")

    def test_freight_repr(self) -> None:
        """Test the repr string of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight!r}",
                         "Freight(10, SystemMock('Pluto'), SystemMock('Uranus'))")

    def test_freight_from(self) -> None:
        """Test importing Freight from a parsed string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source}

        actual = freight_from(10, "(1, 0, -1)", "(0, 0, 0)", systems)
        expected = Freight(10, source, destination)
        self.assertEqual(actual, expected)

        actual = freight_from(100, "(0, 0, 0)", "(1, 0, -1)", systems)
        expected = Freight(100, destination, source)
        self.assertEqual(actual, expected)

        with self.assertRaises(ValueError) as context:
            _ = freight_from(100, "(1, -1, 0)", "(1, 0, -1)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(100, "(0, 0, 0)", "(1, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(0, "(1, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "tonnage must be a positive number: '0'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(-10, "(1, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "tonnage must be a positive number: '-10'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(m, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(1, 0, -1)", "(0, m, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: ' m'")

        with self.assertRaises(ValueError) as context:
            _ = freight_from(10, "(1, 1, 1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")


class BaggageTestCase(unittest.TestCase):
    """Tests Baggage class."""

    def test_baggage_string(self) -> None:
        """Test the string representation of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage}",
                         "Baggage : 1 ton : Pluto -> Uranus")

    def test_baggage_repr(self) -> None:
        """Test the repr string of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage!r}",
                         "Baggage(SystemMock('Pluto'), SystemMock('Uranus'))")

    def test_baggage_from(self) -> None:
        """Test importing Baggage from a parsed string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source}

        actual = baggage_from("(1, 0, -1)", "(0, 0, 0)", systems)
        expected = Baggage(source, destination)
        self.assertEqual(actual, expected)

        actual = baggage_from("(0, 0, 0)", "(1, 0, -1)", systems)
        expected = Baggage(destination, source)
        self.assertEqual(actual, expected)

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, -1, 0)", "(1, 0, -1)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(0, 0, 0)", "(1, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(m, 0, -1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, 0, -1)", "(0, m, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: ' m'")

        with self.assertRaises(ValueError) as context:
            _ = baggage_from("(1, 1, 1)", "(0, 0, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")


class PassengerTestCase(unittest.TestCase):
    """Tests Passenger class."""

    def test_passenger_str(self) -> None:
        """Test the string representation of a Passenger object."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger}", "Low passage to Uranus")

    def test_passenger_repr(self) -> None:
        """Test the repr string of a Passenger object."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger!r}", "Passenger(<PassageClass.LOW: 2>, SystemMock('Uranus'))")

    def test_passenger_guess_survivors(self) -> None:
        """Test Passenger guesses as to number of low lottery survivors."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        for _ in range(1000):
            passenger.guess_survivors(10)
            guess = passenger.guess
            self.assertGreaterEqual(guess, 0)       #type: ignore[arg-type]
            self.assertLessEqual(guess, 10)         #type: ignore[arg-type]

    # pylint: disable=R0915
    # R0915: Too many statements (52/50)
    def test_from_string(self) -> None:
        """Test importing a Passenger from a string."""
        string = "high - (0, 0, 0)"
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : destination}
        actual = passenger_from(string, systems)
        expected = Passenger(PassageClass.HIGH, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "High passage to Jupiter")

        string = "middle - (1, 0, -1)"
        destination = SystemMock("Mars")
        destination.coordinate = Coordinate(1,0,-1)
        systems[Coordinate(1,0,-1)] = destination
        actual = passenger_from(string, systems)
        expected = Passenger(PassageClass.MIDDLE, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "Middle passage to Mars")

        string = "low - (-1, 0, 1)"
        destination = SystemMock("Venus")
        destination.coordinate = Coordinate(-1,0,1)
        systems[Coordinate(-1,0,1)] = destination
        actual = passenger_from(string, systems)
        expected = Passenger(PassageClass.LOW, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "Low passage to Venus")

        string = "HIgh - (0, 0, 0)"
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        actual = passenger_from(string, systems)
        expected = Passenger(PassageClass.HIGH, destination)
        self.assertEqual(actual, expected)
        self.assertEqual(f"{actual}", "High passage to Jupiter")

        string = "bollix - (0, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "unrecognized passage class: 'bollix'")

        string = "High - (0, 0, 0) - some - more"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "input string has extra data: 'High - (0, 0, 0) - some - more'")

        string = "High (0, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "input string is missing data: 'High (0, 0, 0)'")

        string = "High - (m, 0, 0)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "High - (1, 1, 1)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")

        string = "High - (2, 0, -2)"
        with self.assertRaises(ValueError) as context:
            _ = passenger_from(string, systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(2, 0, -2)'")

    def test_encode(self) -> None:
        """Test importing a Passenger from a string."""
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(PassageClass.HIGH, destination)

        actual = passenger.encode()
        expected = "high - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "High passage to Jupiter")

        destination = SystemMock("Neptune")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(PassageClass.MIDDLE, destination)

        actual = passenger.encode()
        expected = "middle - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "Middle passage to Neptune")

        destination = SystemMock("Uranus")
        destination.coordinate = Coordinate(0,0,0)
        passenger = Passenger(PassageClass.LOW, destination)

        actual = passenger.encode()
        expected = "low - (0, 0, 0)"
        self.assertEqual(actual, expected)
        self.assertEqual(f"{passenger}", "Low passage to Uranus")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
