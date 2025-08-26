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

    def liftoff(self):
        if self.detail == "surface":
            self.detail = "orbit"

    def to_jump_point(self):
        if self.detail == "orbit":
            self.detail = "jump"

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

def trade():
    pass

def jump():
    pass
        
location = System("Yorbund")
hold = []

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
                     location.liftoff,
                     'Lifting off to orbit.'),
                     Command('t', 'Trade',
                             trade,
                             'Trading goods.')]
orbit = always + [Command('g', 'Go to jump point',
                  location.to_jump_point,
                  'Travelling to jump point.')]
jump = always + [Command('j', 'Jump to new system',
                         jump,
                         'Executing jump sequence!')]
# TO_DO: should sort commands on key

commands = grounded
running = True
while running:
    pr_red(f"\nYou are {location.description()}.")
    command = input("Enter a command (? to list).  ")
    for c in commands:
        if command.lower() == c.key:
            print(c.message)
            c.action()
