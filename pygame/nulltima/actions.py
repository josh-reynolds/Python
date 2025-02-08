import unittest
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
        self.name = 'Next Level'
        self.target = target
    def execute(self):
        self.target.next_level()

class Restart(Action):
    def __init__(self, target):
        self.name = 'Restart'
        self.target = target
    def execute(self):
        self.target.restart()

# ---------------------------------------------------------------------------
class PlayerMock():
    def __init__(self):
        self.hit_points =0

class TargetMock():
    def __init__(self):
        self.restarted = False
        self.level = 0
        self.player = PlayerMock()

    def move(self, dx, dy):
        self.pos = (dx, dy)

    def restart(self):
        self.restarted = True

    def next_level(self):
        self.level = 1

# ---------------------------------------------------------------------------
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

    # pass execution doesn't need testing

    def test_constructing_a_quit(self):
        t = TargetMock()
        q = Quit(t)
        self.assertEqual(q.name, "Quit")
        self.assertEqual(q.target, t)

    def test_executing_a_quit(self):
        t = TargetMock()
        q = Quit(t)
        q.execute()
        self.assertEqual(t.running, False)

    def test_constructing_an_attack(self):
        t = TargetMock()
        a = Attack(t)
        self.assertEqual(a.name, "Attack")
        self.assertEqual(a.target, t)

    def test_executing_an_attack(self):      # saving for later...
        t = TargetMock()
        a = Attack(t)

    def test_constructing_a_debug(self):
        t = TargetMock()
        d = Debug(t)
        self.assertEqual(d.name, "Debug")
        self.assertEqual(d.target, t)

    # debug action will change ad hoc as needed
    # not worth writing a unit test

    def test_constructing_a_godmode(self):
        t = TargetMock()
        g = GodMode(t)
        self.assertEqual(g.name, "God Mode")
        self.assertEqual(g.target, t)

    def test_executing_a_godmode(self):
        t = TargetMock()
        g = GodMode(t)
        g.execute()
        self.assertEqual(t.player.hit_points, 1000)

    def test_constructing_a_nextlevel(self):
        t = TargetMock()
        n = NextLevel(t)
        self.assertEqual(n.name, "Next Level")
        self.assertEqual(n.target, t)

    def test_executing_a_nextlevel(self):
        t = TargetMock()
        n = NextLevel(t)
        n.execute()
        self.assertEqual(t.level, 1)

    def test_constructing_a_restart(self):
        t = TargetMock()
        r = Restart(t)
        self.assertEqual(r.name, "Restart")
        self.assertEqual(r.target, t)

    def test_executing_a_restart(self):
        t = TargetMock()
        r = Restart(t)
        r.execute()
        self.assertEqual(t.restarted, True)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

