import unittest
import pygame
import game

class Player:
    images = []

    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level
        if not Player.images:
            Player.images = [pygame.image.load("./images/player_0.png"),
                             pygame.image.load("./images/player_1.png")]
        self.time = 0
        self.current_image = 0

    def update(self):
        self.time += 1
        if self.time > 25:
            self.time = 0
            if self.current_image == 0:
                self.current_image = 1
            else:
                self.current_image = 0

    def draw(self):
        grid_coord = self.level.grid.from_world(self.pos)
        screen_coord = self.level.grid.to_screen(grid_coord)
        game.Game.screen.blit(Player.images[self.current_image], screen_coord)

    def move(self, dx, dy):
        pass

def player(coordinate, level):
    return Player(coordinate, level)

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.p = player((100,100), None)

    def test_constructing_a_player(self):
        pass

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
