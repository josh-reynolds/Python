from random import randint

def pr_yellow_on_red(string):
    """Print string to console, yellow text on red background."""
    print(f"\033[1;33;41m{string}\033[00m")

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m{string}\033[00m")

def pr_green(string):
    """Print string to console, colored green."""
    print(f"\033[92m{string}\033[00m")

def die_roll():
    return randint(1,6)

def constrain(value, min_val, max_val):
    if value <= min_val:
        return min_val
    elif value >= max_val:
        return max_val
    else:
        return value

# table from Book 2 p. 42
def actual_value(roll):
    actual_value = {2:.4, 3:.5, 4:.7, 5:.8, 6:.9, 7:1, 8:1.1,
                    9:1.2, 10:1.3, 11:1.5, 12:1.7, 13:2, 14:3, 15:4}
    return actual_value[roll]

class Credits:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        val = round(self.amount)
        suffix = "Cr"
        if val >= 1000000:
            suffix = "MCr"
            val = val/1000000
        return f"{val:,} {suffix}"

    def __gt__(self, other):
        return self.amount > other.amount

    def __add__(self, other):
        return Credits(self.amount + other.amount)

    def __sub__(self, other):
        return Credits(self.amount - other.amount)

class StarSystem:
    def __init__(self, name, atmosphere, hydrographics, population, government, current_date):
        self.name = name
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.detail = "surface"
        self.depot = CargoDepot(self, current_date)

        self.agricultural = False
        if (atmosphere >= 4 and atmosphere <= 9 and 
            hydrographics >= 4 and hydrographics <= 8 and
            population >= 5 and population <= 7):
            self.agricultural = True

        self.nonagricultural = False
        if (atmosphere <= 3 and 
            hydrographics <= 3 and
            population >= 6):
            self.nonagricultural = True

        self.industrial = False
        if ((atmosphere <= 2 or atmosphere == 4 or atmosphere == 7 or atmosphere == 9) and
            population >= 9):
            self.industrial = True

        self.nonindustrial = False
        if population <= 6:
            self.nonindustrial = True

        self.rich = False
        if (government >= 4 and government <= 9 and
            (atmosphere == 6 or atmosphere == 8) and
            population >= 6 and population <= 8):
            self.rich = True

        self.poor = False
        if (atmosphere >= 2 and atmosphere <= 5 and
            hydrographics <= 3):
            self.poor = True

    #   making a big assumption that worlds cannot share the
    #   same name - good enough for now
    def __eq__(self, other):
        if isinstance(other, StarSystem):
            return self.name == other.name
        return False

    def description(self):
        if self.detail == "surface":
            return f"on {self.name}"
        elif self.detail == "orbit":
            return f"in orbit around {self.name}"
        elif self.detail == "jump":
            return f"at the {self.name} jump point"
        elif self.detail == "trade":
            return f"at the {self.name} trade depot"

    def land(self):
        if self.detail == "orbit":
            self.detail = "surface"

    def liftoff(self):
        if self.detail == "surface":
            self.detail = "orbit"

    def to_jump_point(self):
        if self.detail == "orbit":
            self.detail = "jump"

    def from_jump_point(self):
        if self.detail == "jump":
            self.detail = "orbit"

    def join_trade(self):
        if self.detail == "surface":
            self.detail = "trade"

    def leave_trade(self):
        if self.detail == "trade":
            self.detail = "surface"

class Command:
    def __init__(self, key, description, action, message):
        self.key = key
        self.description = description
        self.action = action
        self.message = message

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
    def __init__(self, system, current_date):
        self.system = system
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

    def buy_cargo(self):
        global game
        self.goods()
        # In Traveller '77, there is only one available cargo
        # per week. Retain this for future versions, though.
        # BUG: non-numeric input causes a crash
        item_number = int(input('Enter cargo number to buy: '))
        if item_number >= len(self.cargo):
            print("That is not a valid cargo ID.")
            return

        cargo = self.cargo[item_number]
        # BUG: non-numeric input causes a crash
        # BUG: can purchase 0 items (how about negative?)
        quantity = int(input('How many would you like to purchase? '))
        if (quantity > cargo.quantity):
            print("There is not enough available. Specify a lower quantity.")
            return

        free_space = game.ship.free_space()
        if (quantity * cargo.unit_size > free_space):
            print("That amount will not fit in your hold.")
            print(f"You only have {free_space} tons free.")
            return

        modifier = 0
        if self.system.agricultural:
            modifier += cargo.purchase_dms[0]
        if self.system.nonagricultural:
            modifier += cargo.purchase_dms[1]
        if self.system.industrial:
            modifier += cargo.purchase_dms[2]
        if self.system.nonindustrial:
            modifier += cargo.purchase_dms[3]
        if self.system.rich:
            modifier += cargo.purchase_dms[4]
        if self.system.poor:
            modifier += cargo.purchase_dms[5]

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

        if cost > game.financials.balance:
            print("You do not have sufficient funds.")
            print(f"Your available balance is {game.financials.balance}.")
            return

        confirmation = ""
        while confirmation != 'y' and confirmation != 'n':
            confirmation = input(f"Would you like to purchase " 
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
                          cargo.purchase_dms, cargo.sale_dms, game.location)
        game.ship.load_cargo(purchased)

        game.financials.debit(cost)

    def sell_cargo(self):
        global game
        game.ship.cargo_hold()
        item_number = int(input('Enter cargo number to sell '))
        if item_number >= len(game.ship.hold):
            print("That is not a valid cargo ID.")
            return

        cargo = game.ship.hold[item_number]

        if cargo.source_world:
            if cargo.source_world == game.location:
                print("You cannot resell cargo on the world where it was purchased.")
                return

        broker = ""
        while broker != 'y' and broker != 'n':
            broker = input(f"Would you like to hire a broker (y/n)? ")

        broker_skill = 0
        if broker == 'y':
            while broker_skill < 1 or broker_skill > 4:
                broker_skill = int(input("What level of broker (1-4)? "))

            broker_confirm = ""
            while broker_confirm != 'y' and broker_confirm != 'n':
                broker_confirm = input(f"This will incur a {5 * broker_skill}% fee. Confirm (y/n)? ")

            if broker_confirm == 'n':
                broker_skill = 0

        # BUG: non-numeric input causes a crash
        # BUG: can purchase 0 items (how about negative?)
        quantity = int(input('How many would you like to sell? '))
        if (quantity > cargo.quantity):
            print("There is not enough available. Specify a lower quantity.")
            return

        modifier = 0
        if self.system.agricultural:
            modifier += cargo.sale_dms[0]
        if self.system.nonagricultural:
            modifier += cargo.sale_dms[1]
        if self.system.industrial:
            modifier += cargo.sale_dms[2]
        if self.system.nonindustrial:
            modifier += cargo.sale_dms[3]
        if self.system.rich:
            modifier += cargo.sale_dms[4]
        if self.system.poor:
            modifier += cargo.sale_dms[5]

        modifier += game.ship.trade_skill()
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
            game.financials.debit(broker_fee)

        confirmation = ""
        while confirmation != 'y' and confirmation != 'n':
            confirmation = input(f"Would you like to sell " 
                                 f"{Cargo.quantity_string(cargo, quantity)} of "
                                 f"{cargo.name} for {sale_price} (y/n)? ")

        if confirmation == 'n':
            print("Cancelling sale.")
            return

        # proceed with the transaction
        game.ship.unload_cargo(cargo, quantity)
        game.financials.credit(sale_price)

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

class Ship:
    # For now we'll use the stats of a standard Free Trader (Book 2 p. 19) as necessary
    def __init__(self):
        self.hold = [Cargo("Grain", 20, 300, 1, [-2,1,2,0,0,0], [-2,0,0,0,0,0])]
        self.hold_size = 82

    def cargo_hold(self):
        for i,item in enumerate(self.hold):
            print(f"{i} - {item}")

    def free_space(self):
        taken = sum([cargo.tonnage for cargo in self.hold])
        return self.hold_size - taken

    # for now keep all cargo lots separate, since the may have had different
    # purchase prices, plus it is simpler
    # if this turns out not to matter, or we can handle via a transaction log
    # instead, then we could merge identical cargo types together
    def load_cargo(self, cargo):
        self.hold.append(cargo)

    def unload_cargo(self, cargo, quantity):
        if quantity == cargo.quantity:
            self.hold.remove(cargo)
        else:
            cargo.quantity -= quantity

    # Book 2 p. 43
    # If characters are skilled in bribery or admin, they may apply these
    # as DMs for the sale of goods. In any given transaction, such DMs may
    # be used by only one person.
    def trade_skill(self):
        return 1

class Financials:
    def __init__(self, balance, current_date):
        self.balance = Credits(balance)
        self.current_date = current_date.copy()
        self.berth_expiry = ImperialDate(self.current_date.day + 6, self.current_date.year)

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount

    def notify(self, date):
        self.current_date = date.copy()
        if date > self.berth_expiry and game.location.detail == "surface":
            self.renew_berth(date)

    # Book 2 p. 7:
    # Average cost is CR 100 to land and remain for up to six days;
    # thereafter, a CR 100 per day fee is imposed for each
    # additional day spent in port. In some locations this fee will
    # be higher, while at others local government subsidies will 
    # lower or eliminate it.
    def berthing_fee(self):
        if game.location.detail == "surface":
            print("Charging 100 Cr berthing fee.")
            self.debit(Credits(100))
            self.berth_expiry = ImperialDate(self.current_date.day + 6, self.current_date.year)

    def renew_berth(self, date):
        days_extra = date - self.berth_expiry
        if days_extra == 1:
            unit = "day"
        else:
            unit = "days"
        print(f"Renewing berth on {date} for {days_extra} {unit}.")
        self.debit(Credits(days_extra * 100))
        self.berth_expiry = ImperialDate(date.day + days_extra, date.year)

# We'll use the standard Imperial calendar, though that didn't
# yet exist in Traveller '77
# year is 365 consecutively numbered days
# date displayed as DDD-YYYY
# seven day weeks and four week months are used to refer to
# lengths of time, but rarely to establish dates
# (of course fun math, 7 * 4 * 12 = 336, so we are missing
# 29 days - but since week/month are really just durations
# it shouldn't matter)

# right now we only have refreshing the cargo depot weekly as an
# event, but there will be more:
#    * monthly loan payment
#    * annual maintenance
#    * monthly crew salaries
#    * daily berthing fees for extended stays
# other operational costs might better be handled as resource modeling:
#    * fuel
#    * life support

# also need to advance the calendar while in-system
# RAW says that ships typically take two trips per month:
# each jump is one week, and they spend a week buying & selling
# cargo, finding passengers, and on shore leave

# two approaches:
#    * give each action a cost in days
#    * advance the calendar only on jump and liftoff (the latter
#        perhaps with a message like 'you spent a week on Yorbund')

# for the former, does it add up to about a week? and do we want the
# player to be fiddling with time as well as money and space?
#    * to/from jump point - 1 day each
#    * to/from orbit - no time, don't want to privilege highport
#    * buy cargo (and load into ship) - 1 day
#    * sell cargo (and load into ship) - 1 day
#    * find passengers (and embark) - 1 day
#    * find freight (and load into ship) - 1 day
#    * listing hold/depot contents - no time
#    * refuelling - no time at port, 1 day to skim 
#    * recharging life support?
#    * financial transactions - no time
#
# easily 6-7 days if the player does all activities
# but if they want to go fast, jump in, skim fuel, jump out - just
# one day? or even no delay if they have reserve fuel.

class Calendar:
    def __init__(self):
        self.current_date = ImperialDate(1,1105)
        self.observers = []

    @property
    def day(self):
        return self.current_date.day

    @day.setter
    def day(self, value):
        self.current_date.day = value
        if self.current_date.day >= 366:
            self.current_date.day = self.day - 365
            self.year += 1
        for observer in self.observers:
            observer.notify(self.current_date)

    @property
    def year(self):
        return self.current_date.year

    @year.setter
    def year(self, value):
        self.current_date.year = value
        for observer in self.observers:
            observer.notify(self.current_date)

    def plus_day(self):
        self.day += 1

    def plus_week(self):
        self.day += 7

    def plus_month(self):
        self.day += 28

    def plus_year(self):
        self.year += 1

    def __repr__(self):
        return f"{self.current_date}"

    def add_observer(self, observer):
        self.observers.append(observer)

class ImperialDate:
    def __init__(self, day, year):
        self.day = day
        self.year = year
        if self.day > 365:
            self.day -= 365
            self.year += 1

    def __repr__(self):
        return f"{self.day:03.0f}-{self.year}"

    def __eq__(self, other):
        return self.day == other.day and self.year == other.year

    def __gt__(self, other):
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other):
        return self == other or self > other

    def __sub__(self, other):
        return self.day - other.day

    def copy(self):
        return ImperialDate(self.day, self.year)

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()
        self.location = StarSystem("Yorbund", 5, 5, 5, 5, self.date.current_date) 
        self.ship = Ship()
        self.financials = Financials(10000000, self.date.current_date)

        # BUG: this will break when we jump to a new system, fix!
        self.date.add_observer(self.location.depot)
        self.date.add_observer(self.financials)

    def run(self):
        self.commands = grounded
        self.running = True
        while self.running:
            pr_yellow_on_red(f"\n{self.date} : You are {self.location.description()}.")
            print(f"Credits: {self.financials.balance}"
                  f"\tFree hold space: {self.ship.free_space()} tons")
            command = input("Enter a command (? to list):  ")
            for c in self.commands:
                if command.lower() == c.key:
                    print(c.message)
                    c.action()

    def quit(self):
        self.running = False

    def list_commands(self):
        for c in self.commands:
            print(f"{c.key} - {c.description}")

    def liftoff(self):
        self.location.liftoff()
        self.commands = orbit

    def land(self):
        self.location.land()
        self.financials.berthing_fee()
        self.commands = grounded

    def outbound_to_jump(self):
        self.location.to_jump_point()
        self.commands = jump

    def inbound_from_jump(self):
        self.location.from_jump_point()
        self.commands = orbit

    def leave(self):
        self.location.leave_trade()
        self.commands = grounded

    def to_trade(self):
        self.location.join_trade()
        self.commands = trade

    def jump(self):
        pass

