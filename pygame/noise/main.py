from random import randint
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Perlin Noise"

OUTLINE = (0,0,0)

grid_w = 100
grid_h = 100
cell_w = WIDTH // grid_w
cell_h = HEIGHT // grid_h

# ---------------------------------------
scale = 0.03
gradients = [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]
random_values = [[randint(0,7) for i in range(grid_w)] for i in range(grid_h)]
cells = [[0 for i in range(grid_w)] for j in range(grid_h)]

min_val = 0
max_val = 0

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

for i in range(grid_w):
    for j in range(grid_h):
        x = i * scale
        y = j * scale

        # grid corners
        x1, y1 = int(x), int(y)
        x2, y2 = x1 + 1, y1 + 1

        # distance vectors
        dA, dB, dC, dD = (x1 - x, y1 - y), \
                         (x1 - x, y2 - y), \
                         (x2 - x, y1 - y), \
                         (x2 - x, y2 - y)

        # gradient vectors
        gA, gB, gC, gD = gradients[random_values[x1][y1]], \
                         gradients[random_values[x1][y2]], \
                         gradients[random_values[x2][y1]], \
                         gradients[random_values[x2][y2]]

        # dot products
        dotA, dotB, dotC, dotD = (dA[0] * gA[0] + dA[1] * gA[1]), \
                                 (dB[0] * gB[0] + dB[1] * gB[1]), \
                                 (dC[0] * gC[0] + dC[1] * gC[1]), \
                                 (dD[0] * gD[0] + dD[1] * gD[1])

        # fade values
        u, v = fade(x - x1), fade(y - y1)
        
        # interpolation
        tmp1 = u * dotC + (1 - u) * dotA
        tmp2 = u * dotD + (1 - u) * dotB
        pixel_value = v * tmp2 + (1 - v) * tmp1

        color_value = int(pixel_value * 255)

        if color_value < min_val:
            min_val = color_value
        if color_value > max_val:
            max_val = color_value

        color_value = (color_value + 255) // 2
        color_value = min(max(color_value, 0), 255)
        color = (color_value, color_value, color_value)
        cells[j][i] = color

print(min_val, max_val)

# ---------------------------------------
#def random_grayscale():
   #value = randint(0,255)
   #return (value, value, value)

#cells = [[random_grayscale() for i in range(grid_w)] for i in range(grid_h)]

# ---------------------------------------
def update():
    pass

def draw():
    for i in range(grid_w):
        for j in range(grid_h):
            cell_rect = (i * cell_w, j * cell_h, cell_w, cell_h)

            screen.draw.rect(cell_rect, cells[j][i], 0)
            screen.draw.rect(cell_rect, OUTLINE, 1)

run()
