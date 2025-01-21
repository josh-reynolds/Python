import unittest
import pygame
import game

class Monster:
    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level

    def update(self):
        pass

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.world_to_grid(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            pygame.draw.ellipse(game.Game.screen, pygame.Color('red'), screen_coord)

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
