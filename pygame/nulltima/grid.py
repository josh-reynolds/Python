import unittest
import math
import pygame
from pygame.locals import *
from world import world, terrains
from player import player
from game import Game, Level

class Grid:
    def __init__(self, width, height, left, top, cell_width=32, cell_height=32):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.contents = [[Color('black') for x in range(width)] for x in range(height)]
        self.world = world()
        self.offset = (0,0)
        self.center = (self.width//2, self.height//2)
        self.player = player()

        self.file = 'large_world.txt'
        self.world.open_file(self.file)

        Game.level.nodes.append(self)

    def __getitem__(self, index):
        return self.world.get_cell(index[1] + self.offset[1], 
                                   index[0] + self.offset[0])

    def update(self):
        pass

    # will move the image loading pieces - don't need to keep doing that
    # every frame...
    def draw(self):
        player_image = pygame.image.load("./images/player.png")
        for iy, row in enumerate(self.contents):
            for ix, cell in enumerate(row):
                coord = self.index_to_screen(ix,iy)
                image = pygame.image.load("./images/" + self[ix,iy][3])
                if self.is_occluded(ix,iy):
                    image = pygame.image.load("./images/tile_0.png")
                Game.screen.blit(image, coord)
                #pygame.draw.rect(screen, cell, coord, 1)

        player_position = self.index_to_screen(self.center[0], self.center[1])
        Game.screen.blit(player_image, player_position)

    def is_occluded(self, ix, iy):
        cells = self.bresenham(ix, iy)
        for cell in cells:
            if self[cell[0], cell[1]][2]:        # field codes getting too 'magic numbery'
                return True
        return False

    # assumes we are tracing a line to the center of the grid
    # since this consumes index coordinates, we have an origin in 
    # the top-left corner and are only dealing with one cartesian quadrant
    # (plus it's upside down) - may need to adjust, and possibly simplify.
    # starting with the full algorithm
    def bresenham(self, ix, iy):
        cells = []

        x = self.center[0]
        y = self.center[1]
        dx = ix - x
        dy = iy - y
        ax = 2 * abs(dx)
        ay = 2 * abs(dy)
        sx = math.copysign(1, dx)
        sy = math.copysign(1, dy)

        if ax > ay:
            d = ay - ax/2
            while True:
                if self.not_endpoint(x, y, ix, iy):
                    cells.append((int(x), int(y)))
                if x == ix:
                    return cells
                if d >= 0:
                    y = y + sy
                    d = d - ax
                x = x + sx
                d = d + ay
        else:
            d = ax - ay/2
            while True:
                if self.not_endpoint(x, y, ix, iy):
                    cells.append((int(x), int(y)))
                if y == iy:
                    return cells
                if d >= 0:
                    x = x + sx
                    d = d - ay
                y = y + sy
                d = d + ax

    def not_endpoint(self, x1, y1, x2, y2):
        return (x1,y1) != (x2,y2) and (x1,y1) != (self.center[0], self.center[1])

    def index_to_screen(self, ix, iy):
        return (ix * self.cell_width + self.left,
                iy * self.cell_height + self.top,
                self.cell_width,
                self.cell_height)

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.offset = self.offset[0] + dx, self.offset[1] + dy

    def can_move(self, dx, dy):
        return self[self.center[0] + dx, 
                    self.center[1] + dy][1]

class GridTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        Level()
        self.g = Grid(3, 3, 11, 9, cell_width=4, cell_height=3)
        self.g.world.contents = [[0, 0, 0, 0, 0],
                                [0, 1, 1, 1, 0],
                                [0, 1, 1, 1, 0],
                                [0, 1, 1, 1, 0],
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

    def test_converting_grid_coords_to_screen(self):
        coords = self.g.index_to_screen(1,1)

        self.assertEqual(coords[0], 15)
        self.assertEqual(coords[1], 12)
        self.assertEqual(coords[2], 4)
        self.assertEqual(coords[3], 3)

    def test_move_check(self):
        self.assertEqual(self.g.can_move(0,1), True)
        self.assertEqual(self.g.can_move(1,0), True)
        self.assertEqual(self.g.can_move(0,-1), False)
        self.assertEqual(self.g.can_move(-1,0), False)

    def test_bresenham_calculation(self):
        g = Grid(11, 11, 5, 5, 5, 5)
        g.world.contents = [[0 for x in range(20)] for x in range(20)]

        b = g.bresenham(0,0)
        self.assertEqual(b, [(4,4), (3,3), (2,2), (1,1)])

        b = g.bresenham(10,10)
        self.assertEqual(b, [(6,6), (7,7), (8,8), (9,9)])

        b = g.bresenham(0,10)
        self.assertEqual(b, [(4,6), (3,7), (2,8), (1,9)])

        b = g.bresenham(10,0)
        self.assertEqual(b, [(6,4), (7,3), (8,2), (9,1)])

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
