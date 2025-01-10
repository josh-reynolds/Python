import unittest
from common import *
from world import world, terrains

class Grid:
    def __init__(self, width, height, left, top, cell_width, cell_height):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.contents = [[BLACK for x in range(width)] for x in range(height)]
        self.world = world()
        self.offset = (0,0)

    def __getitem__(self, coord):
        return self.world.get_cell(coord[0] + self.offset[0], 
                                   coord[1] + self.offset[1])

    def update(self):
        pass

    def draw(self, screen):
        for y, row in enumerate(self.contents):
            for x, cell in enumerate(row):
                coord = (x * self.cell_width + self.left,
                         y * self.cell_height + self.top,
                         self.cell_width,
                         self.cell_height)
                color = self[x,y]
                pygame.draw.rect(screen, color, coord)
                pygame.draw.rect(screen, cell, coord, 1)


def grid(width, height, left, top, cell_width, cell_height):
    return Grid(width, height, left, top, cell_width, cell_height)

class GridTestCase(unittest.TestCase):
    def setUp(self):
        self.g = grid(3, 3, 11, 9, 4, 3)
        self.g.world.contents = [[0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0]]

    def test_constructing_a_grid(self):
        self.assertEqual(self.g.width, 3)
        self.assertEqual(self.g.height, 3)
        self.assertEqual(self.g.left, 11)
        self.assertEqual(self.g.top, 9)
        self.assertEqual(self.g.cell_width, 4)
        self.assertEqual(self.g.cell_height, 3)

    def test_coordinate_mapping_to_world(self):

        self.assertEqual(self.g[2,2], terrains[1])

    def test_coordinate_offset(self):
        self.g.offset = (1,1)

        self.assertEqual(self.g[1,1], terrains[1])

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
