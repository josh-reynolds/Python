"""Chapter 6 - Creating Oscillations with Trigonometry."""
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
    polygon(((100,100), (100,200), (200,200), (200,100), (150,50)))
    pop_matrix()


run()
