from random import randint
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Perlin Noise"

OUTLINE = (0,0,0)

grid_w = 40
grid_h = 20
cell_w = WIDTH // grid_w
cell_h = HEIGHT // grid_h

def random_grayscale():
    value = randint(0,255)
    return (value, value, value)

cells = [[random_grayscale() for i in range(grid_w)] for i in range(grid_h)]

def update():
    pass

def draw():
    for i in range(grid_w):
        for j in range(grid_h):
            cell_rect = (i * cell_w, j * cell_h, cell_w, cell_h)

            screen.draw.rect(cell_rect, cells[j][i], 0)
            screen.draw.rect(cell_rect, OUTLINE, 1)



run()
