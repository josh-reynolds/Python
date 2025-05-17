from pygame import Rect
from engine import *

class Liquid:
    def __init__(self, x, y, w, h, c):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c
        self.rect = Rect(x, y, w, h)

    def draw(self):
        screen.draw.rect(self.rect, (0,0,200,128), 0)
