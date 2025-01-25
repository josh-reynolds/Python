import unittest
import pygame
from actor import Actor

class Player(Actor):
    images = []

    def __init__(self, coordinate, level):
        super().__init__(coordinate, level)
        if not Player.images:
            Player.images = [pygame.image.load("./images/player_0.png"),
                             pygame.image.load("./images/player_1.png")]
        self.images = Player.images

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
