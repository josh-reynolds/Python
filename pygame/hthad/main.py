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
MITHRIL = (255,255,255)
BORDER = (0,0,0)

locations = []

def get_random_underground_location():
    return (randint(0,WIDTH), randint(GROUND_LEVEL,HEIGHT))

class Mithril():
    def __init__(self):
        self.x, self.y = get_random_underground_location()
        self.radius = HEIGHT//10
        self.angle = 0

    def draw(self):
        push_matrix()
        translate(self.x, self.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
        equilateral_triangle(self.radius, BORDER, 2)
        pop_matrix()

def update():
    pass

def draw():
    global angle

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    for location in locations:
        location.draw()

# Primordial Age events
locations.append(Mithril())
locations.append(Mithril())

run()
