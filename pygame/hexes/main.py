import math
import tuples
import transformations
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

TWO_PI = math.pi * 2
HALF_QUARTER = transformations.rotation_z(math.pi / 2)
SIXTY_DEGREES = transformations.rotation_z(TWO_PI/6)
points = []

def rotate_around_center(point, angle):
    p = transformations.translation(-WIDTH//2, -HEIGHT//2, 0) * point
    p = angle * p
    return transformations.translation(WIDTH//2, HEIGHT//2 , 0) * p

def update():
    pass

def draw():
    for p in points:
        screen.draw.circle(p.x, p.y, 10, (0,0,0))
        screen.draw.circle(p.x, p.y, 10, (0,0,0))

points.append(tuples.point(WIDTH//2 + 30, HEIGHT//2, 0))
for i in range(5):
    points.append(rotate_around_center(points[i], SIXTY_DEGREES))

run()


# vertices in a hexagon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vX = radius * cos(angle)
#         vY = radius * sin(angle)
