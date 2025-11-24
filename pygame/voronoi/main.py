"""Fill a canvas with Voronoi cells."""
from random import randint
from engine import screen, run

WIDTH = 600
HEIGHT = 800
TITLE = "Voronoi Cells"

CELL_SIZE = 100
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

points = []

def update():
    pass

def draw():
    screen.fill((200,200,200))

    counter = 0
    for y in range(ROWS):
        for x in range(COLUMNS):
            screen.draw.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, (255,0,0), 1)
            screen.draw.text(f"{counter}", center=(x * CELL_SIZE + CELL_SIZE//2,
                                              y * CELL_SIZE + CELL_SIZE//2))
            counter += 1

    for p in points:
        screen.draw.circle(p[0], p[1], 4, (0,0,255))

    for i,p in enumerate(points):
        if p in top:
            top_neighbor = (p[0], 0)
        else:
            top_neighbor = points[i - COLUMNS]

        if p in left:
            left_neighbor = (0, p[1])
        else:
            left_neighbor = points[i - 1]

        if p in right:
            right_neighbor = (WIDTH, p[1])
        else:
            right_neighbor = points[i + 1]

        if p in bottom:
            bottom_neighbor = (p[0], HEIGHT)
        else:
            bottom_neighbor = points[i + COLUMNS]

        screen.draw.line((0,0,0), p, top_neighbor)
        screen.draw.line((0,0,0), p, left_neighbor)
        screen.draw.line((0,0,0), p, right_neighbor)
        screen.draw.line((0,0,0), p, bottom_neighbor)

for y in range(ROWS):
    for x in range(COLUMNS):
        point_x = randint(x * CELL_SIZE, (x + 1) * CELL_SIZE)
        point_y = randint(y * CELL_SIZE, (y + 1) * CELL_SIZE)
        points.append((point_x, point_y))

# TOP ROW    = 0 to (COLUMNS - 1)                       = [:(COLUMNS-1)]
# BOTTOM ROW = len(points) - COLUMNS to len(points) - 1 = [len(points) - COLUMNS:]
# LEFT COLUMN = index % COLUMNS == 0
# RIGHT COLUMN = (index + 1) % COLUMNS == 0

top = [points[n] for n in range(COLUMNS)]
bottom = [points[n] for n in range(len(points) - COLUMNS, len(points))]
left  = [points[n] for n in range(len(points)) if n % COLUMNS == 0]
right = [points[n] for n in range(len(points)) if (n+1) % COLUMNS == 0]



run()
