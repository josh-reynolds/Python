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
            9:(GREY, False)}       # boundary color

class World:
    def __init__(self, contents):
        self.contents = contents

    def get_cell(self, x, y):
        if (x >= 0 and x < len(self.contents[0]) and
            y >= 0 and y < len(self.contents)):
                return terrains[self.contents[x][y]]
        else:
            return terrains[9]

    def open_file(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()
        contents = []
        for line in lines:
            new_line = [int(x) for x in line.split()]
            contents.append(new_line)
        self.contents = contents
        f.close()

    def width(self):
        return len(self.contents[0])

    def height(self):
        return len(self.contents)

def world(contents=[]):
    return World(contents)

class WorldTestCase(unittest.TestCase):
    def test_constructing_a_world(self):
        contents = [1]
        w = world(contents)
        self.assertEqual(w.contents, [1])

    def test_loading_a_world_file(self):
        w = world()
        w.open_file("test_world.txt")
        self.assertEqual(w.get_cell(1,1), terrains[3])

    def test_world_width_and_height(self):
        w = world()
        w.open_file("test_world.txt")
        self.assertEqual(w.width(), 10)
        self.assertEqual(w.height(), 10)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
