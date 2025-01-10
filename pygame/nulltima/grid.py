import unittest

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height

def grid(width, height):
    return Grid(width, height)

class GridTestCase(unittest.TestCase):
    def test_constructing_a_grid(self):
        g = grid(10, 7)
        self.assertEqual(g.width, 10)
        self.assertEqual(g.height, 7)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
