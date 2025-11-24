"""Fill a canvas with Voronoi cells."""
from random import randint
from engine import screen, run

WIDTH = 600
HEIGHT = 800
TITLE = "Voronoi Cells"

CELL_SIZE = 200
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

points = []

def update():
    pass

def draw():
    screen.fill((200,200,200))

    for x in range(COLUMNS):
        for y in range(ROWS):
            screen.draw.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, (255,0,0), 1)

    for p in points:
        screen.draw.circle(p[0], p[1], 4, (0,0,255))


for x in range(COLUMNS):
    for y in range(ROWS):
        point_x = randint(x * CELL_SIZE, (x + 1) * CELL_SIZE)
        point_y = randint(y * CELL_SIZE, (y + 1) * CELL_SIZE)
        points.append((point_x, point_y))

run()
