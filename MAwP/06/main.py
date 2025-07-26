"""Chapter 6 - Creating Oscillations with Trigonometry."""
from math import radians, cos, sin
from engine import run
from screen_matrix import push_matrix, translate, pop_matrix, polygon

WIDTH = 600
HEIGHT = 600
TITLE = "Trigonometry"


def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    # TO_DO: Maybe. Depends if we want to closely emulate Processing.
    #        The model there is to use beginShape, vertex and endShape.
    vertices = []
    for i in range(6):
        vertices.append((100 * cos(radians(60 * i)),
                         100 * sin(radians(60 * i))))
    polygon(vertices)
    pop_matrix()


run()