game = Game()

always = [Command('q', 'Quit',
                  game.quit,
                  'Goodbye.'),
          Command('?', 'List commands',
                  game.list_commands,
                  'Available commands:'),
          Command('c', 'Cargo hold contents',
                  game.ship.cargo_hold,
                  'Contents of cargo hold:'),
          Command('w', 'Wait a week',
                  game.date.plus_week,
                  'Waiting')]

grounded = always + [Command('l', 'Lift off to orbit', 
                             game.liftoff,
                             'Lifting off to orbit.'),
                     Command('t', 'Trade',
                             game.to_trade,
                             'Trading goods.')]
grounded = sorted(grounded, key=lambda command: command.key)

orbit = always + [Command('g', 'Go to jump point',
                          game.outbound_to_jump,
                          'Travelling to jump point.'),
                  Command('l', 'Land on surface',
                          game.land,
                          f"Landing on {game.location.name}")]
orbit = sorted(orbit, key=lambda command: command.key)

jump = always + [Command('j', 'Jump to new system',
                         game.jump,
                         'Executing jump sequence!'),
                 Command('i', 'Inbound to orbit',
                         game.inbound_from_jump,
                         f"Travel in to orbit {game.location.name}")]
jump = sorted(jump, key=lambda command: command.key)

trade = always + [Command('l', 'Leave trade interaction',
                          game.leave,
                          'Leaving trader depot.'),
                  Command('g', 'Show goods for sale',
                          game.location.depot.goods,
                          'Available cargo loads:'),
                  Command('b', 'Buy cargo',
                          game.location.depot.buy_cargo,
                          'Purchasing cargo'),
                  Command('s', 'Sell cargo',
                          game.location.depot.sell_cargo,
                          'Selling cargo')]
