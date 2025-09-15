import unittest
from utilities import die_roll, constrain, int_input, confirm_input
from utilities import actual_value, pr_red, pr_green
from financials import Credits

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
        q = str(quantity)
        if "Dx" in q:
            die_count, multiplier = [int(n) for n in q.split("Dx")]
            value = 0
            for _ in range(0, die_count):
                value += die_roll()
            value *= multiplier
            return value
        else:
            return int(quantity)

class CargoDepot:
    def __init__(self, system, current_date):
        self.system = system
        self.current_date = current_date.copy()
        self.cargo = self.determine_cargo()
        self.prices = [0]  
        # '0' indicates price modifier has not been determined yet
        # we are only retaining price modifiers for
        # purchases, not for sales

    def notify(self, date):
        if date >= self.current_date + 7:
            self.current_date = date.copy()
            self.cargo = self.determine_cargo()
            self.prices = [0]

    # deprecate, replaced with print_cargo_list below...
    def goods(self):
        for i,item in enumerate(self.cargo):
            print(f"{i} - {item}")

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

    def print_cargo_list(self, cargo_list):
        for i,item in enumerate(cargo_list):
            print(f"{i} - {item}")

    def get_cargo_lot(self, source, prompt):
        self.print_cargo_list(source)
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

            broker_confirm = confirm_input(f"This will incur a {5 * broker_skill}% fee. Confirm (y/n)? ")
            if broker_confirm == 'n':
                broker_skill = 0
        return broker_skill

    def insufficient_hold_space(self, cargo, quantity, free_space):
        if (quantity * cargo.unit_size > free_space):
            print("That amount will not fit in your hold.")
            print(f"You only have {free_space} tons free.")
            return True
        return False

    def determine_price(self, prompt, cargo, quantity, item_number, broker_skill, trade_skill):
        modifier = self.get_price_modifiers(cargo, prompt)

        if prompt == "sale":
            modifier += trade_skill
            modifier += broker_skill
            roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
            price_adjustment = actual_value(roll)
        elif prompt == "purchase":
            if self.prices[item_number] > 0:
                price_adjustment = self.prices[item_number]
            else:
                roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
                price_adjustment = actual_value(roll)
                if quantity < cargo.quantity:
                    price_adjustment += .01
                self.prices[item_number] = price_adjustment

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
        else:
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
        if quantity == cargo.quantity:
            source.remove(cargo)
        else:
            cargo.quantity -= quantity

    def determine_cargo(self):
        cargo = []

        first = die_roll()
        if (self.system.population <= 5):
            first -= 1
        if (self.system.population >= 9):
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
        a = Cargo("Foo", 10, 10, 1, {}, {})
        self.assertEqual(a.quantity, 10)

        b = Cargo("Bar", "1Dx1", 10, 1, {}, {})
        self.assertGreater(b.quantity, 0)
        self.assertLess(b.quantity, 7)

        c = Cargo("Baz", "1Dx10", 10, 1, {}, {})
        self.assertEqual(c.quantity % 10, 0)
        self.assertGreater(c.quantity, 9)
        self.assertLess(c.quantity, 61)

    def test_cargo_quantity_string(self):
        a = Cargo("Foo", 1, 10, 1, {}, {})
        self.assertEqual(a.quantity_string(1), "1 ton")
        self.assertEqual(a.quantity_string(5), "5 tons")

        b = Cargo("Bar", 1, 10, 5, {}, {})
        self.assertEqual(b.quantity_string(1), "1 (5 tons/item)")

    def test_cargo_tonnage(self):
        a = Cargo("Foo", 1, 10, 1, {}, {})
        self.assertEqual(a.tonnage, 1)

        b = Cargo("Bar", 1, 10, 5, {}, {})
        self.assertEqual(b.tonnage, 5)

        c = Cargo("Baz", 20, 10, 1, {}, {})
        self.assertEqual(c.tonnage, 20)

        d = Cargo("Boo", 20, 10, 10, {}, {})
        self.assertEqual(d.tonnage, 200)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
