"""Chapter 10 - Creating Fractals Using Recursion."""
from math import radians, sqrt
import pygame
from engine import run, remap
from screen_matrix import push_matrix, pop_matrix, line
from screen_matrix import translate, rotate, triangle

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

def snowflake(size, level):
    """Draw a Koch snowflake."""
    for _ in range(3):
        segment(size, level)
        rotate(radians(120))

def segment(size, level):
    """Draw one segment of the side of a Koch snowflake."""
    if level == 0:
        line(0,0,size,0)
        translate(size, 0)
    else:
        segment(size/3.0, level-1)
        rotate(radians(-60))

        segment(size/3.0, level-1)
        rotate(radians(120))

        segment(size/3.0, level-1)
        rotate(radians(-60))

        segment(size/3.0, level-1)

def sierpinski(size, level):
    """Draw a Sierpinski triangle."""
    if level == 0:
        triangle(0, 0, size, 0, size/2.0, -size*sqrt(3)/2.0,
                 color=(0,0,0), width=0)

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    ## Fractal Tree ====================
    #mouse_x, _ = pygame.mouse.get_pos()
    #level = int(remap(mouse_x, 0, WIDTH, 0, 15))
    #push_matrix()
    #translate(300,500)
    #tree_fork(100,level)
    #pop_matrix()

    ## Koch Snowflake ==================
    #mouse_x, _ = pygame.mouse.get_pos()
    #level = int(remap(mouse_x, 0, WIDTH, 0, 7))
    #push_matrix()
    #translate(100, 200)
    #snowflake(400, level)
    #pop_matrix()

    ## Sierpinski Triangle =============
    push_matrix()
    translate(50, 450)
    sierpinski(400, 0)
    pop_matrix()


run()
