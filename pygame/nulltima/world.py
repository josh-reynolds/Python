import unittest
from common import *

terrains = {0:BLACK, 1:WHITE, 2:RED, 3:GREEN, 4:BLUE}

class World:
    def __init__(self, contents):
        self.contents = contents

    def get_cell(self, x, y):
        return terrains[self.contents[x][y]]

def world(contents=[]):
    return World(contents)

class WorldTestCase(unittest.TestCase):
    def test_constructing_a_world(self):
        contents = [1]
        w = world(contents)
        self.assertEqual(w.contents, [1])

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
