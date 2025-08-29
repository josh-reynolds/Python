def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

class System:
    def __init__(self, name):
        self.name = name
        self.detail = "surface"

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
    def __init__(self, name, tonnage, price):
        self.name = name
        self.tonnage = tonnage
        self.price = price

    def __repr__(self):
        return f"{self.name} - {self.tonnage} tons - {self.price} Cr"

class CargoDepot:
    def __init__(self):
        self.cargo = [Cargo("Steel", 50, 500)]

    def goods(self):
        for i,item in enumerate(self.cargo):
            print(f"{i} - {item}")

    def buy_cargo(self):
        self.goods()
        item_number = input('Enter cargo number to buy ')
        # TO_DO:
        #  remove purchased item from cargo
        #  add purchased item to hold
        #  deduct cost from credit balance

    def sell_cargo(self):
        global ship
        ship.cargo_hold()
        item_number = input('Enter cargo number to sell ')
        # TO_DO:
        #  remove purchased item from hold
        #  no need to add purchased item to cargo
        #  add price to credit balance

class Ship:
    def __init__(self):
        self.hold = [Cargo("Grain", 20, 100)]

    def cargo_hold(self):
        for i,item in enumerate(self.hold):
            print(f"{i} - {item}")

class Game:
    def __init__(self):
        self.running = False
        self.location = System("Yorbund")

    def run(self):
        self.commands = grounded
        self.running = True
        while self.running:
            pr_red(f"\nYou are {self.location.description()}.")
            command = input("Enter a command (? to list).  ")
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

depot = CargoDepot()
ship = Ship()
game = Game()

always = [Command('q', 'Quit',
                  game.quit,
                  'Goodbye.'),
          Command('?', 'List commands',
                  game.list_commands,
                  'Available commands:'),
          Command('c', 'Cargo hold contents',
                  ship.cargo_hold,
                  'Contents of cargo hold:')]

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
                          depot.goods,
                          'Available cargo loads:'),
                  Command('b', 'Buy cargo',
                          depot.buy_cargo,
                          'Purchasing cargo'),
                  Command('s', 'Sell cargo',
                          depot.sell_cargo,
                          'Selling cargo')]
trade = sorted(trade, key=lambda command: command.key)

if __name__ == '__main__':
    game.run()

# Trading procedure (Traveller 77 Book 2 pp. 42-4
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
