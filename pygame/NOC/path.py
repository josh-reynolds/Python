import pygame
from engine import *

class Path:
    def __init__(self):
        self.radius = 20
        self.points = []

    def add_point(self, x, y):
        self.points.append((x,y))

    def draw(self):
        # TO_DO: add draw.lines to Painter
        if len(self.points) > 1:
            pygame.draw.lines(screen.surface, (128,128,128), False, self.points, self.radius)
            pygame.draw.lines(screen.surface, (0,0,0), False, self.points)