trade = sorted(trade, key=lambda command: command.key)

if __name__ == '__main__':
    game.run()

# Trading procedure (Traveller 77 Book 2 pp. 42-4)
#
# Once per week, throw d66 to determine best cargo
#   DMs per world population
# Determine quantity
# Purchase if desired, up to limits of quantity
#   and available cargo space
# Partial purchases incur 1% fee
# Determine price of goods by 2d6 roll on table
#   DMs per skills, brokers, world characteristics
#
# Can sell cargo on a (different?) world
# Sale price by 2d6 roll on table
#   DMs per skills, brokers, world characteristics

# So overall sequence would be:
# Enter trade depot and see available goods
# Choice: wait a week, purchase some or all, jump to new system
# (And at any point can sell cargo in the hold)

# Other elements we will need:
#   time/calendar (so we will want to display current time...)
#   world characteristics
#   cargo tables
#   bank account (also need to display/query this...)
#   brokers for hire
#   character skills
#
# Not covered in this section, but eventually will want
# starship economics (Book 2 pp. 5-8)
# Operating expenses:
#   fuel
#   life support
#   routine maintenance
#   crew salaries
#   berthing costs
#   bank payment
#
# The starship economics section also covers freight
# shipping (flat rate - above is speculation) - add
# this option eventually. Also passengers.

