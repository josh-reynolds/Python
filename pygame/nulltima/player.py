import unittest
import pygame

class Player:
    images = []

    def __init__(self, coordinate):
        self.pos = coordinate
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

    def draw(self, screen):
        Game.screen.blit(Player.images[self.current_image], self.player_position)

    def move(self, dx, dy):
        pass

def player(coordinate):
    return Player(coordinate)

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.p = player()

    def test_constructing_a_player(self):
        pass

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
