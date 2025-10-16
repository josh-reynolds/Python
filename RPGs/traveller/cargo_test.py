"""Contains tests for the cargo module."""
import unittest
from cargo import Cargo, CargoDepot, Freight, Baggage, Passenger, PassageClass
from financials import Credits

class CargoTestCase(unittest.TestCase):
    """Tests Cargo class."""

    def test_cargo_quantity(self):
        """Test whether cargo quantity is determined correctly."""
        cargo1 = Cargo("Foo", 10, Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity, 10)

        cargo2 = Cargo("Bar", "1Dx1", Credits(10), 1, {}, {})
        self.assertGreater(cargo2.quantity, 0)
        self.assertLess(cargo2.quantity, 7)

        cargo3 = Cargo("Baz", "1Dx10", Credits(10), 1, {}, {})
        self.assertEqual(cargo3.quantity % 10, 0)
        self.assertGreater(cargo3.quantity, 9)
        self.assertLess(cargo3.quantity, 61)

    def test_cargo_quantity_string(self):
        """Test the string representation of cargo quantity."""
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity_string(1), "1 ton")
        self.assertEqual(cargo1.quantity_string(5), "5 tons")

        cargo2 = Cargo("Bar", 1, Credits(10), 5, {}, {})
        self.assertEqual(cargo2.quantity_string(1), "1 (5 tons/item)")

    def test_cargo_tonnage(self):
        """Test whether cargo tonnage is calculated correctly."""
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(cargo1.tonnage, 1)

        cargo2 = Cargo("Bar", 1, Credits(10), 5, {}, {})
        self.assertEqual(cargo2.tonnage, 5)

        cargo3 = Cargo("Baz", 20, Credits(10), 1, {}, {})
        self.assertEqual(cargo3.tonnage, 20)

        cargo4 = Cargo("Boo", 20, Credits(10), 10, {}, {})
        self.assertEqual(cargo4.tonnage, 200)

    def test_cargo_string(self):
        """Test a Cargo's string representation."""
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo1}", "Foo - 1 ton - 10 Cr/ton")

        cargo2 = Cargo("Bar", 5, Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo2}", "Bar - 5 tons - 10 Cr/ton")

        cargo3 = Cargo("Baz", 5, Credits(10), 5, {}, {})
        self.assertEqual(f"{cargo3}", "Baz - 5 (5 tons/item) - 10 Cr/item")

        # pylint: disable=R0903
        # R0903: Too few public methods (0/2)
        class Location:
            """Mocks a location interface for testing."""

            def __init__(self, name):
                self.name = name

        location = Location("Uranus")
        cargo4 = Cargo("Boo", 100, Credits(10), 1, {}, {}, location)
        self.assertEqual(f"{cargo4}", "Boo - 100 tons - 10 Cr/ton (Uranus)")


