from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Perlin Noise"

grid_w = 20
grid_h = 20
cell_w = WIDTH // grid_w
cell_h = HEIGHT // grid_h

def update():
    pass

def draw():
    for i in range(grid_w):
        for j in range(grid_h):
            screen.draw.rect((i * cell_w, j * cell_h, cell_w, cell_h), (128,128,128), 0)
            screen.draw.rect((i * cell_w, j * cell_h, cell_w, cell_h), (0,0,0), 1)



run()
