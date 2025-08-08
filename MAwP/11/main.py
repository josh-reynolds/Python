"""Chapter 11 - Cellular Automata."""
from engine import run
from screen_matrix import rect
# pylint: disable=C0103

WIDTH = 600
HEIGHT = 600
TITLE = "Cellular Automata"

w = 50
rows = 1
cols = 11

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    for i, cell in enumerate(cells):
        for j, v in enumerate(cell):
            color = (0,0,0) if v == 1 else (255,255,255)
            rect(j*w-(cols*w-WIDTH)/2, w*i, w, w, color, 0)
            rect(j*w-(cols*w-WIDTH)/2, w*i, w, w, (0,0,0), 1)

cells = []
for r in range(rows):
    cells.append([])
    for c in range(cols):
        cells[r].append(0)
cells[0][cols//2] = 1

run()