# Ship design and customization is another potential
# area to explore. We'll assume a simple standard design
# (like the Free Trader) to start with.

# The star map will be a whole 'nother thing. A couple
# potential approaches:
#   Traveller subsector maps, whether generated or
#     loaded from a file
#   On-demand world generation - of course will need
#     to persist these systems as they are created

# UI thoughts:
#  as long as we're text-based, might want to play with
#  more ANSI code formatting to distinguish various things
#
#  also think about persistent display sections, rather than
#  always having to query data points
#
#  will need to make all the input much more robust - it needs
#  to handle bogus input appropriately

    # Comments about individual cargo unit_size assessment, prune
    # through this and retain if any is useful...
    # ---------------------------------------------------
    # This data might belong in the cargo tables rather than here
    # also, the RAW is very handwavy about tonnage for individual items,
    # basically says "figure it out" - only some of these items
    # are in the equipment list, so I'll fill in something plausible
    # as best I can
    # 
    # Equipment list comparisons drawn from Book 3 (pp.16-7)
    #
    # Also need to consider that tonnage should be _displacement tons_
    # not mass, so fiddle with the numbers supplied as necessary
    # and there's packing material to consider too, as they call out in
    # the example on Book 2 p. 43
    #
    # Per Traders & Gunboats p. 5, a 1.5m deck plan square, floor to
    # ceiling, is half a displacement ton - so a 100-ton ship has
    # 200 grid squares in theory. Yes, cargo hold ceilings might be
    # higher than 3m, but this is a good enough basis for converting
    # length/width into displacement numbers.
    #
    # Of course if we're dipping into sources later than the original
    # three LBB, then we should be able to look all this up directly.
    #
    # Another observation - Traveller 77 trading setup does not consider
    # Tech Level at all. Some of the items below might not be 
    # producible on a given (low-tech) world. Can hand-wave by 
    # assuming they are off-world products being warehoused here...
    # 
    # We'll assume the aircraft are less dense than the ground vehicles
    # and fiddle with mass to volume ratios accordingly
    #
    # assume TL5 Fixed Wing Aircraft based on price
    # weight 5 tons, cargo 5 tons, length 15m, wingspan 15m

    # assume TL8 Air/Raft based on price
    # weight 4 tons, cargo 4 tons
    # the Scout/Courier deck plans in Traderes & Gunboats
    # allocates 12 grid squares to its Air/Raft, so 6 d-tons

    # not listed - base this on ship's computers
    # closest fit is the Model/2bis, which costs a bit more
    # (12MCr vs 10), and displaces 2 tons

    # assume TL6 All Terrain Vehicle based on price
    # weight 10 tons

    # assume TL6 Armored Fighting Vehicle based on price
    # weight 10 tons

    # not listed, will need to guesstimate
    # let's just assign it the same stats as ATV/AFV

