import unittest

class Player:
    def __init__(self, x, y):
        self.position = (x, y)

    def update(self):
        pass

    def draw(self, screen):
        pass

    def move(self, dx, dy):
        pass

def player(x, y):
    return Player(x, y)

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.p = player(3,3)

    def test_constructing_a_player(self):
        self.assertEqual(self.p.position, (3,3))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
