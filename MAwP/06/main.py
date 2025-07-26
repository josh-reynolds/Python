"""Chapter 6 - Creating Oscillations with Trigonometry."""
from math import radians, cos, sin
from engine import run
from screen_matrix import push_matrix, translate, pop_matrix, polygon

WIDTH = 600
HEIGHT = 600
TITLE = "Trigonometry"

def poly(sides, sz):
    """Draw a polygon of arbitrary size and number of sides."""
    # TO_DO: Maybe. Depends if we want to closely emulate Processing.
    #        The model there is to use beginShape, vertex and endShape.
    vertices = []
    step = radians(360/sides)
    for i in range(sides):
        vertices.append((sz * cos(step * i),
                         sz * sin(step * i)))
    polygon(vertices)

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    poly(3,100)
    pop_matrix()


run()
