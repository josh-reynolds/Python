import math
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

hexRadius = 30
border = 8
yOffset = math.sqrt((hexRadius * hexRadius) - (hexRadius/2 * hexRadius/2))
startX = hexRadius + border
startY = int(yOffset) + border

def hex_coordinate_to_screen(column, row):
    #x = startX + (column - 1) * hexRadius * 1.5
    #columnAdjust = 0 if (column - 1) % 2 == 0 else yOffset
    #y = startY + (yOffset * (row - 1) * 2) + colunnAdjust

    x = startX + column * hexRadius * 1.5
    columnAdjust = 0 if column % 2 == 0 else yOffset
    y = startY + yOffset * row * 2 + columnAdjust
    return (x,y)

hexes = []
for i in range(7):
    for j in range(8):
        hexes.append(hex_coordinate_to_screen(j,i))

def update():
    pass

def draw():
    for h in hexes:
        screen.draw.hex(h[0], h[1], hexRadius, (0,0,0))

run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
