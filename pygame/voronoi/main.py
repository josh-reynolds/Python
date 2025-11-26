"""Fill a canvas with Voronoi cells."""
from math import inf
from random import randint
from engine import screen, run

# Three approaches to generating Voronoi cells:
# - Delaunay triangulation
# - Fortune's algorithm (sweep line)
# - perpendicular bisectors

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

        # we keep redrawing lines between neighbors, could
        # probably just draw up and left (and then handle
        # right & bottom edges specially...)

        draw_lines(p, top_neighbor)
        draw_lines(p, left_neighbor)
        #draw_lines(p, right_neighbor)
        #draw_lines(p, bottom_neighbor)

def draw_lines(p, neighbor):
    screen.draw.line((0,0,0), p, neighbor)
    midpoint = find_midpoint(p, neighbor)
    screen.draw.circle(midpoint[0], midpoint[1], 3, (255,0,255))
    slope = find_slope(p, neighbor)
    perpendicular = find_perp_slope(slope)
    intercept = midpoint[1] - (perpendicular * midpoint[0])

def find_midpoint(p1, p2):
    return (int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2))

def find_slope(p1, p2):
    if p1[0] != p2[0]:
        return (p2[1] - p1[1])/(p2[0] - p1[0])
    return inf

def find_perp_slope(slope):
    if slope != 0:
        return -1/slope
    return inf

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
