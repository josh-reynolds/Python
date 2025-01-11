import unittest
from common import *
from world import world, terrains
from player import player

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
        self.center = (self.width//2, self.height//2)
        self.player = player(self.center[0], self.center[1])

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

        player_position = (self.player.position[0] * self.cell_width + self.left,
                           self.player.position[1] * self.cell_height + self.top,
                           self.cell_width,
                           self.cell_height)
        pygame.draw.ellipse(screen, BLACK, player_position)


    def move(self, dx, dy):
        newx = self.offset[0] + dx
        if newx < 0:
            newx = 0
        if newx > len(self.world.contents[0]) - self.width:
            newx = len(self.world.contents[0]) - self.width

        newy = self.offset[1] + dy
        if newy < 0:
            newy = 0
        if newy > len(self.world.contents) - self.height:
            newy = len(self.world.contents) - self.height

        self.offset = (newx, newy)

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

    def test_moving_a_grid(self):
        self.g.move(1,2)

        self.assertEqual(self.g.offset, (1, 2))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
