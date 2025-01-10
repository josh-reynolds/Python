import unittest
from common import *

class World:
    def __init__(self, contents):
        self.contents = contents

    def get_cell(self, x, y):
        return BLUE

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
