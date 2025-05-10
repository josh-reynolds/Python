import math
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

BORDER = 8

class Grid:
    def __init__(self, hexRadius, columns, rows, color):
        self.hexRadius = hexRadius
        self.columns = columns
        self.rows = rows
        self.color = color
        self.yOffset = math.sqrt((hexRadius * hexRadius) - (hexRadius/2 * hexRadius/2))
        self.startX = hexRadius + BORDER
        self.startY = int(self.yOffset) + BORDER

        self.hexes = []
        for i in range(columns):
            for j in range(rows):
                self.hexes.append(self.hex_coordinate_to_screen(i,j))

    def hex_coordinate_to_screen(self, column, row):
        x = self.startX + column * self.hexRadius * 1.5
        columnAdjust = 0 if column % 2 == 0 else self.yOffset
        y = self.startY + self.yOffset * row * 2 + columnAdjust
        return (x,y)

    def draw(self):
        for h in self.hexes:
            screen.draw.hex(h[0], h[1], self.hexRadius, self.color)

def update():
    pass

def draw():
    g.draw()

g = Grid(10, 25, 22, (0,0,0))

run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
