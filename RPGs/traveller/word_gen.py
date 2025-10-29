"""Contains functions to randomly generate words and names."""
import random
from io import TextIOWrapper

def get_world_name() -> str:
    """Return a random word from the words.txt file."""
    with open("./words.txt", 'r', encoding='utf-8') as in_file:
        word = random_line(in_file)[:-1]   # strip trailing newline
    expand = random.randint(1,6)
    if expand == 1:
        word = "New " + word
    elif expand == 2:
        word += random.choice([" Station", " Platfom", " Colony", " Depot", " Base",
                              " Claim", " Exchange", " Landing", " Port", " Relay",
                              " Terminal"])
    elif expand == 3:
        digits = random.randint(2,12)
        word += f"-{digits}"
    return word

# From Stack Overflow 3540288
# Waterman's 'Reservoir Algorithm' from Knuth ACP
def random_line(a_file: TextIOWrapper) -> str:
    """Return a random line from a_file."""
    line = next(a_file)
    for num, a_line in enumerate(a_file, 2):
        if random.randrange(num):
            continue
        line = a_line
    return line
