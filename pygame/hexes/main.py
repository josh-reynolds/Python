import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

def update():
    pass

def draw():
    screen.draw.hex(200, 200, 25, (0,0,0), 0)
    screen.draw.hex(100, 180, 12, (255,0,0), 0)
    screen.draw.hex(300, 280, 32, (255,0,255))

run()


# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
