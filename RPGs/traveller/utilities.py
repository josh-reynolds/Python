"""Contains utility functions."""
from random import randint

def die_roll(count=1):
    total = 0
    for _ in range(count):
        total += randint(1,6)
    return total

def constrain(value, min_val, max_val):
    if value <= min_val:
        return min_val

    if value >= max_val:
        return max_val

    return value

# table from Book 2 p. 42
def actual_value(roll):
    actual_value_table = {2:.4, 3:.5, 4:.7, 5:.8, 6:.9, 7:1, 8:1.1,
                          9:1.2, 10:1.3, 11:1.5, 12:1.7, 13:2, 14:3, 15:4}
    return actual_value_table[roll]

def pr_yellow_on_red(string):
    """Print string to console, yellow text on red background."""
    print(f"\033[1;33;41m {string}\033[00m")

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[1;31;40m{string}\033[00m")

def pr_green(string):
    """Print string to console, colored green."""
    print(f"\033[1;32;40m{string}\033[00m")

def pr_yellow(string):
    """Print string to console, colored yellow."""
    print(f"\033[1;33;40m{string}\033[00m")

def pr_blue(string):
    """Print string to console, colored blue."""
    print(f"\033[1;36;40m{string}\033[00m")

def int_input(prompt):
    while True:
        try:
            result = int(input(prompt))
            break
        except ValueError:
            print("Please input a number.")
    return result

def confirm_input(prompt):
    confirmation = ""
    while confirmation not in ('y', 'n'):
        confirmation = input(prompt)
    return confirmation

def print_list(items):
    for i,item in enumerate(items):
        print(f"{i} - {item}")
