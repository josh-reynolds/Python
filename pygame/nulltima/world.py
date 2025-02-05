import unittest
import pygame

# terrain fields: name, passable?, opaque?, smart?, image
terrains = {0:("Occluded", False, False, False, "tile_0.png"),
            1:("Plains", True, False, False, "tile_1.png"), 
            2:("Brush", True, False, False, "tile_2.png"), 
            3:("Forest", True, True, False, "tile_3.png"), 
            4:("Water", False, False, False, ["tile_4_1.png", "tile_4_2.png"]),
            5:("Desert", True, False, False, "tile_5.png"), 
            6:("Swamp", True, False, False, "tile_6.png"), 
            7:("Hills", True, False, False, "tile_7.png"),
            8:("Mountains", False, True, False, "tile_8.png"),
            9:("Out of Bounds", False, False, False, "tile_9.png"),
            10:("Road", True, False, True, "road_")}

class Base:        # need a better name for this one
    def __init__(self, data):
        self.name = data[0]
        self.is_passable = data[1]
        self.is_opaque = data[2]
        self.is_smart = data[3]

class Terrain(Base):
    def __init__(self, data):
        super().__init__(data)
        self.file = data[4]
        self.image = pygame.image.load('./images/' + self.file)

    def get_image(self, neighbors=0):
        return self.image

    def __repr__(self):
        return f'Terrain({self.name})'

class AnimatedTerrain(Base):
    def __init__(self, data):
        super().__init__(data)
        self.files = data[4]
        self.images = [pygame.image.load('./images/' + x) for x in self.files]
        self.time = 0
        self.current_image = 0
        self.animation_delay = 80

    def update(self):
        self.time += 1
        if self.time > self.animation_delay:
            self.time = 0
            self.current_image = (self.current_image + 1) % len(self.images)

    def get_image(self, neighbors=0):
        return self.images[self.current_image]

    def __repr__(self):
        return f'AnimatedTerrain({self.name})'

class SmartTerrain(Base):
    def __init__(self, data):
        super().__init__(data)
        self.file_base = './images/' + data[4]
        self.images = []
        for filename in [self.file_base + f'{x:02}' + '.png' for x in range(16)]:
            self.images.append(pygame.image.load(filename))

    # neighbors is a bit flag count of four orthogonal neighbors going
    # clockwse: N=1, E=2, S=4, W=8
    # so this is a four-bit number ranging from 0 to 15
    def get_image(self, neighbors):
        return self.images[neighbors]

    def __repr__(self):
        return f'SmartTerrain({self.name})'

class World:
    def __init__(self, contents=[]):
        self.contents = contents
        self.terrains = {}
        for index in terrains:
            if isinstance(terrains[index][4], list):
                self.terrains[index] = AnimatedTerrain(terrains[index])
            elif terrains[index][3]:
                self.terrains[index] = SmartTerrain(terrains[index])
            else:
                self.terrains[index] = Terrain(terrains[index])

    def update(self):
        for index in self.terrains:
            if isinstance(self.terrains[index], AnimatedTerrain):
                self.terrains[index].update()

    def get_cell(self, y, x):
        if (x >= 0 and x < len(self.contents[0]) and
            y >= 0 and y < len(self.contents)):
                index = self.contents[y][x]
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
