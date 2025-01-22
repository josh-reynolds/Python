import math
import unittest
import pygame
import game

class Monster:
    image = None

    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level
        if not Monster.image:
            Monster.image = pygame.image.load("./images/monster.png")

    def update(self):
        pass

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            game.Game.screen.blit(Monster.image, screen_coord)

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

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.pos = (self.pos[0] + dx,
                        self.pos[1] + dy)

    def can_move(self, dx, dy):
        grid_coord = self.level.grid.from_world(self.pos)
        destination = (grid_coord[0] + dx,
                       grid_coord[1] + dy)

        return self.level.grid[destination][1]
    
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
