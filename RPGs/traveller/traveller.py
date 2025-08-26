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

location = System("Yorbund")
hold = []
commands = []
grounded = [Command('l', 'Lift off to orbit', 
                    location.liftoff,
                    "Lifting off to orbit.")]
orbit = [Command('g', 'Go to jump point',
                 location.to_jump_point,
                 "Travelling to jump point.")]
commands = grounded
running = True
while running:
    pr_red(f"\nYou are {location.description()}.")
    command = input("Enter a command (? to list).  ")
    for c in commands:
        if command.lower() == c.key:
            print(c.message)
            c.action()
    if command.lower() == 'q':
        running = False
    if command.lower() == '?':
        # TO_DO: commands should be location-dependent
        for c in commands:
            print(f"{c.key} - {c.description}")
        print("? - List commands")
        print("c - Cargo hold contents")
        print("j - Jump to new system")
        print("q - Quit")
        print("t - Trade")
    if command.lower() == 'c':
        print("Contents of cargo hold:")
        for item in hold:
            print(item)

print("Goodbye.")

