"""Contains utility functions."""
import json
import re
from os import listdir
from os.path import isfile, join
from random import randint
from typing import Any, List, Dict
from src.format import END_FORMAT, BOLD_GREEN, BOLD_RED

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

def valid_index(value: int, a_list: List) -> bool:
    """Confirm a value is a valid list index."""
    return 0 <= value < len(a_list)

def choose_from(a_list: List, prompt: str) -> int:
    """Present a list to the user, and return their chosen index value."""
    pr_list(a_list)
    choice = -1
    while not valid_index(choice, a_list):
        choice = int_input(prompt)
    return choice

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

def get_files(path: str, extension: str | None=None) -> List[str]:
    """Return a list of all files in the specified directory.

    Also takes an optional extension argument that will filter
    the list of files to just that type.
    """
    files = [f for f in listdir(path) if isfile(join(path, f))]
    if extension:
        files = [f for f in files if f.endswith(extension)]
    files.sort()
    return files

def get_next_file(base_name: str, extension: str) -> str:
    """Return the next file to be created in the 'saves' directory."""
    files = get_files("./saves/", extension)
    pattern = re.compile(base_name + r"_(\d+)." + extension)
    highest = 0
    for file in files:
        match = pattern.match(file)
        if match:
            index = int(match.group(1))
            if index > highest:
                highest = index
    # enforcing two-digits for ordering
    # will still output three+ digit numbers, but
    # ordering will break
    return f"{base_name}_{highest+1:02}.{extension}"

def get_json_data(filename: str) -> Dict[str, Any] | None:
    """Retrieve data from a JSON file.

    Returns a dictionary containing the JSON data, or
    None if the file does not exist.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as a_file:
            return json.load(a_file)
    except FileNotFoundError:
        print(f"{BOLD_RED}File {filename} not found.{END_FORMAT}")
        return None

def get_tokens(string: str, min_tokens: int, max_tokens: int) -> List[str]:
    """Split a string into tokens, validating the expected number is received.

    Tokens in the input string should be delimited by ' - '.
    """
    tokens = string.split(' - ')

    if len(tokens) > max_tokens:
        raise ValueError(f"input string has extra data: '{string}'")

    if len(tokens) < min_tokens:
        raise ValueError(f"input string is missing data: '{string}'")

    return tokens

def is_good_deal(prompt: str, price_adjustment: float) -> bool:
    """Assess whether a given adjustment is a good deal."""
    return (prompt == "sale" and price_adjustment > 1) or \
           (prompt == "purchase" and price_adjustment < 1)

def is_bad_deal(prompt: str, price_adjustment: float) -> bool:
    """Assess whether a given adjustment is a bad deal."""
    return (prompt == "sale" and price_adjustment < 1) or \
           (prompt == "purchase" and price_adjustment > 1)
