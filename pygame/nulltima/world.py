import unittest

# terrain fields: name, passable?, opaque?, image
#    I don't think these yet merit a full class - tuple 
#    data records are enough for now
terrains = {0:("Occluded", False, False, "tile_0.png"),
            1:("Plains", True, False, "tile_1.png"), 
            2:("Light Forest", True, False, "tile_2.png"), 
            3:("Deep Forest", True, True, "tile_3.png"), 
            4:("Water", False, False, "tile_4.png"),
            5:("Desert", True, False, "tile_5.png"), 
            6:("Swamp", True, False, "tile_6.png"), 
            7:("Hills", True, False, "tile_7.png"),
            8:("Mountains", False, True, "tile_8.png"),
            9:("Out of Bounds", False, False, "tile_9.png")}

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
