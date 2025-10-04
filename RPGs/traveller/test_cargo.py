"""Contains tests for the cargo module."""
import unittest
from cargo import Cargo, CargoDepot, Freight
from financials import Credits

class CargoTestCase(unittest.TestCase):
    """Tests Cargo class."""

    def test_cargo_quantity(self):
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
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity_string(1), "1 ton")
        self.assertEqual(cargo1.quantity_string(5), "5 tons")

        cargo2 = Cargo("Bar", 1, Credits(10), 5, {}, {})
        self.assertEqual(cargo2.quantity_string(1), "1 (5 tons/item)")

    def test_cargo_tonnage(self):
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(cargo1.tonnage, 1)

        cargo2 = Cargo("Bar", 1, Credits(10), 5, {}, {})
        self.assertEqual(cargo2.tonnage, 5)

        cargo3 = Cargo("Baz", 20, Credits(10), 1, {}, {})
        self.assertEqual(cargo3.tonnage, 20)

        cargo4 = Cargo("Boo", 20, Credits(10), 10, {}, {})
        self.assertEqual(cargo4.tonnage, 200)

    def test_cargo_string(self):
        cargo1 = Cargo("Foo", 1, Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo1}", "Foo - 1 ton - 10 Cr/ton")

        cargo2 = Cargo("Bar", 5, Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo2}", "Bar - 5 tons - 10 Cr/ton")

        cargo3 = Cargo("Baz", 5, Credits(10), 5, {}, {})
        self.assertEqual(f"{cargo3}", "Baz - 5 (5 tons/item) - 10 Cr/item")

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
            self.value = value

        def copy(self):
            return CargoDepotTestCase.DateMock(self.value)

        def __add__(self, rhs):
            return CargoDepotTestCase.DateMock(self.value + rhs)

        def __sub__(self, rhs):
            return self.value - rhs.value

        def __ge__(self, other):
            return self.value >= other.value

    class SystemMock:
        """Mocks a system interface for testing."""

        def __init__(self):
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
            return f"{self.coordinate} - {self.name}"

    def setUp(self):
        CargoDepotTestCase.depot = CargoDepot(CargoDepotTestCase.SystemMock(),
                                              CargoDepotTestCase.DateMock(1))

    def test_notify(self):
        depot = CargoDepotTestCase.depot
        cargo = depot.cargo
        self.assertEqual(depot.refresh_date.value, 1)

        date = CargoDepotTestCase.DateMock(7)
        depot.notify(date)
        self.assertEqual(depot.refresh_date.value, 1)
        self.assertEqual(cargo, depot.cargo)

        date = CargoDepotTestCase.DateMock(8)
        depot.notify(date)
        self.assertEqual(depot.refresh_date.value, 8)
        self.assertNotEqual(cargo, depot.cargo)

    def test_get_price_modifiers(self):
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", "1", Credits(1), 1, {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1},
                                                  {"Ag":1, "Na":1, "In":1, "Ni":1, "Ri":1, "Po":1})

        modifier = depot.get_price_modifiers(cargo, "purchase")
        self.assertEqual(modifier, 6)

        modifier = depot.get_price_modifiers(cargo, "sale")
        self.assertEqual(modifier, 6)

    @unittest.skip("test has side effects: input & printing")
    def test_get_cargo_lot(self):
        depot = CargoDepotTestCase.depot
        cargo_list = ["a", "b", "c"]
        print(cargo_list)

        item_number, item = depot.get_cargo_lot(cargo_list, "buy")
        if item_number is None:
            self.assertEqual(item, None)
        if item_number == 0:
            self.assertEqual(item, "a")
        if item_number == 1:
            self.assertEqual(item, "b")
        if item_number == 2:
            self.assertEqual(item, "c")

    @unittest.skip("test has side effects: input & printing")
    def test_get_cargo_quantity(self):
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

        _ = depot.get_cargo_quantity("buy", cargo)
        # 0 - None
        # max - None
        # 0 < quantity < max - quantity

    @unittest.skip("test has side effects: printing")
    def test_invalid_cargo_origin(self):
        depot = CargoDepotTestCase.depot
        class Location:
            """Mocks a location interface for testing."""

            def __init__(self, name):
                self.name = name
            def __eq__(self, other):
                return self.name == other.name

        location1 = Location("Uranus")
        cargo1 = Cargo("Test", 10, Credits(1), 1, {}, {}, location1)
        self.assertTrue(depot.invalid_cargo_origin(cargo1))

        location2 = Location("Jupiter")
        cargo2 = Cargo("Test", 10, Credits(1), 1, {}, {}, location2)
        self.assertFalse(depot.invalid_cargo_origin(cargo2))

        cargo3 = Cargo("Test", 10, Credits(1), 1, {}, {})
        self.assertFalse(depot.invalid_cargo_origin(cargo3))

    @unittest.skip("test has side effects: input & printing")
    def test_get_broker(self):
        depot = CargoDepotTestCase.depot
        self.assertGreater(depot.get_broker(), -1)
        self.assertLess(depot.get_broker(), 5)
        # y/n | 1-4 | y/n = result 0-4

    @unittest.skip("test has side effects: printing")
    def test_insufficient_hold_space(self):
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

        self.assertTrue(depot.insufficient_hold_space(cargo, 10, 0))
        self.assertFalse(depot.insufficient_hold_space(cargo, 10, 10))

    @unittest.skip("test has side effects: printing")
    def test_determine_price(self):
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

        price = depot.determine_price("sale", cargo, 10, 0, 0)
        self.assertTrue(isinstance(price, Credits))
        self.assertGreaterEqual(price, Credits(4))
        self.assertLessEqual(price, Credits(40))

        self.assertEqual(cargo.price_adjustment, 0)
        price = depot.determine_price("purchase", cargo, 10, 0, 0)
        self.assertTrue(isinstance(price, Credits))
        self.assertGreaterEqual(price, Credits(4))
        self.assertLessEqual(price, Credits(40))
        self.assertGreater(cargo.price_adjustment, 0)

        price2 = depot.determine_price("purchase", cargo, 10, 0, 0)
        self.assertEqual(price2, price)

    @unittest.skip("test has side effects: printing")
    def test_insufficient_funds(self):
        depot = CargoDepotTestCase.depot

        result = depot.insufficient_funds(Credits(2), Credits(1))
        self.assertTrue(result)

        result = depot.insufficient_funds(Credits(1), Credits(1))
        self.assertFalse(result)

        result = depot.insufficient_funds(Credits(1), Credits(2))
        self.assertFalse(result)

    @unittest.skip("test has side effects: printing")
    def test_broker_fee(self):
        depot = CargoDepotTestCase.depot

        fee = depot.broker_fee(0, Credits(100))
        self.assertEqual(fee, Credits(0))

        fee = depot.broker_fee(1, Credits(100))
        self.assertEqual(fee, Credits(5))

        fee = depot.broker_fee(4, Credits(100))
        self.assertEqual(fee, Credits(20))

    @unittest.skip("test has side effects: input & printing")
    def test_confirm_transaction(self):
        depot = CargoDepotTestCase.depot
        cargo = Cargo("Test", 10, Credits(1), 1, {}, {})

        _ = depot.confirm_transaction("purchase", cargo, 1, Credits(1))
        # y/n

    def test_remove_cargo(self):
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

    def test_determine_cargo(self):
        depot = CargoDepotTestCase.depot

        cargo = depot.determine_cargo()
        self.assertEqual(len(cargo), 1)
        self.assertTrue(isinstance(cargo[0], Cargo))

    @unittest.skip("test has side effects: input & printing")
    def test_get_available_freight(self):
        depot = CargoDepotTestCase.depot
        world1 = CargoDepotTestCase.SystemMock()
        world1.name = "Pluto"
        world2 = CargoDepotTestCase.SystemMock()
        world2.name = "Jupiter"
        destinations = [world1, world2]

        _, _ = depot.get_available_freight(destinations)

    def test_passenger_origin_table(self):
        depot = CargoDepotTestCase.depot

        self.assertEqual(depot.passenger_origin_table(0), (0,0,0))
        self.assertEqual(depot.passenger_origin_table(1), (0,0,0))

        self.assertGreater(depot.passenger_origin_table(2)[0], -6)
        self.assertLess(depot.passenger_origin_table(2)[0], 6)
        self.assertGreater(depot.passenger_origin_table(2)[1], -6)
        self.assertLess(depot.passenger_origin_table(2)[1], 6)
        self.assertGreater(depot.passenger_origin_table(2)[2], -4)
        self.assertLess(depot.passenger_origin_table(2)[2], 18)

        self.assertGreater(depot.passenger_origin_table(3)[0], -10)
        self.assertLess(depot.passenger_origin_table(3)[0], 17)
        self.assertGreater(depot.passenger_origin_table(3)[1], -11)
        self.assertLess(depot.passenger_origin_table(3)[1], 11)
        self.assertGreater(depot.passenger_origin_table(3)[2], -4)
        self.assertLess(depot.passenger_origin_table(3)[2], 18)

        self.assertGreater(depot.passenger_origin_table(4)[0], -16)
        self.assertLess(depot.passenger_origin_table(4)[0], 16)
        self.assertGreater(depot.passenger_origin_table(4)[1], -16)
        self.assertLess(depot.passenger_origin_table(4)[1], 16)
        self.assertGreater(depot.passenger_origin_table(4)[2], -3)
        self.assertLess(depot.passenger_origin_table(4)[2], 24)

        self.assertGreater(depot.passenger_origin_table(5)[0], -10)
        self.assertLess(depot.passenger_origin_table(5)[0], 17)
        self.assertGreater(depot.passenger_origin_table(5)[1], -10)
        self.assertLess(depot.passenger_origin_table(5)[1], 17)
        self.assertGreater(depot.passenger_origin_table(5)[2], -3)
        self.assertLess(depot.passenger_origin_table(5)[2], 24)

        self.assertGreater(depot.passenger_origin_table(6)[0], -10)
        self.assertLess(depot.passenger_origin_table(6)[0], 17)
        self.assertGreater(depot.passenger_origin_table(6)[1], -10)
        self.assertLess(depot.passenger_origin_table(6)[1], 17)
        self.assertGreater(depot.passenger_origin_table(6)[2], 2)
        self.assertLess(depot.passenger_origin_table(6)[2], 19)

        self.assertGreater(depot.passenger_origin_table(7)[0], -10)
        self.assertLess(depot.passenger_origin_table(7)[0], 17)
        self.assertGreater(depot.passenger_origin_table(7)[1], -10)
        self.assertLess(depot.passenger_origin_table(7)[1], 17)
        self.assertGreater(depot.passenger_origin_table(7)[2], 2)
        self.assertLess(depot.passenger_origin_table(7)[2], 19)

        self.assertGreater(depot.passenger_origin_table(8)[0], -5)
        self.assertLess(depot.passenger_origin_table(8)[0], 12)
        self.assertGreater(depot.passenger_origin_table(8)[1], -10)
        self.assertLess(depot.passenger_origin_table(8)[1], 17)
        self.assertGreater(depot.passenger_origin_table(8)[2], 3)
        self.assertLess(depot.passenger_origin_table(8)[2], 25)

        self.assertGreater(depot.passenger_origin_table(9)[0], -5)
        self.assertLess(depot.passenger_origin_table(9)[0], 12)
        self.assertGreater(depot.passenger_origin_table(9)[1], -5)
        self.assertLess(depot.passenger_origin_table(9)[1], 12)
        self.assertGreater(depot.passenger_origin_table(9)[2], 3)
        self.assertLess(depot.passenger_origin_table(9)[2], 25)

        self.assertGreater(depot.passenger_origin_table(10)[0], -5)
        self.assertLess(depot.passenger_origin_table(10)[0], 12)
        self.assertGreater(depot.passenger_origin_table(10)[1], -5)
        self.assertLess(depot.passenger_origin_table(10)[1], 12)
        self.assertGreater(depot.passenger_origin_table(10)[2], 3)
        self.assertLess(depot.passenger_origin_table(10)[2], 25)

    def test_passenger_destination_table(self):
        depot = CargoDepotTestCase.depot

        counts = (4,4,4)
        self.assertEqual(depot.passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(depot.passenger_destination_table(1, counts), (0,0,0))
        self.assertEqual(depot.passenger_destination_table(2, counts), (3,2,0))
        self.assertEqual(depot.passenger_destination_table(3, counts), (3,3,1))
        self.assertEqual(depot.passenger_destination_table(4, counts), (3,3,2))
        self.assertEqual(depot.passenger_destination_table(5, counts), (4,3,3))
        self.assertEqual(depot.passenger_destination_table(6, counts), (4,4,3))
        self.assertEqual(depot.passenger_destination_table(7, counts), (4,4,4))
        self.assertEqual(depot.passenger_destination_table(8, counts), (5,4,4))
        self.assertEqual(depot.passenger_destination_table(9, counts), (5,5,4))
        self.assertEqual(depot.passenger_destination_table(10, counts), (5,5,6))

        counts = (0,0,0)
        self.assertEqual(depot.passenger_destination_table(0, counts), (0,0,0))
        self.assertEqual(depot.passenger_destination_table(2, counts), (0,0,0))

        counts = (50,50,50)
        self.assertEqual(depot.passenger_destination_table(7, counts), (40,40,40))

class FreightTestCase(unittest.TestCase):
    """Tests Freight class."""

    class SystemMock:
        """Mocks a system interface for testing."""

        def __init__(self, name):
            self.name = name

    def test_freight_string(self):
        freight = Freight(10,
                          FreightTestCase.SystemMock("Pluto"),
                          FreightTestCase.SystemMock("Uranus"))
        self.assertEqual(f"{freight}",
                         "Freight : 10 tons : Pluto -> Uranus")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
