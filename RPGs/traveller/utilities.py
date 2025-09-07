from random import randint

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

def pr_yellow_on_red(string):
    """Print string to console, yellow text on red background."""
    print(f"\033[1;33;41m {string}\033[00m")

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m{string}\033[00m")

def pr_green(string):
    """Print string to console, colored green."""
    print(f"\033[92m{string}\033[00m")

def int_input(prompt):
    while True:
        try:
            result = int(input(prompt))
            break
        except ValueError:
            print("Please input a number.")
    return result
