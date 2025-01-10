import unittest
from common import *

class Grid:
    def __init__(self, width, height, left, top, cell_width, cell_height):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.contents = [[BLACK for x in range(width)] for x in range(height)]

    def update(self):
        pass

    def draw(self, screen):
        for y, row in enumerate(self.contents):
            for x, cell in enumerate(row):
                coord = (x * self.cell_width + self.left,
                         y * self.cell_height + self.top,
                         self.cell_width,
                         self.cell_height)
                pygame.draw.rect(screen, cell, coord, 1)


def grid(width, height, left, top, cell_width, cell_height):
    return Grid(width, height, left, top, cell_width, cell_height)

class GridTestCase(unittest.TestCase):
    def test_constructing_a_grid(self):
        g = grid(10, 7, 11, 9, 4, 3)
        self.assertEqual(g.width, 10)
        self.assertEqual(g.height, 7)
        self.assertEqual(g.left, 11)
        self.assertEqual(g.top, 9)
        self.assertEqual(g.cell_width, 4)
        self.assertEqual(g.cell_height, 3)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
