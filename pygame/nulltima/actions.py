import pygame
from pygame.locals import *
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

    # might be better if these classes know nothing
    # about explicit keys - should pass the direction
    # in instead...
    def execute(self, direction_key):
        if direction_key == K_UP:
            direction = (0,-1)
        if direction_key == K_DOWN:
            direction = (0,1)
        if direction_key == K_LEFT:
            direction = (-1,0)
        if direction_key == K_RIGHT:
            direction = (1,0)
        coordinate = (self.target.pos[0] + direction[0],
                      self.target.pos[1] + direction[1])
        for monster in game.Game.level.monsters:
            if monster.pos == coordinate:
                print("Attacking {}".format(monster))
                self.target.attack(monster)
                game.Game.level.effects.append(effects.MeleeAttack(coordinate, game.Game.level))
                return
        print("No target")

class Debug(Action):
    def __init__(self, target):
        self.name = 'Debug'
        self.target = target
    def execute(self):
        print(self.target.action_queue)

class NextLevel(Action):
    def __init__(self, target):
        self.name = 'NextLevel'
        self.target = target
    def execute(self):
        self.target.score = self.target.level.player.experience
        self.target.level = self.target.levels[1]
        self.target.level.enter()
