from utilities import die_roll, constrain, int_input, confirm_input
from utilities import actual_value, pr_red, pr_green
from credits import Credits

class Cargo:
    def __init__(self, name, quantity, price, unit_size, 
                 purchase_dms, sale_dms, source_world=None):
        self.name = name
        self.quantity = Cargo.determine_quantity(quantity)

        # would prefer to pass this in as Credits already, but we are taking
        # input from the cargo table which just has integers
        self.price = Credits(price)
        self.unit_size = unit_size

        # DMs are in order: agricultural, non-agricultural, industrial,
        #                   non-industrial, rich, poor
        self.purchase_dms = purchase_dms
        self.sale_dms = sale_dms

        self.source_world = source_world

    def __repr__(self):
        if self.unit_size == 1:
            unit = "ton"
        else:
            unit = "item"

        result = f"{self.name} - {Cargo.quantity_string(self, self.quantity)} - {self.price}/{unit}"
        if self.source_world:
            result += f" ({self.source_world.name})"

        return result

    @property
    def tonnage(self):
        return self.quantity * self.unit_size

    def quantity_string(cargo, quantity):
        string = f"{quantity}"
        if cargo.unit_size == 1:
            if quantity == 1:
                string += " ton"
            else:
                string += " tons"
        else:
            string += f" ({cargo.unit_size} tons/item)"
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
    def __init__(self, system, ship, financials, current_date):
        self.system = system
        self.ship = ship
        self.financials = financials
        self.current_date = current_date.copy()
        self.cargo = self.determine_cargo()
        self.prices = [0]  
        # '0' indicates price modifier has not been determined yet
        # we are only retaining price modifiers for
        # purchases, not for sales

    def notify(self, date):
        if date >= ImperialDate(self.current_date.day + 7, self.current_date.year):
            self.current_date = date.copy()
            self.cargo = self.determine_cargo()
            self.prices = [0]

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
            modifier += table[0]
        if self.system.nonagricultural:
            modifier += table[1]
        if self.system.industrial:
            modifier += table[2]
        if self.system.nonindustrial:
            modifier += table[3]
        if self.system.rich:
            modifier += table[4]
        if self.system.poor:
            modifier += table[5]
        return modifier

    def buy_cargo(self):
        self.goods()
        # In Traveller '77, there is only one available cargo
        # per week. Retain this for future versions, though.
        item_number = int_input('Enter cargo number to buy: ')
        if item_number >= len(self.cargo):
            print("That is not a valid cargo ID.")
            return

        cargo = self.cargo[item_number]

        quantity = int_input('How many would you like to purchase? ')
        if quantity > cargo.quantity:
            print("There is not enough available. Specify a lower quantity.")
            return
        if quantity <= 0:
            print("Quantity needs to be a positive number.")
            return

        free_space = self.ship.free_space()
        if (quantity * cargo.unit_size > free_space):
            print("That amount will not fit in your hold.")
            print(f"You only have {free_space} tons free.")
            return

        modifier = self.get_price_modifiers(cargo, "purchase")

        if self.prices[item_number] > 0:
            price_adjustment = self.prices[item_number]
        else:
            roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
            price_adjustment = actual_value(roll)

            if quantity < cargo.quantity:
                price_adjustment += .01

            self.prices[item_number] = price_adjustment

        cost = Credits(cargo.price.amount * price_adjustment * quantity)
        if price_adjustment < 1:
            pr_function = pr_green
        elif price_adjustment > 1:
            pr_function = pr_red
        else:
            pr_function = print
        pr_function(f"That quantity will cost {cost}.")

        if cost > self.financials.balance:
            print("You do not have sufficient funds.")
            print(f"Your available balance is {self.financials.balance}.")
            return

        confirmation = confirm_input(f"Would you like to purchase " 
                                     f"{Cargo.quantity_string(cargo, quantity)} of "
                                     f"{cargo.name} for {cost} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling purchase.")
            return

        # proceed with the transaction
        if quantity == cargo.quantity:
            self.cargo.remove(cargo)
        else:
            cargo.quantity -= quantity

        purchased = Cargo(cargo.name, quantity, cargo.price.amount, cargo.unit_size, 
                          cargo.purchase_dms, cargo.sale_dms, self.system)
        self.ship.load_cargo(purchased)

        self.financials.debit(cost)

    def sell_cargo(self):
        self.ship.cargo_hold()
        item_number = int_input('Enter cargo number to sell ')
        if item_number >= len(self.ship.hold):
            print("That is not a valid cargo ID.")
            return

        cargo = self.ship.hold[item_number]

        if cargo.source_world:
            if cargo.source_world == self.system:
                print("You cannot resell cargo on the world where it was purchased.")
                return

        broker = confirm_input("Would you like to hire a broker (y/n)? ")

        broker_skill = 0
        if broker == 'y':
            while broker_skill < 1 or broker_skill > 4:
                broker_skill = int_input("What level of broker (1-4)? ")

            broker_confirm = confirm_input(f"This will incur a {5 * broker_skill}% fee. Confirm (y/n)? ")
            if broker_confirm == 'n':
                broker_skill = 0

        quantity = int_input('How many would you like to sell? ')
        if (quantity > cargo.quantity):
            print("There is not enough available. Specify a lower quantity.")
            return
        if quantity <= 0:
            print("Quantity needs to be a positive number.")
            return

        modifier = self.get_price_modifiers(cargo, "sale")
        modifier += self.ship.trade_skill()
        modifier += broker_skill

        roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
        price_adjustment = actual_value(roll)

        sale_price = Credits(cargo.price.amount * price_adjustment * quantity)
        if price_adjustment > 1:
            pr_function = pr_green
        elif price_adjustment < 1:
            pr_function = pr_red
        else:
            pr_function = print
        pr_function(f"That quantity will sell for {sale_price}.")

        if broker_skill > 0:
            broker_fee = Credits(sale_price.amount * (.05 * broker_skill))
            print(f"Deducting {broker_fee} broker fee for skill {broker_skill}.")
            self.financials.debit(broker_fee)

        confirmation = confirm_input("Would you like to sell " 
                                     f"{Cargo.quantity_string(cargo, quantity)} of "
                                     f"{cargo.name} for {sale_price} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling sale.")
            return

        # proceed with the transaction
        self.ship.unload_cargo(cargo, quantity)
        self.financials.credit(sale_price)

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
                11 : Cargo("Textiles", "3Dx5", 3000, 1, [-7,-5,0,-3,0,0], [-6,1,0,0,3,0]),
                12 : Cargo("Polymers", "4Dx5", 7000, 1, [0,0,-2,0,-3,2], [0,0,-2,0,3,0]),
                13 : Cargo("Liquor", "1Dx5", 10000, 1, [-4,0,0,0,0,0], [-3,0,1,0,2,0]),
                14 : Cargo("Wood", "2Dx10", 1000, 1, [-6,0,0,0,0,0], [-6,0,1,0,2,0]),
                15 : Cargo("Crystals", "1Dx1", 20000, 1, [0,-3,4,0,0,0], [0,-3,3,0,3,0]),
                16 : Cargo("Radioactives", "1Dx1", 1000000, 1, [0,0,7,-3,5,0], [0,0,6,-3,-4,0]),
                21 : Cargo("Steel", "4Dx10", 500, 1, [0,0,-2,0,-1,1], [0,0,-2,0,-1,3]),
                22 : Cargo("Copper", "2Dx10", 2000, 1, [0,0,-3,0,-2,1], [0,0,-3,0,-1,0]),
                23 : Cargo("Aluminum", "5Dx10", 1000, 1, [0,0,-3,0,-2,1], [0,0,-3,4,-1,0]),
                24 : Cargo("Tin", "3Dx10", 9000, 1, [0,0,-3,0,-2,1], [0,0,-3,0,-1,0]),
                25 : Cargo("Silver", "1Dx5", 70000, 1, [0,0,5,0,-1,2], [0,0,5,0,-1,0]),
                26 : Cargo("Special Alloys", "1Dx1", 200000, 1, [0,0,-3,5,-2,0], [0,0,-3,4,-1,0]),
                31 : Cargo("Petrochemicals", "6Dx5", 10000, 1, [0,-4,1,-5,0,0], [0,-4,3,-5,0,0]),
                32 : Cargo("Grain", "8Dx5", 300, 1, [-2,1,2,0,0,0], [-2,0,0,0,0,0]),
                33 : Cargo("Meat", "4Dx5", 1500, 1, [-2,2,3,0,0,0], [-2,0,2,0,0,1]),
                34 : Cargo("Spices", "1Dx5", 6000, 1, [-2,3,2,0,0,0], [-2,0,0,0,2,3]),
                35 : Cargo("Fruit", "2Dx5", 1000, 1, [-3,1,2,0,0,0], [-2,0,3,0,0,2]),
                36 : Cargo("Pharmaceuticals", "1Dx1", 100000, 1, [0,-3,4,0,0,3], [0,-3,5,0,4,0]),
                41 : Cargo("Gems", "1Dx1", 1000000, 1, [0,0,4,-8,0,-3], [0,0,4,-2,8,0]),
                42 : Cargo("Firearms", "2Dx1", 30000, 1, [0,0,-3,0,-2,3], [0,0,-2,0,-1,3]),
                43 : Cargo("Ammunition", "2Dx1", 30000, 1, [0,0,-3,0,-2,3], [0,0,-2,0,-1,3]),
                44 : Cargo("Blades", "2Dx1", 10000, 1, [0,0,-3,0,-2,3], [0,0,-2,0,-1,3]),
                45 : Cargo("Tools", "2Dx1", 10000, 1, [0,0,-3,0,-2,3], [0,0,-2,0,-1,3]),
                46 : Cargo("Body Armor", "2Dx1", 50000, 1, [0,0,-1,0,-3,3], [0,0,-2,0,1,4]),
                51 : Cargo("Aircraft", "1Dx1", 1000000, 10, [0,0,-4,0,-3,0], [0,0,0,2,0,1]),
                52 : Cargo("Air/Raft", "1Dx1", 6000000, 6, [0,0,-3,0,-2,0], [0,0,0,2,0,1]),
                53 : Cargo("Computers", "1Dx1", 10000000, 2, [0,0,-2,0,-2,0], [-3,0,0,2,0,1]),
                54 : Cargo("ATV", "1Dx1", 3000000, 4, [0,0,-2,0,-2,0], [1,0,0,2,0,1]),
                55 : Cargo("AFV", "1Dx1", 7000000, 4, [0,0,-5,0,-2,4], [2,-2,0,0,1,0]),
                56 : Cargo("Farm Machinery", "1Dx1", 150000, 4, [0,0,-5,0,-2,0], [5,-8,0,0,0,1]),
                61 : Cargo("Electronics Parts", "1Dx5", 100000, 1, [0,0,-4,0,-3,0], [0,0,0,2,0,1]),
                62 : Cargo("Mechanical Parts", "1Dx5", 75000, 1, [0,0,-5,0,-3,0], [2,0,0,3,0,0]),
                63 : Cargo("Cybernetic Parts", "1Dx5", 250000, 1, [0,0,-4,0,-1,0], [1,2,0,4,0,0]),
                64 : Cargo("Computer Parts", "1Dx5", 150000, 1, [0,0,-5,0,-3,0], [1,2,0,3,0,0]),
                65 : Cargo("Machine Tools", "1Dx5", 750000, 1, [0,0,-5,0,-4,0], [1,2,0,3,0,0]),
                66 : Cargo("Vacc Suits", "1Dx5", 400000, 1, [0,-5,-3,0,-3,0], [0,-1,0,2,0,0])
                }

        cargo.append(table[roll])
        return cargo
