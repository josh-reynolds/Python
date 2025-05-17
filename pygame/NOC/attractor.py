from engine import *
from pvector import PVector

G = 0.4

class Attractor:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        self.mass = 20

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.mass*2, (0,0,255))
        screen.draw.circle(self.location.x, self.location.y, self.mass*2, (0,0,0), 1)

    def attract(self, mover):
        force = PVector.sub(self.location, mover.location)
        distance = force.mag()
        distance = max(min(distance, 25), 5)
        force.normalize()
        strength = (G * self.mass * mover.mass) / (distance * distance)
        force * strength
        return force

class Repulsor(Attractor):
    def attract(self, mover):
        force = PVector.sub(self.location, mover.location)
        distance = force.mag()
        distance = max(min(distance, 25), 5)
        force.normalize()
        strength = (G * self.mass * mover.mass) / (distance * distance)
        force * strength
        force * -0.01
        return force
