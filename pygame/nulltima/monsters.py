import math
import random
import unittest
import pygame
import game
import actor

class Monster(actor.Actor):
    images = []

    def __init__(self, coordinate, level):
        super().__init__(coordinate, level)
        if level:
            level.add_observer(self)
        if not Monster.images:
            Monster.images = [pygame.image.load("./images/monster_0.png"),
                              pygame.image.load("./images/monster_1.png")]
        self.images = Monster.images
        self.hit_points = 1

    def on_notify(self, last_move, player_position):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            dx = grid_coord[0] - self.level.grid.center[0]
            dy = grid_coord[1] - self.level.grid.center[1]
            sx = -int(math.copysign(1,dx))
            sy = -int(math.copysign(1,dy))
    
            rx = 0
            ry = 0
            if abs(dx) > 1 or abs(dy) > 1:
                max_dist = max(abs(dx), abs(dy))
    
                if abs(dx) == max_dist:
                    rx = sx
    
                if abs(dy) == max_dist:
                    ry = sy
    
                self.move(rx, ry)
            else:
                self.attack(game.Game.level.player)

    def attack(self, target):
        if random.random() < 0.5:
            target.hit_points -= 1
            game.Game.message_queue.append(('Hit!', False))
        else:
            game.Game.message_queue.append(('Miss', False))
        game.Game.message_queue.append(('{} attacks'.format(self), False)) # showing in console out of
                                                                  # order, so small temporary
                                                                  # hack here
    
    def update(self):
        super().update()
        if self.hit_points < 1:
            game.Game.level.monsters.remove(self)
            game.Game.level.remove_observer(self)
            game.Game.level.player.experience += 1


    def __repr__(self):
        return "Monster{}".format(self.pos)

class MonsterTestCase(unittest.TestCase):
    def setUp(self):
        coordinate = (5,5)
        self.m = Monster(coordinate, None)

    def test_constructing_a_monster(self):
        self.assertEqual(self.m.pos, (5,5))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
