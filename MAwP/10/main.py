"""Chapter 10 - Creating Fractals Using Recursion."""
from math import radians
import pygame
from engine import run, remap
from screen_matrix import push_matrix, pop_matrix, line, translate, rotate

WIDTH = 600
HEIGHT = 600
TITLE = "Fractals & Recursion"

def tree_fork(size, level):
    """Draw a fork consisting of a trunk and two branches."""
    _, mouse_y = pygame.mouse.get_pos()
    angle = remap(mouse_y, 0, HEIGHT, 0, 180)

    if level > 0:
        line(0,0,0,-size)
        translate(0, -size)
        rotate(radians(angle))
        
        tree_fork(0.8*size, level-1)
        rotate(radians(-2*angle))

        tree_fork(0.8*size, level-1)
        rotate(radians(angle))

        translate(0, size)

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    mouse_x, _ = pygame.mouse.get_pos()
    level = int(remap(mouse_x, 0, WIDTH, 0, 15))
    push_matrix()
    translate(300,500)
    tree_fork(100,level)
    pop_matrix()

run()
