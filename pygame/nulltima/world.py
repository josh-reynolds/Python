import unittest
from common import *

# terrain fields: color, impassable?
#    color will be phased out in favor of tile images
#    we will want an opaque? field at some point as well
#    I don't think these yet merit a full class - tuple 
#    data records are enough for now
terrains = {0:(BLACK, True), 
            1:(WHITE, False), 
            2:(RED, False), 
            3:(GREEN, False), 
            4:(BLUE, True),
            5:(CYAN, False), 
            6:(MAGENTA, False), 
            7:(YELLOW, False)}

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
