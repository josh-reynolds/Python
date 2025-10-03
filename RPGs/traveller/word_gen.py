"""Contains functions to randomly generate words and names."""
import random
import unittest

def get_world_name():
    with open("./words.txt", 'r', encoding='utf-8') as in_file:
        word = random_line(in_file)[:-1]   # strip trailing newline
    return word

# From Stack Overflow 3540288
# Waterman's 'Reservoir Algorithm' from Knuth ACP
def random_line(a_file):
    line = next(a_file)
    for num, a_line in enumerate(a_file, 2):
        if random.randrange(num):
            continue
        line = a_line
    return line

class WordGenTestCase(unittest.TestCase):
    """Tests word generation functions."""

    def test_get_world_name_strips_newline(self):
        self.assertNotEqual(get_world_name()[-1], "\n")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
