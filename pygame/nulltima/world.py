import unittest
from common import *

class World:
    def __init__(self):
        pass

    def get_cell(self, x, y):
        return BLUE

def world():
    return World()

class WorldTestCase(unittest.TestCase):
    def test_constructing_a_world(self):
        w = world()

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
