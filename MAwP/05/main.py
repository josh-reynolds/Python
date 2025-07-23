"""Chapter 5 - Transforming Shapes with Geometry."""
from engine import run
from screen_matrix import rect, translate, push_matrix, pop_matrix

WIDTH = 600
HEIGHT = 600
TITLE = "Geometry"

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    rect(50,100,100,60)
    pop_matrix()

run()
