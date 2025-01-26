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
        coordinate = (100, 100)
        self.p = Player(coordinate, None)

    def test_constructing_a_player(self):
        self.assertEqual(self.p.pos, (100,100))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
