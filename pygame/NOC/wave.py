import math
from engine import *

class Wave:
    def __init__(self, min_, max_, spacing, velocity, height):
        self.min = min_
        self.max = max_
        self.spacing = spacing
        self.velocity = velocity
        self.height = height
        self.angle = 0

    def draw(self):
        for x in range(self.min, self.max, self.spacing):
            y = (math.sin(self.angle) + 1) * self.height//2
            screen.draw.circle(x, y, 10, (0,255,0))
            screen.draw.circle(x, y, 10, (0,0,0), 1)
            self.angle += self.velocity
