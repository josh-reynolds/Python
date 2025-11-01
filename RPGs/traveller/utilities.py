"""Contains utility functions."""
from os import listdir
from os.path import isfile, join
from random import randint
from typing import Any, List

def die_roll(count: int = 1) -> int:
    """Roll count six-sided dice and return the total."""
    total = 0
    for _ in range(count):
        total += randint(1,6)
    return total

def constrain(value: int, min_val: int, max_val: int) -> int:
    """Constrain a value within a given range."""
    if value <= min_val:
        return min_val

    if value >= max_val:
        return max_val

    return value

def actual_value(roll: int) -> float:
    """Return a value from the table on Book 2 page 42."""
    actual_value_table = {2:.4, 3:.5, 4:.7, 5:.8, 6:.9, 7:1, 8:1.1,
                          9:1.2, 10:1.3, 11:1.5, 12:1.7, 13:2, 14:3, 15:4}
    return actual_value_table[roll]

# see wikipedia page for ANSI codes
HOME = "\033[H"
CLEAR = "\033[2J"
BOLD = "\033[1m"
YELLOW_ON_RED = "\033[1;33;41m"
BOLD_RED = "\033[1;31;40m"
BOLD_GREEN = "\033[1;32;40m"
BOLD_YELLOW = "\033[1;33;40m"
BOLD_BLUE = "\033[1;36;40m"
END_FORMAT = "\033[00m"

#string = "foo bar"
#start = 60 - (len(string)//2)
#print(f"\033[1;30;41m\033[{start}G{string}\033[00m")
#print(f"\033[1m{string}\033[00m")    # bold
#print(f"\033[2m{string}\033[00m")    # faint
#print(f"\033[3m{string}\033[00m")    # italic (same as inverse)
#print(f"\033[4m{string}\033[00m")    # underline
#print(f"\033[5m{string}\033[00m")    # slow blink
#print(f"\033[6m{string}\033[00m")    # fast blink (same as slow)
#print(f"\033[7m{string}\033[00m")    # inverse
#print(f"\033[8m{string}\033[00m")    # hide
#print(f"\033[9m{string}\033[00m")    # strikethrough
#print(f"\033[21m{string}\033[00m")   # dbl. underline (same as underline)

def int_input(prompt: str) -> int:
    """Take input from the user, reprompt if not an integer."""
    while True:
        try:
            result = int(input(prompt))
            break
        except ValueError:
            print("Please input a number.")
    return result

def confirm_input(prompt: str) -> str:
    """Take yes or no input from the user, reprompt until match."""
    confirmation = ""
    while confirmation not in ('y', 'n'):
        confirmation = input(prompt)
    return confirmation

def pr_list(items: list) -> None:
    """Print out a list with its index values."""
    for i,item in enumerate(items):
        print(f"{i} - {item}")

def pr_highlight_list(items: list, highlight: Any, annotation: str = "") -> None:
    """Print out a list with its index values, highlighting specific entries."""
    for i,item in enumerate(items):
        if item == highlight:
            print(f"{BOLD_GREEN}{i} - {item}{annotation}{END_FORMAT}")
        else:
            print(f"{i} - {item}")

def get_lines(filename: str) -> list[str]:
    """Read all lines from filename and return as a list."""
    result = []
    with open(filename, 'r', encoding='utf-8') as a_file:
        for line in a_file:
            result.append(line)
    return result

def dictionary_from(a_string: str) -> dict[str, int]:
    """Convert a specially-formatted string to a dictionary.

    String format is "{key1:value1,key2:value2,key3:value3...}".
    The entire string is surrounded by braces, and does not end
    with a newline character. Key-value pairs are separated by
    commas (with no spaces), and keys are separated from
    values by colons. Values will be converted to integers
    as well.
    """
    contents = a_string[1:-1]  # strip enclosing '{' + '}'
    dictionary = {}
    for item in contents.split(','):
        key, value = item.split(':')
        dictionary[key] = int(value)
    return dictionary

def get_save_files() -> List[str]:
    """Return a list of all files in the saves directory."""
    path = "./saves/"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return files
