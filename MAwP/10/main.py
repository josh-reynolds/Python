"""Chapter 10 - Creating Fractals Using Recursion."""
from math import radians, sqrt, pi
import pygame
from engine import run, remap, keyboard
from screen_matrix import push_matrix, pop_matrix, line, rect
from screen_matrix import translate, rotate, triangle, sm
## pylint: disable=W0603,E1101,C0103

WIDTH = 600
HEIGHT = 600
TITLE = "Fractals & Recursion"

RED = (255,0,0)
BLACK = (0,0,0)
PURPLE = (150,0,150)

dragon_level = 8
dragon_size = 40
key_down = False

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
                 color=BLACK, width=0)
    else:
        for _ in range(3):
            sierpinski(size/2.0, level-1)
            translate(size/2.0, -size*sqrt(3)/2.0)
            rotate(radians(120))

def square_fractal(size, level):
    """Draw a square fractal."""
    if level == 0:
        rect(0, 0, size, size,
             color=PURPLE, width=0)
    else:
        push_matrix()
        square_fractal(size/2.0, level-1)
        translate(size/2.0, 0)
        square_fractal(size/2.0, level-1)
        translate(-size/2.0, size/2.0)
        square_fractal(size/2.0, level-1)
        pop_matrix()

def left_dragon(size, level, color=BLACK):
    """Draw the left half of a dragon curve fractal."""
    if level == 0:
        sm.color = color
        line(0,0,size,0)
        translate(size,0)
    else:
        left_dragon(size, level-1, color=color)
        rotate(radians(-90))
        right_dragon(size, level-1, color=color)

def right_dragon(size, level, color=BLACK):
    """Draw the right half of a dragon curve fractal."""
    if level == 0:
        sm.color = color
        line(0,0,size,0)
        translate(size,0)
    else:
        left_dragon(size, level-1, color=color)
        rotate(radians(90))
        right_dragon(size, level-1, color=color)

def update():
    """Update the app state once per frame."""
    global key_down, dragon_size, dragon_level
    if keyboard.left and not key_down:
        dragon_size -= 5
        print(f"dragon size = {dragon_size}")
    elif keyboard.right and not key_down:
        dragon_size += 5
        print(f"dragon size = {dragon_size}")
    elif keyboard.up and not key_down:
        dragon_level += 1
        print(f"dragon level = {dragon_level}")
    elif keyboard.down and not key_down:
        dragon_level -= 1
        print(f"dragon level = {dragon_level}")
    key_down = (keyboard.left or keyboard.right or
                keyboard.up or keyboard.down)

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
    #push_matrix()
    #translate(50, 450)
    #sierpinski(400, 8)
    #pop_matrix()

    ## Square Fractal ==================
    #push_matrix()
    #translate(50, 50)
    #square_fractal(500, 8)
    #pop_matrix()

    ## Dragon Curve ===================
    mouse_x, _ = pygame.mouse.get_pos()
    angle = remap(mouse_x, 0, WIDTH, 0, pi*2)
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    push_matrix()
    left_dragon(dragon_size, dragon_level, color=RED)
    pop_matrix()
    left_dragon(dragon_size, dragon_level-1, color=RED)
    rotate(angle)
    right_dragon(dragon_size, dragon_level-1)
    pop_matrix()

run()