class CargoDepotTestCase(unittest.TestCase):
    """Tests CargoDepot class."""

    class DateMock:
        """Mocks a date interface for testing."""

        def __init__(self, value):
            """Create an instance of a DateMock object."""
            self.value = value

        def copy(self):
            """Return a copy of a DateMock object."""
            return CargoDepotTestCase.DateMock(self.value)

        def __add__(self, rhs):
            """Add a value to a DateMock object."""
            return CargoDepotTestCase.DateMock(self.value + rhs)

        def __sub__(self, rhs):
            """Subtract a value from a DateMock object."""
            return self.value - rhs.value

        def __ge__(self, other):
            """Test whether another object is greater than or equal to a DateMock."""
            return self.value >= other.value

    # pylint: disable=R0903, R0902
    # R0903: Too few public methods (1/2)
    # R0902: Too many instance attributes (10/7)
    class SystemMock:
        """Mocks a system interface for testing."""

        def __init__(self):
            """Create an instance of a SystemMock object."""
            self.population = 5
            self.agricultural = True
            self.nonagricultural = True
            self.industrial = True
            self.nonindustrial = True
            self.rich = True
            self.poor = True
            self.name = "Uranus"
            self.coordinate = 111
            self.destinations = []

        def __repr__(self):
            """Return the string representation of a SystemMock object."""
            return f"{self.coordinate} - {self.name}"

    class ObserverMock:
        """Mocks an observer for testing."""

        def __init__(self):
            """Create an instance of an ObserverMock."""
            self.message = ""
            self.priority = ""

        def on_notify(self, message, priority):
            """On notification from Calendar, track the event."""
            self.message = message
            self.priority = priority

    class ControlsMock:
        """Mocks a controller for testing."""

        def __init__(self, commands):
            """Create an instance of a ControlsMock."""
            self.commands = commands

        def get_input(self, _constraint: str, _prompt: str) -> str:
            """Return the next command in the list."""
            # not safe if we call too many times...
            return self.commands.pop()

    def setUp(self):
        """Create a test fixture for testing CargoDepots."""
        CargoDepotTestCase.depot = CargoDepot(CargoDepotTestCase.SystemMock(),
                                              CargoDepotTestCase.DateMock(1))

    def test_on_notify(self):
        """Test notification behavior of a CargoDepot."""
        depot = CargoDepotTestCase.depot
        cargo = depot.cargo
        self.assertEqual(depot.refresh_date.value, 1)

        date = CargoDepotTestCase.DateMock(7)
        depot.on_notify(date)
        self.assertEqual(depot.refresh_date.value, 1)
        self.assertEqual(cargo, depot.cargo)

        date = CargoDepotTestCase.DateMock(8)
        depot.on_notify(date)
        self.assertEqual(depot.refresh_date.value, 8)
        self.assertNotEqual(cargo, depot.cargo)

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_price_modifiers of a client class
    def test_get_price_modifiers(self):
        """Test lookup of price modifiers."""
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", "1", Credits(1), 1, {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1},
                                                  {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1})

        modifier = depot._get_price_modifiers(cargo, "purchase")
        self.assertEqual(modifier, 6)

        modifier = depot._get_price_modifiers(cargo, "sale")
        self.assertEqual(modifier, 6)

    def test_get_cargo_lot(self):
        """Test selection of cargo lots."""
        depot = CargoDepotTestCase.depot
        depot.controls = CargoDepotTestCase.ControlsMock([2, 1, 0, 7])
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)
        cargo_list = ["a", "b", "c"]

        item = depot.get_cargo_lot(cargo_list, "buy")
        self.assertEqual(observer.message, "That is not a valid cargo ID.")
        self.assertEqual(observer.priority, "")

        item = depot.get_cargo_lot(cargo_list, "buy")
        self.assertEqual(item, "a")

        item = depot.get_cargo_lot(cargo_list, "buy")
        self.assertEqual(item, "b")

        item = depot.get_cargo_lot(cargo_list, "buy")
        self.assertEqual(item, "c")

    def test_get_cargo_quantity(self):
        """Test selection of cargo quantity."""
        depot = CargoDepotTestCase.depot
        depot.controls = CargoDepotTestCase.ControlsMock([9, 1, 0, -1, 11])
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

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

    def test_invalid_cargo_origin(self):
        """Test validation of cargo origin."""
        depot = CargoDepotTestCase.depot
        self.assertEqual(depot.system.name, "Uranus")
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)

        # pylint: disable=R0903
        # R0903: Too few public methods (1/2)
        class Location:
            """Mocks a location interface for testing."""

            def __init__(self, name):
                self.name = name

            def __eq__(self, other):
                return self.name == other.name

        location1 = Location("Jupiter")
        cargo1 = Cargo("Test", 10, Credits(1), 1, {}, {}, location1)
        self.assertFalse(depot.invalid_cargo_origin(cargo1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        cargo2 = Cargo("Test", 10, Credits(1), 1, {}, {})
        self.assertFalse(depot.invalid_cargo_origin(cargo2))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        location2 = Location("Uranus")
        cargo3 = Cargo("Test", 10, Credits(1), 1, {}, {}, location2)
        self.assertTrue(depot.invalid_cargo_origin(cargo3))
        self.assertEqual(observer.message,
                         "You cannot resell cargo on the world where it was purchased.")
        self.assertEqual(observer.priority, "")

    def test_get_broker(self):
        """Test choosing a broker."""
        depot = CargoDepotTestCase.depot
        scenarios = ['n', 4, 5, 'y', 'y', 4, 5, 'y', 'n', 1, 'y', 'y', 1, 0, 'y', 'n']
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = CargoDepotTestCase.ObserverMock()
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

    def test_insufficient_hold_space(self):
        """Test validation of cargo hold space."""
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)

        self.assertFalse(depot.insufficient_hold_space(cargo, 10, 10))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        self.assertTrue(depot.insufficient_hold_space(cargo, 10, 0))
        self.assertEqual(observer.message, "You only have 0 tons free.")
        self.assertEqual(observer.priority, "")

    def test_determine_price(self):
        """Test calculation of sale & purchase prices.

        Since the prices are randomly determined, the tests below need
        to account for variable output. Also, the determine_price()
        method will set a priority based on whether the price is good
        or bad - so validating the observer.priority field is tricky.
        """
        # TO_DO: monkeypatch die_roll() so we can get deterministic
        #        results for testing
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})
        observer = CargoDepotTestCase.ObserverMock()
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

    def test_insufficient_funds(self):
        """Test validation of bank balance."""
        depot = CargoDepotTestCase.depot
        observer = CargoDepotTestCase.ObserverMock()
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

    def test_broker_fee(self):
        """Test calculation of broker fees."""
        depot = CargoDepotTestCase.depot
        observer = CargoDepotTestCase.ObserverMock()
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

    def test_confirm_transaction(self):
        """Test transaction confirmation."""
        depot = CargoDepotTestCase.depot
        scenarios = ['n', 'y']
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

        result = depot.confirm_transaction("purchase", cargo, 1, Credits(1))
        self.assertTrue(result)

        result = depot.confirm_transaction("purchase", cargo, 1, Credits(1))
        self.assertFalse(result)
        self.assertEqual(observer.message, "Cancelling purchase.")
        self.assertEqual(observer.priority, "")

    def test_remove_cargo(self):
        """Test removal of cargo from the depot or cargo hold."""
        depot = CargoDepotTestCase.depot
        cargo1 = Cargo("Test", 10, Credits(1), 1, {}, {})
        cargo2 = Cargo("Test", 10, Credits(1), 1, {}, {})
        cargo3 = Cargo("Test", 10, Credits(1), 1, {}, {})
        source = [cargo1, cargo2]

        depot.remove_cargo(source, cargo3, 10)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 0)
        self.assertEqual(source[1].quantity, 10)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 1)
        self.assertEqual(source[1].quantity, 9)
        self.assertEqual(len(source), 2)

        depot.remove_cargo(source, cargo2, 9)
        self.assertEqual(len(source), 1)

        depot.remove_cargo(source, cargo1, 11)
        self.assertEqual(len(source), 0)

    # pylint: disable=W0212
    # W0212: Access to a protected member _determine_cargo of a client class
    def test_determine_cargo(self):
        """Test random determination of cargo lots."""
        depot = CargoDepotTestCase.depot

        cargo = depot._determine_cargo()
        self.assertEqual(len(cargo), 1)
        self.assertTrue(isinstance(cargo[0], Cargo))

    def test_get_available_freight(self):
        """Test listing of freight in the depot."""
        depot = CargoDepotTestCase.depot
        scenarios = [2, 1, 0]
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)
        world1 = CargoDepotTestCase.SystemMock()
        world1.name = "Pluto"
        world1.coordinate = 222
        world2 = CargoDepotTestCase.SystemMock()
        world2.name = "Jupiter"
        world2.coordinate = 111
        destinations = [world1, world2]

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, 222)
        self.assertTrue(isinstance(freight, list))

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, 111)
        self.assertTrue(isinstance(freight, list))

        coord, freight = depot.get_available_freight(destinations)
        self.assertEqual(coord, None)
        self.assertTrue(freight is None)
        self.assertEqual(observer.message, "That is not a valid destination number.")

    # pylint: disable=W0212, R0915
    # W0212: Access to a protected member _passenger_origin_table of a client class
    # R0915: Too many statements (58/50)
    def test_passenger_origin_table(self):
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

    def test_passenger_destination_table(self):
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
    def test_refresh_freight(self):
        """Test refreshing freight allotments."""
        depot = CargoDepotTestCase.depot
        freight = depot.freight
        depot._refresh_freight([CargoDepotTestCase.SystemMock()])
        self.assertNotEqual(depot.freight, freight)

    # pylint: disable=W0212
    # W0212: Access to a protected member _refresh_passengers of a client class
    def test_refresh_passengers(self):
        """Test refreshing prospective passengers."""
        depot = CargoDepotTestCase.depot
        passengers = depot.passengers
        depot._refresh_passengers([CargoDepotTestCase.SystemMock()])
        self.assertNotEqual(depot.passengers, passengers)

    def test_get_available_passengers(self):
        """Test listing of passengers in the terminal."""
        depot = CargoDepotTestCase.depot
        scenarios = [2, 1, 0]
        depot.controls = CargoDepotTestCase.ControlsMock(scenarios)
        observer = CargoDepotTestCase.ObserverMock()
        depot.add_observer(observer)
        world1 = CargoDepotTestCase.SystemMock()
        world1.name = "Pluto"
        world1.coordinate = 222
        world2 = CargoDepotTestCase.SystemMock()
        world2.name = "Jupiter"
        world2.coordinate = 111
        destinations = [world1, world2]

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, 222)
        self.assertTrue(isinstance(passengers, tuple))

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, 111)
        self.assertTrue(isinstance(passengers, tuple))

        coord, passengers = depot.get_available_passengers(destinations)
        self.assertEqual(coord, None)
        self.assertTrue(passengers is None)
        self.assertEqual(observer.message, "That is not a valid destination number.")


