"""Chapter 5 - Transforming Shapes with Geometry."""
from math import radians
from engine import run
from screen_matrix import circle, translate, rotate, push_matrix, pop_matrix

WIDTH = 600
HEIGHT = 600
TITLE = "Geometry"

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    for i in range(12):
        circle(200,0,25)
        rotate(radians(360/12))
    pop_matrix()

run()
