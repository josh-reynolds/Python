import math
from engine import *

class Orbiter:
    def __init__(self, x, y, radius, o_radius, o_velocity):
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.o_radius = o_radius
        self.o_velocity = o_velocity

        self.theta = 0
        self.update()

    def update(self):
        self.x = self.o_radius * math.cos(self.theta)
        self.y = self.o_radius * math.sin(self.theta)
        self.theta += self.o_velocity

    def draw(self):
        x = self.center_x + self.x
        y = self.center_y + self.y

        screen.draw.line((0,0,0), (self.center_x, self.center_y), (x,y))
        screen.draw.circle(x, y, self.radius, (0,255,0), 0)
        screen.draw.circle(x, y, self.radius, (0,0,0), 1)
        screen.draw.circle(self.center_x, self.center_y, self.radius//2, (255,0,0), 0)
