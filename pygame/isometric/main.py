"""Draw an isometric grid."""
import math
import os.path
import pygame
from engine import screen, run
from screen_matrix import push_matrix, pop_matrix, line, rotate, translate

WIDTH = 425
HEIGHT = 560
TITLE = "Isometric Grid"

ROW_SPACING = HEIGHT//10

def update():
    pass

def draw():
    for i in range(0, int(HEIGHT * 2.5), ROW_SPACING):
        push_matrix()
        translate(0, i)
        rotate(math.radians(-60))
        line(0, 0, WIDTH * 2, 0, 1)
        pop_matrix()

    for j in range(-HEIGHT * 2, HEIGHT, ROW_SPACING):
        push_matrix()
        translate(0, j)
        rotate(math.radians(60))
        line(0, 0, WIDTH * 2, 0, 1)
        pop_matrix()

    for k in range(0, HEIGHT, ROW_SPACING//2):
        push_matrix()
        translate(0, k)
        line(0, 0, WIDTH * 2, 0, 1)
        pop_matrix()

    try:
        filename = "./output.png"
        if not os.path.isfile(filename):
            pygame.image.save(screen.surface, filename)
    except Exception as e:
        print(e)

run()
