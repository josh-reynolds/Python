import unittest
import pygame
import game
import effects

class Action():
    def __init__(self, target):
        pass
    def execute(self):
        pass

class North(Action):
    def __init__(self, target):
        self.name = 'North'
        self.target = target
    def execute(self):
        self.target.move(0,-1)

class South(Action):
    def __init__(self, target):
        self.name = 'South'
        self.target = target
    def execute(self):
        self.target.move(0,1)

class East(Action):
    def __init__(self, target):
        self.name = 'East'
        self.target = target
    def execute(self):
        self.target.move(1,0)

class West(Action):
    def __init__(self, target):
        self.name = 'West'
        self.target = target
    def execute(self):
        self.target.move(-1,0)

class Pass(Action):
    def __init__(self, target):
        self.name = 'Pass'
        self.target = target
    def execute(self):
        pass

class Quit(Action):
    def __init__(self, target):
        self.name = 'Quit'
        self.target = target
    def execute(self):
        self.target.running = False

class Attack(Action):
    def __init__(self, target):
        self.name = 'Attack'
        self.target = target

    def execute(self, direction):
        coordinate = (self.target.pos[0] + direction[0],
                      self.target.pos[1] + direction[1])
        for entity in game.Game.level.monsters + [game.Game.level.player]:
            if entity.pos == coordinate:
                self.target.attack(entity)
                game.Game.level.effects.append(effects.MeleeAttack(coordinate, game.Game.level))
                return

class Debug(Action):
    def __init__(self, target):
        self.name = 'Debug'
        self.target = target
    def execute(self):
        print(self.target.components[0].count_matching_neighbors(self.target.player.pos, debug=True))

class GodMode(Action):
    def __init__(self, target):
        self.name = 'God Mode'
        self.target = target
    def execute(self):
        self.target.player.hit_points = 1000   # hack, if needed we should do a real god mode

class NextLevel(Action):
    def __init__(self, target):
        self.name = 'NextLevel'
        self.target = target
    def execute(self):
        self.target.next_level()

class Restart(Action):
    def __init__(self, target):
        self.name = 'Restart'
        self.target = target
    def execute(self):
        self.target.restart()

class TargetMock():
    def move(self, dx, dy):
        self.pos = (dx, dy)

class ActionTestCase(unittest.TestCase):
    def test_constructing_a_north(self):
        t = TargetMock()
        n = North(t)
        self.assertEqual(n.name, "North")
        self.assertEqual(n.target, t)

    def test_executing_a_north(self):
        t = TargetMock()
        n = North(t)
        n.execute()
        self.assertEqual(t.pos, (0, -1))

    def test_constructing_a_south(self):
        t = TargetMock()
        s = South(t)
        self.assertEqual(s.name, "South")
        self.assertEqual(s.target, t)

    def test_executing_a_south(self):
        t = TargetMock()
        s = South(t)
        s.execute()
        self.assertEqual(t.pos, (0, 1))

    def test_constructing_an_east(self):
        t = TargetMock()
        e = East(t)
        self.assertEqual(e.name, "East")
        self.assertEqual(e.target, t)

    def test_executing_an_east(self):
        t = TargetMock()
        e = East(t)
        e.execute()
        self.assertEqual(t.pos, (1, 0))

    def test_constructing_a_west(self):
        t = TargetMock()
        w = West(t)
        self.assertEqual(w.name, "West")
        self.assertEqual(w.target, t)

    def test_executing_a_west(self):
        t = TargetMock()
        w = West(t)
        w.execute()
        self.assertEqual(t.pos, (-1, 0))

    def test_constructing_a_pass(self):
        t = TargetMock()
        p = Pass(t)
        self.assertEqual(p.name, "Pass")
        self.assertEqual(p.target, t)

# Quit
# Attack
# Debug
# GodMode
# NextLevel
# Restart
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

