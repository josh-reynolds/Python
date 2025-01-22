import unittest
import pygame

class Player:
    image = None

    def __init__(self):
        if not Player.image:
            Player.image = pygame.image.load("./images/player.png")

    def update(self):
        pass

    def draw(self, screen):
        pass

    def move(self, dx, dy):
        pass

def player():
    return Player()

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.p = player()

    def test_constructing_a_player(self):
        pass

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
