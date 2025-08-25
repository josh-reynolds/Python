def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

class Location:
    def __init__(self, name):
        self.name = name

world = Location("Yorbund")
hold = []

while True:
    pr_red(f"\nYou are on {world.name}.")
    command = input("Enter a command (? to list).  ")
    if command.lower() == 'q':
        break
    if command.lower() == '?':
        # TO_DO: commands should be location-dependent
        print("? - List commands")
        print("c - Cargo hold contents")
        print("j - Jump to new system")
        print("l - Lift off to orbit")
        print("q - Quit")
        print("t - Trade")
    if command.lower() == 'c':
        print("Contents of cargo hold:")
        for item in hold:
            print(item)

print("Goodbye.")