# pylint: disable=R0903
# R0903: Too few public methods (0/2)
class SystemMock:
    """Mocks a system interface for testing."""

    def __init__(self, name):
        """Create an instance of a SystemMock."""
        self.name = name

    def __repr__(self):
        """Return the string representation of a SystemMock object."""
        return f"SystemMock('{self.name}')"


class FreightTestCase(unittest.TestCase):
    """Tests Freight class."""

    def test_freight_string(self):
        """Test the string representation of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight}",
                         "Freight : 10 tons : Pluto -> Uranus")

    def test_freight_repr(self):
        """Test the repr string of a Freight object."""
        freight = Freight(10,
                          SystemMock("Pluto"),
                          SystemMock("Uranus"))
        self.assertEqual(f"{freight!r}",
                         "Freight(10, SystemMock('Pluto'), SystemMock('Uranus'))")

class BaggageTestCase(unittest.TestCase):
    """Tests Baggage class."""

    def test_baggage_string(self):
        """Test the string representation of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage}",
                         "Baggage : 1 ton : Pluto -> Uranus")

    def test_baggage_repr(self):
        """Test the repr string of a Baggage object."""
        baggage = Baggage( SystemMock("Pluto"), SystemMock("Uranus"))
        self.assertEqual(f"{baggage!r}",
                         "Baggage(SystemMock('Pluto'), SystemMock('Uranus'))")

class PassengerTestCase(unittest.TestCase):
    """Tests Passenger class."""

    def test_passenger_str(self):
        """Test the string representation of a Passenger object."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger}", "Low passage to Uranus")

    def test_passenger_repr(self):
        """Test the repr string of a Passenger object."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        self.assertEqual(f"{passenger!r}", "Passenger(<PassageClass.LOW: 2>, SystemMock('Uranus'))")

    def test_passenger_guess_survivors(self):
        """Test Passenger guesses as to number of low lottery survivors."""
        passenger = Passenger(PassageClass.LOW, SystemMock("Uranus"))
        for _ in range(1000):
            passenger.guess_survivors(10)
            guess = passenger.guess
            self.assertGreaterEqual(guess, 0)
            self.assertLessEqual(guess, 10)


# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
