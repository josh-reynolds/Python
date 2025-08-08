"""Chapter 11 - Cellular Automata."""
from engine import run
from screen_matrix import rect
# pylint: disable=C0103

WIDTH = 600
HEIGHT = 600
TITLE = "Cellular Automata"

w = 3
rows = 500
cols = 500

def rules(a,b,c):
    """Evaluate CA ruleset."""
    return ruleset[7 - (4*a + 2*b + c)]

def generate():
    """Create next row in CA."""
    for i, row in enumerate(cells):
        for j in range(1, len(row)-1):
            left = row[j-1]
            me = row[j]
            right = row[j+1]
            if i < len(cells) - 1:
                cells[i+1][j] = rules(left, me, right)
    return cells

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    for i, cell in enumerate(cells):
        for j, v in enumerate(cell):
            color = (0,0,0) if v == 1 else (255,255,255)
            rect(j*w-(cols*w-WIDTH)/2, w*i, w, w, color, 0)

ruleset = [0,1,0,1,1,0,1,0]
cells = []
for r in range(rows):
    cells.append([])
    for c in range(cols):
        cells[r].append(0)
cells[0][cols//2] = 1
cells = generate()

run()
