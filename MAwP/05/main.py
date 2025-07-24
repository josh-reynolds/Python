"""Chapter 5 - Transforming Shapes with Geometry."""
from math import radians
from engine import run
from screen_matrix import push_matrix, translate, rotate, rect, pop_matrix

WIDTH = 600
HEIGHT = 600
TITLE = "Geometry"

time = 0

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    global time
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    rotate(radians(time))
    for i in range(12):
        rect(200,0,50,50)
        rotate(radians(360/12))
    pop_matrix()
    time += 1

run()
