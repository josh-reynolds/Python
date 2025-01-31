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
        self.name = "Lord McGonigal"
        self.hit_points = 100
        self.experience = 0
        self.observers = []

    def update(self):
        super().update()
        for observer in self.observers:
            observer.on_notify(self.name, self.hit_points)

    def add_observer(self, observer):
        self.observers.append(observer)

    def attack(self, target):
        target.hit_points -= 1

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        coordinate = (100, 100)
        self.p = Player(coordinate, None)

    def test_constructing_a_player(self):
        self.assertEqual(self.p.pos, (100,100))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
