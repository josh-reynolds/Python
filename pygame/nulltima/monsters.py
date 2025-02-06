import math
import random
import unittest
import pygame
import game
import actor
import effects

# monster fields: name, hit_points, damage, experience, images
monsters = {0:('Orc', 1, 1, 1, ['orc_0.png', 'orc_1.png']),
            1:('Broo', 2, 2, 2, ['broo_0.png', 'broo_1.png'])}

class Monster(actor.Actor):
    images = {}

    def __init__(self, coordinate, level, monster_type):
        super().__init__(coordinate, level)
        if level:
            level.add_observer(self)
        self.name = monsters[monster_type][0]
        self.hit_points = monsters[monster_type][1]
        self.damage = monsters[monster_type][2]
        self.experience = monsters[monster_type][3]
        if self.name not in Monster.images:
            image_files = monsters[monster_type][4]
            Monster.images[self.name] = [pygame.image.load('./images/' + x) for x in image_files]
        self.images = Monster.images[self.name]

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
        game.Game.level.effects.append(effects.MeleeAttack(target.pos, self.level))
        if random.random() < 0.5:
            target.hit_points -= self.damage
            game.Game.message_queue.append(('Hit!', False))
        else:
            game.Game.message_queue.append(('Miss', False))
        game.Game.message_queue.append(('{} attacks'.format(self.name), False)) # showing in console out of
                                                                  # order, so small temporary
                                                                  # hack here
    
    def update(self):
        super().update()
        if self.hit_points < 1:
            game.Game.level.monsters.remove(self)
            game.Game.level.remove_observer(self)
            game.Game.level.player.experience += self.experience
            game.Game.score += self.experience

    def __repr__(self):
        return "Monster{}".format(self.pos)

class MonsterTestCase(unittest.TestCase):
    def setUp(self):
        coordinate = (5,5)
        self.m = Monster(coordinate, None, 0)

    def test_constructing_a_monster(self):
        self.assertEqual(self.m.pos, (5,5))
        self.assertEqual(self.m.name, 'Orc')

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
