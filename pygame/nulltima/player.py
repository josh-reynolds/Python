import unittest
import pygame
import game
from actor import Actor

class Player(Actor):
    images = []

    def __init__(self, coordinate, level):
        super().__init__(coordinate, level)
        if not Player.images:
            Player.images = [pygame.image.load("./images/player_0.png"),
                             pygame.image.load("./images/player_1.png")]

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            game.Game.screen.blit(Player.images[self.current_image], screen_coord)

    def no_action(self):
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
