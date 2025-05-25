from pvector import PVector
from engine import *

class Spring:
    k = 0.1

    def __init__(self, x, y, l):
        self.anchor = PVector(x,y)
        self.len = l

    def connect(self, bob):
        force = PVector.sub(bob.location, self.anchor)
        d = force.mag()
        stretch = d - self.len

        force = PVector.normalize(force)
        force * (-1 * Spring.k * stretch)

        bob.apply_force(force)

    def draw(self):
        screen.draw.rect((self.anchor.x-5, self.anchor.y-5,10,10), (128,128,128), 0)

    def draw_line(self, bob):
        screen.draw.line((0,0,0), (bob.location.x, bob.location.y), (self.anchor.x, self.anchor.y))
