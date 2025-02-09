import unittest
import game

class Actor:
    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level
        self.time = 0
        self.images = []
        self.current_image = 0
        self.animation_delay = 60

    def update(self):
        self.time += 1
        if self.time > self.animation_delay:
            self.time = 0
            self.current_image = (self.current_image + 1) % len(self.images)

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            game.Game.screen.blit(self.images[self.current_image], screen_coord)

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.pos = (self.pos[0] + dx,
                        self.pos[1] + dy)

    def can_move(self, dx, dy):
        grid_coord = self.level.grid.from_world(self.pos)
        destination = (grid_coord[0] + dx,
                       grid_coord[1] + dy)
        passable = self.level.grid[destination].is_passable
        vacant = self.level.grid.is_vacant(self.level.grid.to_world(destination))

        return passable and vacant

class ActorTestCase(unittest.TestCase):
    def setUp(self):
        coordinate = (100, 100)
        self.a = Actor(coordinate, None)
        self.a.images = [0, 1, 2]

    def test_constructing_an_actor(self):
        self.assertEqual(self.a.pos, (100,100))
        self.assertEqual(self.a.level, None)
        self.assertEqual(self.a.time, 0)
        self.assertEqual(self.a.images, [0, 1, 2])
        self.assertEqual(self.a.current_image, 0)
        self.assertEqual(self.a.animation_delay, 60)

    def test_updating_an_actor(self):
        self.a.update()
        self.assertEqual(self.a.time, 1)

    def test_updating_an_actor(self):
        for i in range(self.a.animation_delay + 1):
            self.a.update()
        self.assertEqual(self.a.time, 0)
        self.assertEqual(self.a.current_image, 1)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
