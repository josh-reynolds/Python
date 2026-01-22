"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
import os.path
import pygame
from engine import screen, run
from screen_matrix import push_matrix, pop_matrix, line, rotate, translate

WIDTH = 1100
HEIGHT = 850
TITLE = "How to Host a Dungeon"

GROUND_LEVEL = HEIGHT // 5

SKY = (36, 87, 192)
GROUND = (81, 76, 34)

def update():
    pass

def draw():
    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

run()
