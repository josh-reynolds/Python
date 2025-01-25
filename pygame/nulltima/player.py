import unittest
import pygame
import actor

class Player(actor.Actor):
    images = []

    def __init__(self, coordinate, level):
        super().__init__(coordinate, level)
        if not Player.images:
            Player.images = [pygame.image.load("./images/player_0.png"),
                             pygame.image.load("./images/player_1.png")]
        self.images = Player.images

    def no_action(self):
        pass

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.p = Player((100,100), None)

    def test_constructing_a_player(self):
        pass

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
