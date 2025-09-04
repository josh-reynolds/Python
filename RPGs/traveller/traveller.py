from random import randint

def pr_yellow_on_red(string):
    """Print string to console, yellow text on red background."""
    print(f"\033[1;33;41m {string}\033[00m")

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

def pr_green(string):
    """Print string to console, colored green."""
    print(f"\033[92m {string}\033[00m")

def die_roll():
    return randint(1,6)

def constrain(value, min_val, max_val):
    if value <= min_val:
        return min_val
    elif value >= max_val:
        return max_val
    else:
        return value

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

def credit_string(value):
    val = round(value)
    suffix = "Cr"
    if val >= 1000000:
        suffix = "MCr"
        val = val/1000000
    return f"{val:,} {suffix}"

class System:
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
    def __init__(self, name, quantity, price, unit_size, purchase_dms, sale_dms):
        self.name = name
        self.quantity = Cargo.determine_quantity(quantity)
        self.price = Credits(price)
        self.unit_size = unit_size

        # DMs are in order: agricultural, non-agricultural, industrial,
        #                   non-industrial, rich, poor
        self.purchase_dms = purchase_dms
        self.sale_dms = sale_dms

    def __repr__(self):
        return f"{self.name} - {Cargo.quantity_string(self, self.quantity)} - {self.price}/unit"

    @property
    def tonnage(self):
        return self.quantity * self.unit_size

    def quantity_string(cargo, quantity):
        string = f"{quantity}"
        if cargo.unit_size == 1:
            string += " tons"
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

        actual_value = {2:.4, 3:.5, 4:.7, 5:.8, 6:.9, 7:1, 8:1.1,
                        9:1.2, 10:1.3, 11:1.5, 12:1.7, 13:2, 14:3, 15:4}
        if self.prices[item_number] > 0:
            price_adjustment = self.prices[item_number]
        else:
            roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
            price_adjustment = actual_value[roll]

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

        funds = game.financials.balance
        if cost.amount > funds:
            print("You do not have sufficient funds.")
            print(f"Your available balance is {credit_string(funds)}.")
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
                          cargo.purchase_dms, cargo.sale_dms)
        game.ship.load_cargo(purchased)

        game.financials.debit(cost.amount)

    def sell_cargo(self):
        global game
        game.ship.cargo_hold()
        item_number = int(input('Enter cargo number to sell '))
        if item_number >= len(game.ship.hold):
            print("That is not a valid cargo ID.")
            return

        cargo = game.ship.hold[item_number]
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

        actual_value = {2:.4, 3:.5, 4:.7, 5:.8, 6:.9, 7:1, 8:1.1,
                        9:1.2, 10:1.3, 11:1.5, 12:1.7, 13:2, 14:3, 15:4}

        roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
        price_adjustment = actual_value[roll]

        sale_price = Credits(cargo.price.amount * price_adjustment * quantity)
        if price_adjustment > 1:
            pr_function = pr_green
        elif price_adjustment < 1:
            pr_function = pr_red
        else:
            pr_function = print
        pr_function(f"That quantity will sell for {sale_price}.")

        confirmation = ""
        while confirmation != 'y' and confirmation != 'n':
            confirmation = input(f"Would you like to sell " 
                                 f"{Cargo.quantity_string(cargo, quantity)} of "
                                 f"{cargo.name} for {sale_price} (y/n)? ")

        if confirmation == 'n':
            print("Cancelling sale.")
            return

        # proceed with the transaction
        if quantity == cargo.quantity:
            game.ship.hold.remove(cargo)
        else:
            cargo.quantity -= quantity

        game.financials.credit(sale_price.amount)

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
        self.hold = [Cargo("Grain", 20, 300, 1, [-2,1,2,0,0,0], [0,0,0,0,0,0])]
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

class Financials:
    def __init__(self, balance):
        self.balance = balance

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount

# We'll use the standard Imperial calendar, though that didn't
# yet exist in Traveller '77
# year is 365 consecutively numbered days
# date displayed as DDD-YYYY
# seven day weeks and four week months are used to refer to
# lengths of time, but rarely to establish dates
# (of course fun math, 7 * 4 * 12 = 336, so we are missing
# 29 days - but since week/month are really just durations
# it shouldn't matter)
#
# operations we'll need:
#   [DONE] proper display formatting, including leading zeroes
#   [DONE] increment day/week/month/year (no need to decrement)
#   [DONE] roll over year as appropriate
#   [    ] possibly trigger other events, like re-rolling cargo
#            that may end up a separate 'timer' responsibility, we'll see

# probably a lot of ways to do this... here's a couple ideas:
#    * the 'wait a week' action does at least two things:
#        advance the date
#        trigger any weekly events
#        tricky bit: monthly events, how do they know?
#    * have timers that can be created with specific intervals
#        when the date advances, they check to see if the new
#        date is higher than their target, then take action if so
#        and then create a new timer at the next interval
#        timers would be Observers of the Calendar
#        tricky bit: if multiple intervals are jumped past, need
#        to check the new timer until all are in the clear

