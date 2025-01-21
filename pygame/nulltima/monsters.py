import unittest

class Monster:
    def __init__(self, coordinate):
        self.pos = coordinate

    def update(self):
        pass

    def draw(self, screen):
        pass

    def move(self, dx, dy):
        pass
    
    def __repr__(self):
        return "Monster({})".format(self.pos)

def monster(coordinate):
    return Monster(coordinate)

class MonsterTestCase(unittest.TestCase):
    def setUp(self):
        coordinate = (5,5)
        self.m = monster(coordinate)

    def test_constructing_a_monster(self):
        self.assertEqual(self.m.pos, (5,5))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
