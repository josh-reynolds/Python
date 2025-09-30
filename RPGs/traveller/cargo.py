import unittest
from enum import Enum
from utilities import die_roll, constrain, int_input, confirm_input
from utilities import actual_value, pr_red, pr_green
from financials import Credits

class PassageClass(Enum):
    HIGH = 0
    MIDDLE = 1
    LOW = 2

class Passenger:
    def __init__(self, passage, destination):
        if passage == PassageClass.HIGH:
            self.name = "High passage"
            self.ticket_price = Credits(10000)
        if passage == PassageClass.MIDDLE:
            self.name = "Middle passage"
            self.ticket_price = Credits(8000)
        if passage == PassageClass.LOW:
            self.name = "Low passage"
            self.ticket_price = Credits(1000)
        self.passage = passage
        self.destination = destination

    def __repr__(self):
        return f"{self.name} to {self.destination.name}"

class Freight:
    def __init__(self, tonnage, source_world, destination_world):
        self.name = "Freight"
        self.tonnage = tonnage
        self.source_world = source_world
        self.destination_world = destination_world

    def __repr__(self):
        return f"{self.name} : {self.tonnage} tons : " +\
               f"{self.source_world.name} -> {self.destination_world.name}"

class Cargo:
    def __init__(self, name, quantity, price, unit_size,
                 purchase_dms, sale_dms, source_world=None):
        self.name = name
        self.quantity = Cargo.determine_quantity(quantity)
        self.price = price
        self.unit_size = unit_size
        self.purchase_dms = purchase_dms
        self.sale_dms = sale_dms
        self.source_world = source_world
        self.price_adjustment = 0    # purchase price adjustment
                                     # '0' indicates not determined yet

    def __repr__(self):
        if self.unit_size == 1:
            unit = "ton"
        else:
            unit = "item"

        result = f"{self.name} - {self.quantity_string(self.quantity)} - {self.price}/{unit}"
        if self.source_world:
            result += f" ({self.source_world.name})"

        return result

    @property
    def tonnage(self):
        return self.quantity * self.unit_size

    # passing in quantity because we want to be able to specify
    # partial lots, not always the full amount (though a quick
    # grep shows this isn't used elsewhere, so it may have been
    # refactored away). Consider eliminating this param.
    def quantity_string(self, quantity):
        string = f"{quantity}"
        if self.unit_size == 1:
            if quantity == 1:
                string += " ton"
            else:
                string += " tons"
        else:
            string += f" ({self.unit_size} tons/item)"
        return string

    # quantity convention:
    #   if 'quantity' parameter string contains "Dx" then
    #     the value needs to be randomly generated
    #     otherwise it is an exact amount
    #   value is either tonnage or separate items
    #     as indicated by the unit_size field
    def determine_quantity(quantity):
        amount = str(quantity)
        if "Dx" in amount:
            die_count, multiplier = [int(n) for n in amount.split("Dx")]
            value = 0
            for _ in range(0, die_count):
                value += die_roll()
            value *= multiplier
            return value
        return int(quantity)

