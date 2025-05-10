import math
import os.path
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"


class Hex:
    def __init__(self, screen_coordinate, radius, color, width):
        self.x, self.y = screen_coordinate
        self.radius = radius
        self.color = color
        self.width = width

    def draw(self):
        screen.draw.hex(self.x, self.y, self.radius, self.color, self.width)

class Grid:
    def __init__(self, hexRadius, top_border, left_border, columns, rows, color, width=1):
        self.hexRadius = hexRadius
        self.yOffset = math.sqrt((hexRadius * hexRadius) - (hexRadius/2 * hexRadius/2))

        self.startX = hexRadius + left_border
        self.startY = int(self.yOffset) + top_border

        self.left_border = left_border
        self.top_border = top_border
        self.columns = columns
        self.rows = rows

        self.hexes = []
        for i in range(columns):
            for j in range(rows):
                self.hexes.append(Hex(self.hex_coordinate_to_screen(i,j), hexRadius, color, width))

    def hex_coordinate_to_screen(self, column, row):
        x = self.startX + column * self.hexRadius * 1.5
        columnAdjust = 0 if column % 2 == 0 else self.yOffset
        y = self.startY + self.yOffset * row * 2 + columnAdjust
        return (x,y)

    def draw(self):
        for h in self.hexes:
            h.draw()

def update():
    pass

def draw():
    g1.draw()
    #g2.draw()
    #g3.draw()

    try:
        filename = "./output.png"
        if not os.path.isfile(filename):
            pygame.image.save(screen.surface, filename)
    except Exception as e:
        print(e)

g1 = Grid(10, 8, 8, 25, 22, (0,0,0))
g2 = Grid(40, 16, 8, 6, 5, (0,0,255), 2)
g3 = Grid(50, 16, 12, 5, 4, (255,0,0), 2)


run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
