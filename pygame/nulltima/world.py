import unittest
import pygame

# terrain fields: name, passable?, opaque?, image
terrains = {0:("Occluded", False, False, "tile_0.png"),
            1:("Plains", True, False, "tile_1.png"), 
            2:("Light Forest", True, False, "tile_2.png"), 
            3:("Deep Forest", True, True, "tile_3.png"), 
            4:("Water", False, False, ["tile_4_1.png", "tile_4_2.png"]),
            5:("Desert", True, False, "tile_5.png"), 
            6:("Swamp", True, False, "tile_6.png"), 
            7:("Hills", True, False, "tile_7.png"),
            8:("Mountains", False, True, "tile_8.png"),
            9:("Out of Bounds", False, False, "tile_9.png")}

class Base:        # need a better name for this one
    def __init__(self, data):
        self.name = data[0]
        self.is_passable = data[1]
        self.is_opaque = data[2]

class Terrain(Base):
    def __init__(self, data):
        super().__init__(data)
        self.file = data[3]
        self.image = pygame.image.load('./images/' + self.file)

    def get_image(self):
        return self.image

class AnimatedTerrain(Base):
    def __init__(self, data):
        super().__init__(data)
        self.files = data[3]
        self.images = [pygame.image.load('./images/' + x) for x in self.files]
        self.time = 0
        self.current_image = 0
        self.animation_delay = 80

    def update(self):
        self.time += 1
        if self.time > self.animation_delay:
            self.time = 0
            if self.current_image == 0:
                self.current_image = 1
            else:
                self.current_image = 0

    def get_image(self):
        return self.images[self.current_image]

class World:
    def __init__(self, contents=[]):
        self.contents = contents
        self.terrains = {}
        for index in terrains:
            if isinstance(terrains[index][3], list):
                self.terrains[index] = AnimatedTerrain(terrains[index])
            else:
                self.terrains[index] = Terrain(terrains[index])

    def update(self):
        for index in self.terrains:
            if isinstance(self.terrains[index], AnimatedTerrain):
                self.terrains[index].update()

    def get_cell(self, x, y):
        if (x >= 0 and x < len(self.contents[0]) and
            y >= 0 and y < len(self.contents)):
                index = self.contents[x][y]
                return self.terrains[index]
        else:
            return self.terrains[9]

    def get_occluded(self):
        return self.terrains[0]

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

class WorldTestCase(unittest.TestCase):
    def test_constructing_a_world(self):
        contents = [1]
        w = World(contents)
        self.assertEqual(w.contents, [1])

    def test_loading_a_world_file(self):
        w = World()
        w.open_file("test_world.txt")
        self.assertEqual(w.get_cell(1,1), w.terrains[3])

    def test_world_width_and_height(self):
        w = World()
        w.open_file("test_world.txt")
        self.assertEqual(w.width(), 10)
        self.assertEqual(w.height(), 10)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
