import math
import unittest
import pygame
import game
import actor

class Monster(actor.Actor):
    images = []

    def __init__(self, coordinate, level):
        super().__init__(coordinate, level)
        if not Monster.images:
            Monster.images = [pygame.image.load("./images/monster_0.png"),
                              pygame.image.load("./images/monster_1.png")]
        self.images = Monster.images

    def think(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            dx = grid_coord[0] - self.level.grid.center[0]
            dy = grid_coord[1] - self.level.grid.center[1]
            sx = -int(math.copysign(1,dx))
            sy = -int(math.copysign(1,dy))
    
            rx = 0
            ry = 0
            if abs(dx) > 1 or abs(dy) > 1:
                max_dist = max(abs(dx), abs(dy))
    
                if abs(dx) == max_dist:
                    rx = sx
    
                if abs(dy) == max_dist:
                    ry = sy
    
            self.move(rx, ry)
    
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
