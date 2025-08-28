def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

# probably will have a graph of Locations
# connections are world - orbit - jump point - other system jump point
# what if we collapse?
# instead of location, we have 'system'
# with a flag to indicate surface/orbit/jump
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

def quit_game():
    global running
    running = False

def list_commands():
    global commands
    for c in commands:
        print(f"{c.key} - {c.description}")

def cargo_hold():
    global hold
    for item in hold:
        print(item)

def jump():
    pass

def liftoff():
    global location, commands, orbit
    location.liftoff()
    commands = orbit

def land():
    global location, commands, grounded
    location.land()
    commands = grounded

def outbound_to_jump():
    global location, commands, jump
    location.to_jump_point()
    commands = jump

def inbound_from_jump():
    global location, commands, orbit
    location.from_jump_point()
    commands = orbit

def leave():
    global location, commands, grounded
    location.leave_trade()
    commands = grounded

def to_trade():
    global location, commands, trade
    location.join_trade()
    commands = trade

def goods():
    global cargo
    for i,item in enumerate(cargo):
        print(f"{i} - {item}")

def buy_cargo():
    global cargo
    item_number = input('Enter cargo number to buy ')
    # TO_DO:
    #  remove purchased item from cargo
    #  add purchased item to hold
    #  deduct cost from credit balance

def sell_cargo():
    global cargo
    item_number = input('Enter cargo number to sell ')
    # TO_DO:
    #  remove purchased item from hold
    #  no need to add purchased item to cargo
    #  add price to credit balance
    
class Cargo:
    def __init__(self, name, tonnage, price):
        self.name = name
        self.tonnage = tonnage
        self.price = price

    def __repr__(self):
        return f"{self.name} - {self.tonnage} tons - {self.price} Cr"
        
location = System("Yorbund")
hold = [Cargo("Grain", 20, 100)]
cargo = [Cargo("Steel", 50, 500)]

always = [Command('q', 'Quit',
                  quit_game,
                  'Goodbye.'),
          Command('?', 'List commands',
                  list_commands,
                  'Available commands:'),
          Command('c', 'Cargo hold contents',
                  cargo_hold,
                  'Contents of cargo hold:')]
grounded = always + [Command('l', 'Lift off to orbit', 
                             liftoff,
                             'Lifting off to orbit.'),
                     Command('t', 'Trade',
                             to_trade,
                             'Trading goods.')]
grounded = sorted(grounded, key=lambda command: command.key)

orbit = always + [Command('g', 'Go to jump point',
                          outbound_to_jump,
                          'Travelling to jump point.'),
                  Command('l', 'Land on surface',
                          land,
                          f"Landing on {location.name}")]
orbit = sorted(orbit, key=lambda command: command.key)

jump = always + [Command('j', 'Jump to new system',
                         jump,
                         'Executing jump sequence!'),
                 Command('i', 'Inbound to orbit',
                         inbound_from_jump,
                         f"Travel in to orbit {location.name}")]
jump = sorted(jump, key=lambda command: command.key)

trade = always + [Command('l', 'Leave trade interaction',
                          leave,
                          'Leaving trader depot.'),
                  Command('g', 'Show goods for sale',
                          goods,
                          'Available cargo loads:'),
                  Command('b', 'Buy cargo',
                          buy_cargo,
                          'Purchasing cargo'),
                  Command('s', 'Sell cargo',
                          sell_cargo,
                          'Selling cargo')]
trade = sorted(trade, key=lambda command: command.key)

commands = grounded
running = True
while running:
    pr_red(f"\nYou are {location.description()}.")
    command = input("Enter a command (? to list).  ")
    for c in commands:
        if command.lower() == c.key:
            print(c.message)
            c.action()
