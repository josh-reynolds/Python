from engine import *
from pvector import PVector

class Test:
    def __init__(self, x, y):
        self.points = []
        start = PVector(100,0)
        for i in range(350, 400, 10):
            new_point = start.copy()
            new_point.rotate(i)
            self.points.append(new_point)
        self.center = PVector(x,y)

    def draw(self):
        for p in self.points:
            translate = PVector.add(p, self.center)
            screen.draw.circle(translate.x, translate.y, 8, (255,0,0))
        screen.draw.circle(self.center.x, self.center.y, 100, (0,0,0), 1)
