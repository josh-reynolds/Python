"""Contains tests for the cargo_depot module."""
import unittest
from test.mock import ObserverMock, DateMock, SystemMock, ControlsMock
from src.cargo import Cargo
from src.cargo_depot import CargoDepot, _passenger_origin_table
from src.cargo_depot import _passenger_destination_table
from src.coordinate import Coordinate
from src.credits import Credits

class CargoDepotTestCase(unittest.TestCase):
    """Tests CargoDepot class."""

    depot = CargoDepot(SystemMock(), DateMock(1))

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
        depot.controls = ControlsMock([2, 1, 0, 7])
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
        depot.controls = ControlsMock([9, 1, 0, -1, 11])
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

        location1 = SystemMock("Jupiter")
        cargo1 = Cargo("Test", '10', Credits(1), 1, {}, {}, location1)
        self.assertFalse(depot.invalid_cargo_origin(cargo1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        cargo2 = Cargo("Test", '10', Credits(1), 1, {}, {})
        self.assertFalse(depot.invalid_cargo_origin(cargo2))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        location2 = SystemMock("Uranus")
        cargo3 = Cargo("Test", '10', Credits(1), 1, {}, {}, location2)
        self.assertTrue(depot.invalid_cargo_origin(cargo3))
        self.assertEqual(observer.message,
                         "You cannot resell cargo on the world where it was purchased.")
        self.assertEqual(observer.priority, "")

    def test_get_broker(self) -> None:
        """Test choosing a broker."""
        depot = CargoDepotTestCase.depot
        scenarios = ['n', 4, 5, 'y', 'y', 4, 5, 'y', 'n', 1, 'y', 'y', 1, 0, 'y', 'n']
        depot.controls = ControlsMock(scenarios)
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
        depot.controls = ControlsMock(scenarios)
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
        depot.controls = ControlsMock(scenarios)
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

    # pylint: disable=R0915
    # R0915: Too many statements (57/50)
    def test_passenger_origin_table(self) -> None:
        """Test calculation of passengers by origin world."""
        self.assertEqual(_passenger_origin_table(0), (0,0,0))
        self.assertEqual(_passenger_origin_table(1), (0,0,0))

        self.assertGreater(_passenger_origin_table(2)[0], -6)
        self.assertLess(_passenger_origin_table(2)[0], 6)
        self.assertGreater(_passenger_origin_table(2)[1], -6)
        self.assertLess(_passenger_origin_table(2)[1], 6)
        self.assertGreater(_passenger_origin_table(2)[2], -4)
        self.assertLess(_passenger_origin_table(2)[2], 18)

        self.assertGreater(_passenger_origin_table(3)[0], -10)
        self.assertLess(_passenger_origin_table(3)[0], 17)
        self.assertGreater(_passenger_origin_table(3)[1], -11)
        self.assertLess(_passenger_origin_table(3)[1], 11)
        self.assertGreater(_passenger_origin_table(3)[2], -4)
        self.assertLess(_passenger_origin_table(3)[2], 18)

        self.assertGreater(_passenger_origin_table(4)[0], -16)
        self.assertLess(_passenger_origin_table(4)[0], 16)
        self.assertGreater(_passenger_origin_table(4)[1], -16)
        self.assertLess(_passenger_origin_table(4)[1], 16)
        self.assertGreater(_passenger_origin_table(4)[2], -3)
        self.assertLess(_passenger_origin_table(4)[2], 24)

        self.assertGreater(_passenger_origin_table(5)[0], -10)
        self.assertLess(_passenger_origin_table(5)[0], 17)
        self.assertGreater(_passenger_origin_table(5)[1], -10)
        self.assertLess(_passenger_origin_table(5)[1], 17)
        self.assertGreater(_passenger_origin_table(5)[2], -3)
        self.assertLess(_passenger_origin_table(5)[2], 24)

        self.assertGreater(_passenger_origin_table(6)[0], -10)
        self.assertLess(_passenger_origin_table(6)[0], 17)
        self.assertGreater(_passenger_origin_table(6)[1], -10)
        self.assertLess(_passenger_origin_table(6)[1], 17)
        self.assertGreater(_passenger_origin_table(6)[2], 2)
        self.assertLess(_passenger_origin_table(6)[2], 19)

        self.assertGreater(_passenger_origin_table(7)[0], -10)
        self.assertLess(_passenger_origin_table(7)[0], 17)
        self.assertGreater(_passenger_origin_table(7)[1], -10)
        self.assertLess(_passenger_origin_table(7)[1], 17)
        self.assertGreater(_passenger_origin_table(7)[2], 2)
        self.assertLess(_passenger_origin_table(7)[2], 19)

        self.assertGreater(_passenger_origin_table(8)[0], -5)
        self.assertLess(_passenger_origin_table(8)[0], 12)
        self.assertGreater(_passenger_origin_table(8)[1], -10)
        self.assertLess(_passenger_origin_table(8)[1], 17)
        self.assertGreater(_passenger_origin_table(8)[2], 3)
        self.assertLess(_passenger_origin_table(8)[2], 25)

        self.assertGreater(_passenger_origin_table(9)[0], -5)
        self.assertLess(_passenger_origin_table(9)[0], 12)
        self.assertGreater(_passenger_origin_table(9)[1], -5)
        self.assertLess(_passenger_origin_table(9)[1], 12)
        self.assertGreater(_passenger_origin_table(9)[2], 3)
        self.assertLess(_passenger_origin_table(9)[2], 25)

        self.assertGreater(_passenger_origin_table(10)[0], -5)
        self.assertLess(_passenger_origin_table(10)[0], 12)
        self.assertGreater(_passenger_origin_table(10)[1], -5)
        self.assertLess(_passenger_origin_table(10)[1], 12)
        self.assertGreater(_passenger_origin_table(10)[2], 3)
        self.assertLess(_passenger_origin_table(10)[2], 25)

    def test_passenger_destination_table(self) -> None:
        """Test determination of passenger count modifiers by destination world."""
        counts = (4,4,4)
        self.assertEqual(_passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(_passenger_destination_table(1, counts), (0,0,0))
        self.assertEqual(_passenger_destination_table(2, counts), (3,2,0))
        self.assertEqual(_passenger_destination_table(3, counts), (3,3,1))
        self.assertEqual(_passenger_destination_table(4, counts), (3,3,2))
        self.assertEqual(_passenger_destination_table(5, counts), (4,3,3))
        self.assertEqual(_passenger_destination_table(6, counts), (4,4,3))
        self.assertEqual(_passenger_destination_table(7, counts), (4,4,4))
        self.assertEqual(_passenger_destination_table(8, counts), (5,4,4))
        self.assertEqual(_passenger_destination_table(9, counts), (5,5,4))
        self.assertEqual(_passenger_destination_table(10, counts), (5,5,6))

        counts = (0,0,0)
        self.assertEqual(_passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(_passenger_destination_table(2, counts), (0,0,0))

        counts = (50,50,50)
        self.assertEqual(_passenger_destination_table(7, counts), (40,40,40))

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
        depot.controls = ControlsMock(scenarios)
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