# --------------------------------------------------------------
# Consolidating TO_DO list:

#  * [DONE] Create a currency class to keep value vs. display straight
#  * [DONE] Deprecate and remove credit_string() function
#  * [DONE] Add (basic) math/comparison operators to currency class
#            (add more operators as needed)
#  * [    ] Change purchase/sale DMs from lists to hashes to improve data
#            entry and validation
#  * [DONE] Regenerate cargo for sale weekly (and reset price adjustment)
#  * [    ] Review Calendar increment scenarios, remove speculative options
#  * [    ] Review Calendar.plus_year() for whether it should notify observers
#  * [DONE] Add 'wait a week' command
#  * [DONE] Display current date
#  * [    ] Advance calendar for in-system activities
#  * [    ] Add fuel system to Ship, and corresponding mechanics like
#            refuelling costs, skimming, check fuel before jump, etc.
#  * [    ] Skimming as jump point action, assuming gas giants present in 
#            StarSystem (abstract the outer system for this purpose)
#  * [    ] Add life support system to Ship and corresponding mechanics like
#            recharging costs, check level before jump, etc.
#  * [DONE] Add extended berthing fee mechanism
#  * [    ] Add annual maintenance
#  * [    ] Add monthly loan payment
#  * [    ] Add monthly crew salaries
#  * [    ] Protect input from bad data - one example, non-numeric
#            values cause crashes
#  * [    ] Extract confirmation input loop to a reusble function
#  * [    ] Make type dunder methods more robust with NotImpemented etc.
#  * [....] Make StarSystem.__eq__ more robust
#  * [DONE] Create an unload_cargo method to consolidate proper handling
#  * [DONE] Add crew skills and their influence on sale prices
#  * [    ] Add crew members with skills
#  * [DONE] Add brokers and their influence on sale prices
#  * [    ] Review interpretation that skills/brokers only apply to sales
#  * [DONE] Prevent immediate resale of bought cargo
#            (current solution just prevents sale to source world, may want
#             to add a time element - simplest would be to reset the source_world
#             field to None, but later for Merchant Prince we may want to retain it)
#  * [    ] Move cargo data to separate data file
#  * [    ] Add different ship types and ship design
#  * [    ] Replace dummy/test data with 'real' values
#  * [    ] Add a transaction ledger to Financial class
#  * [    ] Add freight shipping
#  * [    ] Add passengers
#  * [    ] Add multiple star systems and map (whether loaded or generated
#            and whether in advance or on the fly)
#  * [    ] Create a proper UWP class and generator in the StarSystem ctor
#  * [....] Adjust UI elements, play with more ANSI codes
#  * [    ] If we want to expand beyond just the trade model, add 
#            ship encounters (Book 2 p. 36), hijacking, piracy, etc.
#  * [    ] Distinguish between highport and downport
#  * [    ] Refactoring and tests!!!
#  * [    ] pylint/pydocstyle scrub
