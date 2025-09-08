from credits import Credits
from utilities import pr_yellow_on_red
from calendar import Calendar, ImperialDate
from ship import Ship
from cargo import Cargo, CargoDepot
from star_system import StarSystem

class Command:
    def __init__(self, key, description, action, message):
        self.key = key
        self.description = description
        self.action = action
        self.message = message

class Financials:
    def __init__(self, balance, current_date):
        self.balance = Credits(balance)
        self.current_date = current_date.copy()
        self.berth_expiry = ImperialDate(self.current_date.day + 6, self.current_date.year)
        self.salary_due = ImperialDate(self.current_date.day + 28, self.current_date.year)

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount

    def notify(self, date):
        self.current_date = date.copy()
        if date > self.berth_expiry and game.location.on_surface():
            self.renew_berth(date)

        if date > self.salary_due:
            self.pay_salaries(date)

    # Book 2 p. 7:
    # Average cost is CR 100 to land and remain for up to six days;
    # thereafter, a CR 100 per day fee is imposed for each
    # additional day spent in port. In some locations this fee will
    # be higher, while at others local government subsidies will 
    # lower or eliminate it.
    def berthing_fee(self, on_surface):
        if on_surface:
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

    def pay_salaries(self, date):
        amount = Credits(game.ship.crew_salary())
        print(f"Paying crew salaries on {self.salary_due} for {amount}.")
        self.debit(amount)
        self.salary_due = ImperialDate(self.salary_due.day + 28, self.salary_due.year)

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()
        self.ship = Ship()
        self.financials = Financials(10000000, self.date.current_date)
        self.location = StarSystem("Yorbund", 5, 5, 5, 5, self.date.current_date, self.ship, self.financials) 
        self.ship.load_cargo(Cargo("Grain", 20, 300, 1, [-2,1,2,0,0,0], [-2,0,0,0,0,0]))

        # BUG: this will break when we jump to a new system, fix!
        self.date.add_observer(self.location.depot)
        self.date.add_observer(self.financials)

    def run(self):
        self.commands = grounded
        self.running = True
        while self.running:
            pr_yellow_on_red(f"\n{self.date} : You are {self.location.description()}.")
            print(f"Credits: {self.financials.balance}"
                  f"\tFree hold space: {self.ship.free_space()} tons"
                  f"\tFuel: {self.ship.current_fuel}/{self.ship.fuel_tank} tons")
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
        self.financials.berthing_fee(self.location.on_surface())
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
#  * [....] Review Calendar increment scenarios, remove speculative options
#  * [    ] Review Calendar.year() setter for whether it should notify observers
#  * [DONE] Add 'wait a week' command
#  * [DONE] Display current date
#  * [    ] Advance calendar for in-system activities
#  * [DONE] Add fuel system to Ship
#  * [    ] Add fuel expenditure
#  * [    ] Add refuelling costs at starport
#  * [    ] Add fuel level check before executing jump
#  * [    ] Skimming as jump point action, assuming gas giants present in 
#            StarSystem (abstract the outer system for this purpose)
#  * [    ] Add view StarSystem data action
#  * [    ] Add life support system to Ship and corresponding mechanics like
#            recharging costs, check level before jump, etc.
#  * [DONE] Add extended berthing fee mechanism
#  * [    ] Add annual maintenance
#  * [    ] Add monthly loan payment
#  * [DONE] Add monthly crew salaries
#  * [    ] Add crew members with skills
#  * [    ] Add proper salary calculation per crew member
#  * [DONE] Protect input from bad data - one example, non-numeric
#            values cause crashes
#  * [DONE] Extract confirmation input loop to a reusable function
#  * [    ] Make type dunder methods more robust with NotImpemented etc.
#  * [    ] Add 'plus days' method to ImperialDate
#  * [....] Make StarSystem.__eq__ more robust
#  * [DONE] Create an unload_cargo method to consolidate proper handling
#  * [DONE] Add crew skills and their influence on sale prices
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
#  * [    ] Save game state
#  * [    ] Load game state
#  * [    ] If we want to expand beyond just the trade model, add 
#            ship encounters (Book 2 p. 36), hijacking, piracy, etc.
#  * [    ] RPG lite elements: named crew, brokers, color events & encounters, etc.
#  * [    ] Distinguish between highport and downport
#  * [....] Separate code out into modules
#  * [    ] Refactoring and tests!!!
#  * [    ] pylint/pydocstyle scrub
