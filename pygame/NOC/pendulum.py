import math
from pvector import PVector
from engine import *

class Pendulum:
    def __init__(self, origin, r):
        self.origin = origin
        self.r = r
        self.angle = math.pi/4
        self.a_velocity = 0
        self.a_accel = 0
        self.damping = 0.995

    def update(self):
        gravity = 0.4
        self.a_accel = (-1 * gravity/self.r) * math.sin(self.angle)
        self.a_velocity += self.a_accel
        self.angle += self.a_velocity
        self.a_velocity *= self.damping

    def draw(self):
        location = PVector(self.r * math.sin(self.angle),
                           self.r * math.cos(self.angle))
        location + self.origin
        screen.draw.line((0,0,0), (self.origin.x, self.origin.y), (location.x, location.y))
        screen.draw.circle(location.x, location.y, 16, (0,0,255))
