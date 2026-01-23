"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
import os.path
import pygame
from random import randint
from engine import screen, run
from screen_matrix import push_matrix, pop_matrix, line, rotate, translate
from screen_matrix import equilateral_triangle

WIDTH = 1100
HEIGHT = 850
TITLE = "How to Host a Dungeon"

GROUND_LEVEL = HEIGHT // 5

SKY = (36, 87, 192)
GROUND = (81, 76, 34)

location = None
angle = 0

def get_random_underground_location():
    return (randint(0,WIDTH), randint(GROUND_LEVEL,HEIGHT))

def mithral():
    global location, angle
    # [DONE] find a random spot underground
    # [DONE] draw a triangle 
    # ...pointing to nearest corner of map
    # label as mithral ore
    # repeat once

    if not location:
        location = get_random_underground_location()

    push_matrix()
    translate(location[0], location[1])
    rotate(angle)
    equilateral_triangle(HEIGHT//10)
    pop_matrix()

def update():
    pass

def draw():
    global angle

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)
    screen.draw.line((0,0,0), (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    # Primordial Age events
    mithral()
    angle += 0.01

run()
