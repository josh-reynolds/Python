"""Chapter 11 - Cellular Automata."""
from engine import run, screen

WIDTH = 600
HEIGHT = 600
TITLE = "Cellular Automata"

GRID_W = 15
GRID_H = 15
CELL_SIZE = 18

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    for x in range(GRID_W):
        for y in range(GRID_H):
            screen.draw.rect(CELL_SIZE*x, CELL_SIZE* y, 
                             CELL_SIZE, CELL_SIZE, 
                             color=(0,0,0), width=1)

run()
