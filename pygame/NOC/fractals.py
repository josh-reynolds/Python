import math
from random import uniform, randint
from engine import screen
from pvector import PVector
from screen_matrix import line, translate, rotate, push_matrix, pop_matrix

def draw_circle(x, y, radius):
    screen.draw.circle(x, y, radius, (0,0,0), 1)
    if radius > 2:
        draw_circle(x + radius/2, y, radius/2)
        draw_circle(x - radius/2, y, radius/2)
        draw_circle(x, y + radius/2, radius/2)
        draw_circle(x, y - radius/2, radius/2)

def cantor(x, y, l):
    if l >= 1:
        screen.draw.line((0,0,0), (x,y), (x+l,y))
        y += 20
        cantor(x, y, l/3)
        cantor(x + l * 2/3, y, l/3)

def branch(length):
    line(0, 0, 0, -length)
    translate(0, -length)

    length *= 0.66

    if length > 2:
        n = randint(1,4)
        for i in range(n):
            theta = uniform(-math.pi/2,math.pi/2)
            push_matrix()
            rotate(theta)
            branch(length)
            pop_matrix()

class KochLine:
    def __init__(self, a, b):
        self.start = a.copy()
        self.end = b.copy()

    def draw(self):
        screen.draw.line((0,0,0), (self.start.x, self.start.y), (self.end.x, self.end.y))

    def koch_a(self):
        return self.start.copy()

    def koch_b(self):
        v = PVector.sub(self.end, self.start)
        v / 3
        return PVector.add(self.start, v)

    def koch_c(self):
        v = PVector.sub(self.end, self.start)
        v / 3
        a = PVector.add(self.start, v)
        if self.end.x < self.start.x:
            v.rotate(120)
        else:
            v.rotate(-60)
        return PVector.add(a,v)

    def koch_d(self):
        v = PVector.sub(self.end, self.start)
        v * 2
        v / 3
        return PVector.add(self.start, v)

    def koch_e(self):
        return self.end.copy()

class KochCurve:
    def __init__(self, start, end, depth):
        self.start = start
        self.end = end
        self.depth = depth

        self.lines = []
        self.lines.append(KochLine(self.start, self.end))
        for i in range(self.depth):
            self.generate()

    def generate(self):
        next_lines = []

        for kl in self.lines:
            a = kl.koch_a()
            b = kl.koch_b()
            c = kl.koch_c()
            d = kl.koch_d()
            e = kl.koch_e()

            next_lines.append(KochLine(a,b))
            next_lines.append(KochLine(b,c))
            next_lines.append(KochLine(c,d))
            next_lines.append(KochLine(d,e))

        self.lines = next_lines.copy()

    def draw(self):
        for kl in self.lines:
            kl.draw()
