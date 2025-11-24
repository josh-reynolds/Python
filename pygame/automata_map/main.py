"""Generate a map image using cellular automata.

Derived from "Cellular Automata Procedural Development"
by White Box Dev (YouTube).
"""
# Moore neighborhood
# if > 4 are wall -> wall
# if <= 4 are wall -> floor
# out of bounds coordinates are walls

# generate noise
# run an iteration
# repeat

from random import randint
from engine import screen, run

WIDTH = 800
HEIGHT = 600
TITLE = "Cellular Automata Map Generation"

CELL_SIZE = 10
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

grid = [[randint(0,1) for x in range(COLUMNS)] for y in range(ROWS)]

def update():
    global counter
    if counter % 30 == 0:
        generate()
    counter += 1

def draw():
    screen.fill((200,200,200))

    for y in range(ROWS):
        for x in range(COLUMNS):
            color = (255,0,200)
            if grid[y][x] == 0:
                color = (0,0,0)

            screen.draw.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color, 0)
            #screen.draw.text(f"{x},{y}", center=(x * CELL_SIZE + CELL_SIZE/2,
                                                 #y * CELL_SIZE + CELL_SIZE/2), 
                             #color=(255,255,255))

def generate():
    #print(f"generating iteration {counter}")
    temp_grid = [row[:] for row in grid]
    for j in range(ROWS):
        for k in range(COLUMNS):
            neighbor_wall_count = count_neighbors(j,k,temp_grid)
            #print(f"{k},{j} state = {temp_grid[j][k]} neighbors = {neighbor_wall_count}")
            if neighbor_wall_count > 4:
                grid[j][k] = 0
            else:
                grid[j][k] = 1

def count_neighbors(row, column, temp_grid):
    #print(f"Counting neighbors for {column},{row}")
    count = 0
    for y in range(row-1, row+2):
        for x in range(column-1, column+2):
            if in_bounds(x,y):
                #print(f"{x},{y} == {temp_grid[y][x]}")
                if y != row or x != column:
                    if temp_grid[y][x] == 0:
                        count += 1
                        #print(f"{x},{y} plus!")
            else:
                #print(f"{x},{y} out of bounds")
                count += 1
                #print(f"{x},{y} plus!")
            #print(f"{count}")
    return count

def in_bounds(x,y):
    return x >= 0 and y >= 0 and x < COLUMNS and y < ROWS

counter = 1

run()
