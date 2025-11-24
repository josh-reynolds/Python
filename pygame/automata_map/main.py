"""Generate a map image using cellular automata."""
from engine import screen, run

WIDTH = 800
HEIGHT = 600
TITLE = "Cellular Automata Map Generation"

CELL_SIZE = 200
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

def update():
    pass

def draw():
    screen.fill((200,200,200))

    for x in range(COLUMNS):
        for y in range(ROWS):
            screen.draw.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, (255,0,200), 1)

run()
