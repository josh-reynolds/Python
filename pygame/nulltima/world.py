import unittest
from common import *

# terrain fields: color, passable?
#    color will be phased out in favor of tile images
#    we will want an opaque? field at some point as well
#    I don't think these yet merit a full class - tuple 
#    data records are enough for now
terrains = {0:(BLACK, False), 
            1:(WHITE, True), 
            2:(RED, True), 
            3:(GREEN, True), 
            4:(BLUE, False),
            5:(CYAN, True), 
            6:(MAGENTA, True), 
            7:(YELLOW, True),
            8:(BROWN, False),
            9:(GREY, False)}

class World:
    def __init__(self, contents):
        self.contents = contents

    def get_cell(self, x, y):
        return terrains[self.contents[x][y]]

    def open_file(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()
        contents = []
        for line in lines:
            new_line = [int(x) for x in line.split()]
            contents.append(new_line)
        self.contents = contents
        f.close()

def world(contents=[]):
    return World(contents)

class WorldTestCase(unittest.TestCase):
    def test_constructing_a_world(self):
        contents = [1]
        w = world(contents)
        self.assertEqual(w.contents, [1])

    def test_loading_a_world_file(self):
        contents = []
        w = world(contents)
        w.open_file("test_world.txt")
        self.assertEqual(w.get_cell(1,1), terrains[3])


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
