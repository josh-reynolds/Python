import math
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

class Grid:
    def __init__(self, hexRadius, top_border, left_border, columns, rows, color, width=1):
        self.hexRadius = hexRadius
        self.left_border = left_border
        self.top_border = top_border
        self.columns = columns
        self.rows = rows
        self.color = color
        self.width = width
        self.yOffset = math.sqrt((hexRadius * hexRadius) - (hexRadius/2 * hexRadius/2))
        self.startX = hexRadius + left_border
        self.startY = int(self.yOffset) + top_border

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
            screen.draw.hex(h[0], h[1], self.hexRadius, self.color, self.width)

def update():
    pass

def draw():
    g1.draw()
    g2.draw()

g1 = Grid(10, 8, 8, 25, 22, (0,0,0))
g2 = Grid(50, 8, 17, 5, 4, (0,0,255), 2)

run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