# right now we only have refreshing the cargo depot weekly as an
# event, but there will be more:
#    * monthly loan payment
#    * annual maintenance
#    * monthly crew salaries
#    * daily berthing fees for extended stays
# other operational costs might better be handled as resource modeling:
#    * fuel
#    * life support

# the second (timer) model seems more robust, and in line with how
# some computer GUI toolkits handle events, so I'll give that a try

# open question where the timer should live - we want them to be cleaned
# up when the entity that cares goes out of scope (as when jumping to a
# new world). I think the timer should live in the entity, and the 
# list in the Calendar class is a callback reference. We'll want to make
# sure lifespan and object cleanup is happening correctly - otherwise 
# we could accumulate a large list of timers firing against worlds other
# than the current. May be able to deal with that by using Game.location
# (which should always point to the current system) to point to the 
# right entity (though even then, we wouldn't want more than on timer
# to fire against that target).

# OK, mulling this over - it's overly complex. This should be doable
# with a simple Observer, no need for an intermediary object. The 
# CargoDepot registers with the Calendar, and is notified when it
# changes. Then it can decide what to do.
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
        # TO_DO: Redundant, but probably harmless. Think through the scenario.
        # Will we ever need this if day.setter has it covered?
        for observer in self.observers:
            observer.notify(self.current_date)

    def plus_day(self):
        self.day += 1

    # TO_DO: Are we ever going to need any increments other
    # than +1 week? Should remove others if not. Review.
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

    def __repr__(self):
        return f"{self.day:03.0f}-{self.year}"

    def __eq__(self, other):
        return self.day == other.day and self.year == other.year

    def __gt__(self, other):
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other):
        return self == other or self > other

    def copy(self):
        return ImperialDate(self.day, self.year)

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()
        self.location = System("Yorbund", 5, 5, 5, 5, self.date.current_date) 
        self.ship = Ship()
        self.financials = Financials(10000000)

        # BUG: this will break when we jump to a new system, fix!
        self.date.add_observer(self.location.depot)

    def run(self):
        self.commands = grounded
        self.running = True
        while self.running:
            pr_yellow_on_red(f"\n{self.date} : You are {self.location.description()}.")
            print(f"Credits: {credit_string(self.financials.balance)}"
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
        global orbit
        game.location.liftoff()
        game.commands = orbit

    def land(self):
        global grounded
        game.location.land()
        game.commands = grounded

    def outbound_to_jump(self):
        global jump
        game.location.to_jump_point()
        game.commands = jump

    def inbound_from_jump(self):
        global orbit
        game.location.from_jump_point()
        game.commands = orbit

    def leave(self):
        global grounded
        game.location.leave_trade()
        game.commands = grounded

    def to_trade(self):
        global trade
        game.location.join_trade()
        game.commands = trade

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
#  * [....] Deprecate and remove credit_string() function
#  * [    ] Create a proper UWP class and generator in the System ctor
#  * [    ] Change purchase/sale DMs from lists to hashes to improve data
#            entry and validation
#  * [DONE] Regenerate cargo for sale weekly (and reset price adjustment)
#  * [    ] Review Calendar increment scenarios, remove speculative options
#  * [DONE] Add 'wait a week' command
#  * [DONE] Display current date
#  * [    ] Add fuel system to Ship, and corresponding mechanics like
#            refuelling costs, skimming, check fuel before jump, etc.
#  * [    ] Add life support system to Ship and corresponding mechanics like
#            recharging costs, check level before jump, etc.
#  * [    ] Protect input from bad data - one example, non-numeric
#            values cause crashes
#  * [    ] Create an unload_cargo method to consolidate proper handling
#  * [    ] Add crew skills and their influence on sale prices
#  * [    ] Add brokers and their influence on sale prices
#  * [    ] Review interpretation that skills/brokers only apply to sales
#  * [    ] Prevent immediate resale of bought cargo (wait a week? leave and
#            return? Not sure how to properly flag cargo lot yet...)
#  * [    ] Move cargo data to separate data file
#  * [    ] Add different ship types and ship design
#  * [    ] Replace dummy/test data with 'real' values
#  * [    ] Add a transaction ledger to Financial class
#  * [....] Add starship operating expenses
#  * [    ] Add freight shipping
#  * [    ] Add passengers
#  * [    ] Add multiple star systems and map (whether loaded or generated
#            and whether in advance or on the fly)
#  * [....] Adjust UI elements, play with more ANSI codes
#  * [    ] If we want to expand beyond just the trade model, add 
#            ship encounters (Book 2 p. 36), hijacking, piracy, etc.
#  * [    ] Distinguish between highport and downport
#  * [    ] Refactoring and tests!!!
