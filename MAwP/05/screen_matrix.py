import math
from engine import *
from pvector import PVector

class ScreenMatrix:
    def __init__(self):
        self.reset()

    def __repr__(self):
        return f"({self.origin.x:0.2f}, {self.origin.y:0.2f}) {self.angle:0.2f} : {self.stack}"

    def reset(self):
        self.origin = PVector(0,0)
        self.color = (0,0,0)
        self.angle = 0
        self.stack = []

    def translate(self, target):
        target.rotate(math.degrees(self.angle))
        self.origin + target

    def rotate(self, radians):
        self.angle += radians

    def push_matrix(self):
        self.stack.append((self.origin.copy(), self.angle))

    def pop_matrix(self):
        if len(self.stack) > 0:
            self.origin, self.angle = self.stack.pop()

    def draw_line(self, start, end, width=1):
        s = PVector(*start)
        s.rotate(math.degrees(self.angle))
        s + self.origin

        e = PVector(*end)
        e.rotate(math.degrees(self.angle))
        e + self.origin

        screen.draw.line(self.color, (s.x, s.y), (e.x, e.y), width)

    def draw_circle(self, x, y, radius, color, width=0):
        o = PVector(x,y)
        o.rotate(math.degrees(self.angle))
        o + self.origin

        screen.draw.circle(o.x, o.y, radius, color, width)

    def draw_rect(self, x, y, w, h, color, width=0):
        # not supporting rotation yet, just translation
        top_left = PVector(x,y)
        top_left + self.origin

        screen.draw.rect(top_left.x, top_left.y, w, h, color, width)


def translate(x, y):
    sm.translate(PVector(x,y))

def rotate(radians):
    sm.rotate(radians)

def push_matrix():
    sm.push_matrix()

def pop_matrix():
    sm.pop_matrix()

def line(ax, ay, bx, by, line_weight=1):
    sm.draw_line((ax, ay), (bx, by), line_weight)

def circle(x, y, r, color=(0,0,0), width=1):
    sm.draw_circle(x, y, r, color, width)

def rect(x, y, w, h, color=(0,0,0), width=1):
    sm.draw_rect(x, y, w, h, color, width)

sm = ScreenMatrix()
