import math
import tuples
import transformations
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Hexes"

HALF_QUARTER = transformations.rotation_z(math.pi / 2)
points = []

def rotate_around_center(point):
    p = transformations.translation(-WIDTH//2, -HEIGHT//2, 0) * point
    p = HALF_QUARTER * p
    return transformations.translation(WIDTH//2, HEIGHT//2 , 0) * p

def update():
    pass

def draw():
    for p in points:
        screen.draw.circle(p.x, p.y, 10, (0,0,0))
        screen.draw.circle(p.x, p.y, 10, (0,0,0))

points.append(tuples.point(WIDTH//2 + 30, HEIGHT//2, 0))
for i in range(3):
    points.append(rotate_around_center(points[i]))

run()