class CargoDepot:
    def __init__(self, system, refresh_date):
        self.system = system
        self.refresh_date = refresh_date.copy()
        self.recurrence = 7
        self.cargo = self.determine_cargo()
        self.freight = {}
        self.passengers = {}

    def notify(self, date):
        duration = (date - self.refresh_date) // self.recurrence
        for _ in range(duration):
            self.refresh_date += self.recurrence
        if duration > 0:       # we only need to refresh the cargo once, not repeatedly
            self.cargo = self.determine_cargo()
            self.refresh_freight(self.system.destinations)
            self.refresh_passengers(self.system.destinations)

    def refresh_freight(self, destinations):
        self.freight = {}
        for world in destinations:
            self.freight[world] = []
            for i in range(world.population):
                self.freight[world].append(die_roll() * 5)
            self.freight[world] = sorted(self.freight[world])

    # Table from Book 2 p. 7
    # In RAW the table goes up to population 12, but the system only 
    # generates populations up to 10, so I am truncating
    def passenger_origin_table(self, population):
        if population < 2:
            return (0,0,0)
        if population == 2:
            return (die_roll()-die_roll(), 
                    die_roll()-die_roll(), 
                    die_roll(3)-die_roll())
        if population == 3:
            return (die_roll(3)-die_roll(2),
                    die_roll(2)-die_roll(2), 
                    die_roll(3)-die_roll())
        if population == 4:
            return (die_roll(3)-die_roll(3),
                    die_roll(3)-die_roll(3), 
                    die_roll(4)-die_roll())
        if population == 5:
            return (die_roll(3)-die_roll(2),
                    die_roll(3)-die_roll(2), 
                    die_roll(4)-die_roll())
        if population == 6 or population == 7:
            return (die_roll(3)-die_roll(2),
                    die_roll(3)-die_roll(2), 
                    die_roll(3))
        if population == 8:
            return (die_roll(2)-die_roll(),
                    die_roll(3)-die_roll(2), 
                    die_roll(4))
        if population > 8:
            return (die_roll(2)-die_roll(),
                    die_roll(2)-die_roll(), 
                    die_roll(4))

    def passenger_destination_table(self, population, counts):
        if population < 2:
            return (0,0,0)
        if population == 2:
            modifiers = (-1,-2,-4)
        if population == 3:
            modifiers = (-1,-1,-3)
        if population == 4:
            modifiers = (-1,-1,-2)
        if population == 5:
            modifiers = (0,-1,-1)
        if population == 6:
            modifiers = (0,0,-1)
        if population == 7:
            modifiers = (0,0,0)
        if population == 8:
            modifiers = (1,0,0)
        if population == 9:
            modifiers = (1,1,0)
        if population == 10:
            modifiers = (1,1,2)

        return tuple(constrain(a + b, 0, 40) for a,b in zip(counts,modifiers))

    # passenger counts are a tuple, indexed by the PassageClass enum
    def refresh_passengers(self, destinations):
        self.passengers = {}
        for world in destinations:
            origin_counts = self.passenger_origin_table(self.system.population)
            passengers = self.passenger_destination_table(world.population, 
                                                          origin_counts)
            self.passengers[world] = passengers

    def get_available_freight(self, destinations):
        if self.freight == {}:
            self.refresh_freight(destinations)

        for i,world in enumerate(destinations):
            pr_green(f"{i} - {world}")
            print("   ", self.freight[world])
            print()

        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.freight[world].copy())

    def get_available_passengers(self, destinations):
        if self.passengers == {}:
            self.refresh_passengers(destinations)

        for i,world in enumerate(destinations):
            pr_green(f"{i} - {world}")
            print("   ", self.passengers[world])
            print()

        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.passengers[world])
    
    def get_price_modifiers(self, cargo, transaction_type):
        if transaction_type == "purchase":
            table = cargo.purchase_dms
        elif transaction_type == "sale":
            table = cargo.sale_dms
        modifier = 0
        if self.system.agricultural:
            modifier += table.get("Ag",0)
        if self.system.nonagricultural:
            modifier += table.get("Na",0)
        if self.system.industrial:
            modifier += table.get("In",0)
        if self.system.nonindustrial:
            modifier += table.get("Ni",0)
        if self.system.rich:
            modifier += table.get("Ri",0)
        if self.system.poor:
            modifier += table.get("Po",0)
        return modifier

    def get_cargo_lot(self, source, prompt):
        item_number = int_input(f"Enter cargo number to {prompt}: ")
        if item_number >= len(source):
            print("That is not a valid cargo ID.")
            return (None, None)
        return (item_number, source[item_number])

    def get_cargo_quantity(self, prompt, cargo):
        quantity = int_input(f"How many would you like to {prompt}? ")
        if quantity > cargo.quantity:
            print("There is not enough available. Specify a lower quantity.")
            return None
        if quantity <= 0:
            print("Quantity needs to be a positive number.")
            return None
        return quantity

    def invalid_cargo_origin(self, cargo):
        if cargo.source_world:
            if cargo.source_world == self.system:
                print("You cannot resell cargo on the world where it was purchased.")
                return True
        return False

    def get_broker(self):
        broker = confirm_input("Would you like to hire a broker (y/n)? ")
        broker_skill = 0
        if broker == 'y':
            while broker_skill < 1 or broker_skill > 4:
                broker_skill = int_input("What level of broker (1-4)? ")

            broker_confirm = confirm_input( "This will incur a " +
                                           f"{5 * broker_skill}% fee. " +
                                            "Confirm (y/n)? ")
            if broker_confirm == 'n':
                broker_skill = 0
        return broker_skill

    def insufficient_hold_space(self, cargo, quantity, free_space):
        if quantity * cargo.unit_size > free_space:
            print("That amount will not fit in your hold.")
            print(f"You only have {free_space} tons free.")
            return True
        return False

    # TO_DO: this method is still too unwieldy - break it up further
    def determine_price(self, prompt, cargo, quantity, broker_skill, trade_skill):
        modifier = self.get_price_modifiers(cargo, prompt)

        if prompt == "sale":
            modifier += trade_skill
            modifier += broker_skill
            roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
            price_adjustment = actual_value(roll)
        elif prompt == "purchase":
            if cargo.price_adjustment > 0:
                price_adjustment = cargo.price_adjustment
            else:
                roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
                price_adjustment = actual_value(roll)
                if quantity < cargo.quantity:
                    price_adjustment += .01
                cargo.price_adjustment = price_adjustment

        price = Credits(cargo.price.amount * price_adjustment * quantity)
        if ((prompt == "sale" and price_adjustment > 1) or
            (prompt == "purchase" and price_adjustment < 1)):
            pr_function = pr_green
        elif ((prompt == "sale" and price_adjustment < 1) or
              (prompt == "purchase" and price_adjustment > 1)):
            pr_function = pr_red
        else:
            pr_function = print

        pr_function(f"{prompt.capitalize()} price of that quantity is {price}.")
        return price

    def insufficient_funds(self, cost, balance):
        if cost > balance:
            print("You do not have sufficient funds.")
            print(f"Your available balance is {balance}.")
            return True
        return False

    def broker_fee(self, broker_skill, sale_price):
        if broker_skill > 0:
            broker_fee = Credits(sale_price.amount * (.05 * broker_skill))
            print(f"Deducting {broker_fee} broker fee for skill {broker_skill}.")
            return broker_fee
        return Credits(0)

    def confirm_transaction(self, prompt, cargo, quantity, price):
        confirmation = confirm_input(f"Confirming {prompt} of "
                                     f"{Cargo.quantity_string(cargo, quantity)} of "
                                     f"{cargo.name} for {price} (y/n)? ")
        if confirmation == 'n':
            print(f"Cancelling {prompt}.")
            return False
        return True

    # this overlaps with ship.unload_cargo()...
    def remove_cargo(self, source, cargo, quantity):
        if cargo in source:
            if quantity >= cargo.quantity:
                source.remove(cargo)
            else:
                cargo.quantity -= quantity

    def determine_cargo(self):
        cargo = []

        first = die_roll()
        if self.system.population <= 5:
            first -= 1
        if self.system.population >= 9:
            first += 1
        first = constrain(first, 1, 6)
        first *= 10

        second = die_roll()
        roll = first + second

        table = {
                11 : Cargo("Textiles", "3Dx5", Credits(3000), 1, {"Ag":-7,"Na":-5,"Ni":-3},
                                                        {"Ag":-6,"Na":1,"Ri":3}),
                12 : Cargo("Polymers", "4Dx5", Credits(7000), 1, {"In":-2,"Ri":-3,"Po":2},
                                                        {"In":-2,"Ri":3}),
                13 : Cargo("Liquor", "1Dx5", Credits(10000), 1, {"Ag":-4},
                                                       {"Ag":-3,"In":1,"Ri":2}),
                14 : Cargo("Wood", "2Dx10", Credits(1000), 1, {"Ag":-6},
                                                     {"Ag":-6,"In":1,"Ri":2}),
                15 : Cargo("Crystals", "1Dx1", Credits(20000), 1, {"Na":-3,"In":4},
                                                         {"Na":-3,"In":3,"Ri":3}),
                16 : Cargo("Radioactives", "1Dx1", Credits(1000000), 1, {"In":7,"Ni":-3,"Ri":5},
                                                               {"In":6,"Ni":-3,"Ri":-4}),
                21 : Cargo("Steel", "4Dx10", Credits(500), 1, {"In":-2,"Ri":-1,"Po":1},
                                                     {"In":-2,"Ri":-1,"Po":3}),
                22 : Cargo("Copper", "2Dx10", Credits(2000), 1, {"In":-3,"Ri":-2,"Po":1},
                                                       {"In":-3,"Ri":-1}),
                23 : Cargo("Aluminum", "5Dx10", Credits(1000), 1, {"In":-3,"Ri":-2,"Po":1},
                                                         {"In":-3,"Ni":4,"Ri":-1}),
                24 : Cargo("Tin", "3Dx10", Credits(9000), 1, {"In":-3,"Ri":-2,"Po":1},
                                                    {"In":-3,"Ri":-1}),
                25 : Cargo("Silver", "1Dx5", Credits(70000), 1, {"In":5,"Ri":-1,"Po":2},
                                                       {"In":5,"Ri":-1}),
                26 : Cargo("Special Alloys", "1Dx1", Credits(200000), 1, {"In":-3,"Ni":5,"Ri":-2},
                                                                {"In":-3,"Ni":4,"Ri":-1}),
                31 : Cargo("Petrochemicals", "6Dx5", Credits(10000), 1, {"Na":-4,"In":1,"Ni":-5},
                                                               {"Na":-4,"In":3,"Ni":-5}),
                32 : Cargo("Grain", "8Dx5", Credits(300), 1, {"Ag":-2,"Na":1,"In":2},
                                                    {"Ag":-2}),
                33 : Cargo("Meat", "4Dx5", Credits(1500), 1, {"Ag":-2,"Na":2,"In":3},
                                                    {"Ag":-2,"In":2,"Po":1}),
                34 : Cargo("Spices", "1Dx5", Credits(6000), 1, {"Ag":-2,"Na":3,"In":2},
                                                      {"Ag":-2,"Ri":2,"Po":3}),
                35 : Cargo("Fruit", "2Dx5", Credits(1000), 1, {"Ag":-3,"Na":1,"In":2},
                                                     {"Ag":-2,"In":3,"Po":2}),
                36 : Cargo("Pharmaceuticals", "1Dx1", Credits(100000), 1, {"Na":-3,"In":4,"Po":3},
                                                                 {"Na":-3,"In":5,"Ri":4}),
                41 : Cargo("Gems", "1Dx1", Credits(1000000), 1, {"In":4,"Ni":-8,"Po":-3},
                                                       {"In":4,"Ni":-2,"Ri":8}),
                42 : Cargo("Firearms", "2Dx1", Credits(30000), 1, {"In":-3,"Ri":-2,"Po":3},
                                                         {"In":-2,"Ri":-1,"Po":3}),
                43 : Cargo("Ammunition", "2Dx1", Credits(30000), 1, {"In":-3,"Ri":-2,"Po":3},
                                                           {"In":-2,"Ri":-1,"Po":3}),
                44 : Cargo("Blades", "2Dx1", Credits(10000), 1, {"In":-3,"Ri":-2,"Po":3},
                                                       {"In":-2,"Ri":-1,"Po":3}),
                45 : Cargo("Tools", "2Dx1", Credits(10000), 1, {"In":-3,"Ri":-2,"Po":3},
                                                      {"In":-2,"Ri":-1,"Po":3}),
                46 : Cargo("Body Armor", "2Dx1", Credits(50000), 1, {"In":-1,"Ri":-3,"Po":3},
                                                           {"In":-2,"Ri":1,"Po":4}),
                51 : Cargo("Aircraft", "1Dx1", Credits(1000000), 10, {"In":-4,"Ri":-3},
                                                            {"Ni":2,"Po":1}),
                52 : Cargo("Air/Raft", "1Dx1", Credits(6000000), 6, {"In":-3,"Ri":-2},
                                                           {"Ni":2,"Po":1}),
                53 : Cargo("Computers", "1Dx1", Credits(10000000), 2, {"In":-2,"Ri":-2},
                                                             {"Ag":-3,"Ni":2,"Po":1}),
                54 : Cargo("ATV", "1Dx1", Credits(3000000), 4, {"In":-2,"Ri":-2},
                                                      {"Ag":1,"Ni":2,"Po":1}),
                55 : Cargo("AFV", "1Dx1", Credits(7000000), 4, {"In":-5,"Ri":-2,"Po":4},
                                                      {"Ag":2,"Na":-2,"Ri":1}),
                56 : Cargo("Farm Machinery", "1Dx1", Credits(150000), 4, {"In":-5,"Ri":-2},
                                                                {"Ag":5,"Na":-8,"Po":1}),
                61 : Cargo("Electronics Parts", "1Dx5", Credits(100000), 1, {"In":-4,"Ri":-3},
                                                                   {"Ni":2,"Po":1}),
                62 : Cargo("Mechanical Parts", "1Dx5", Credits(75000), 1, {"In":-5,"Ri":-3},
                                                                 {"Ag":2,"Ni":3}),
                63 : Cargo("Cybernetic Parts", "1Dx5", Credits(250000), 1, {"In":-4,"Ri":-1},
                                                                  {"Ag":1,"Na":2,"Ni":4}),
                64 : Cargo("Computer Parts", "1Dx5", Credits(150000), 1, {"In":-5,"Ri":-3},
                                                                {"Ag":1,"Na":2,"Ni":3}),
                65 : Cargo("Machine Tools", "1Dx5", Credits(750000), 1, {"In":-5,"Ri":-4},
                                                               {"Ag":1,"Na":2,"Ni":3}),
                66 : Cargo("Vacc Suits", "1Dx5", Credits(400000), 1, {"Na":-5,"In":-3,"Ri":-1},
                                                            {"Na":-1,"Ni":2,"Po":1})
                }

        cargo.append(table[roll])
        return cargo

class CargoTestCase(unittest.TestCase):
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
            def __init__(self, name):
                self.name = name
        location = Location("Uranus")
        cargo4 = Cargo("Boo", 100, Credits(10), 1, {}, {}, location)
        self.assertEqual(f"{cargo4}", "Boo - 100 tons - 10 Cr/ton (Uranus)")

class CargoDepotTestCase(unittest.TestCase):
    class DateMock:
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

        coordinate, available = depot.get_available_freight(destinations)

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
    class SystemMock:
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
