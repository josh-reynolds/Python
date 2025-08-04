"""Chapter 10 - Creating Fractals Using Recursion."""
from math import radians
from engine import run
from screen_matrix import push_matrix, pop_matrix, line, translate, rotate

WIDTH = 600
HEIGHT = 600
TITLE = "Fractals & Recursion"

def tree_fork(size, level):
    """Draw a fork consisting of a trunk and two branches."""
    if level > 0:
        line(0,0,0,-size)
        translate(0, -size)
        rotate(radians(30))
        
        tree_fork(0.8*size, level-1)
        rotate(radians(-60))

        tree_fork(0.8*size, level-1)
        rotate(radians(30))

        translate(0, size)

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    push_matrix()
    translate(300,500)
    tree_fork(100,5)
    pop_matrix()

run()
