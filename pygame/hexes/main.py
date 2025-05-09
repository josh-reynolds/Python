import math
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

TWO_PI = math.pi * 2

def hexagon_points(radius, center_x, center_y):
    hex_points = []
    for i in range(6):
        angle = TWO_PI/6 * (i+1)
        vX = radius * math.cos(angle) + center_x
        vY = radius * math.sin(angle) + center_y
        hex_points.append((vX,vY))
    return hex_points

def update():
    pass

def draw():
    pygame.draw.polygon(screen.surface, (0,0,0), hexagon_points(20, 100, 100), 1)

run()


# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
