import unittest
import game

class Monster:
    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level

    def update(self):
        pass

    def draw(self, screen):
        pass

    def move(self, dx, dy):
        pass
    
    def __repr__(self):
        return "Monster({})".format(self.pos)

def monster(coordinate, level):
    return Monster(coordinate, level)

class MonsterTestCase(unittest.TestCase):
    def setUp(self):
        game.GameMock()
        level = game.Level()
        coordinate = (5,5)
        self.m = monster(coordinate, level)

    def test_constructing_a_monster(self):
        self.assertEqual(self.m.pos, (5,5))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
