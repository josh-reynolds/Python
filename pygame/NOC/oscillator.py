import math
from random import uniform, randint
from pvector import PVector
from engine import *

class Oscillator:
    def __init__(self, WIDTH, HEIGHT):
        self.angle = PVector(0,0)
        self.velocity = PVector(uniform(-0.05,0.05), uniform(-0.05,0.05))
        self.amplitude = PVector(randint(0, WIDTH//2), randint(0, HEIGHT//2))
        self.max_width = WIDTH
        self.max_height = HEIGHT

    def oscillate(self):
        self.angle + self.velocity

    def draw(self):
        x = math.sin(self.angle.x) * self.amplitude.x
        y = math.cos(self.angle.y) * self.amplitude.y

        #screen.draw.line((0,0,0), (WIDTH//2,HEIGHT//2), (x + WIDTH//2, y + HEIGHT//2))
        screen.draw.circle(x + self.max_width//2, y + self.max_height//2, 20, (0,0,255))
        screen.draw.circle(x + self.max_width//2, y +self.max_height//2, 20, (0,0,0), 1)
