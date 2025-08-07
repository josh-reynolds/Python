"""Chapter 11 - Cellular Automata."""
from engine import run, screen

WIDTH = 600
HEIGHT = 600
TITLE = "Cellular Automata"

GRID_W = 50
GRID_H = 50
CELL_SIZE = WIDTH // GRID_W

class Cell:
    """Cell class for Cellular Automata."""

    def __init__(self, column, row, state=0):
        """Create a Cell object."""
        self.column = column
        self.row = row
        self.state = state

    def display(self):
        """Draw Cell on screen."""
        if self.state == 1:
            color = (0,0,0)
        else:
            color = (255,255,255)

        screen.draw.rect(CELL_SIZE*self.row, CELL_SIZE* self.column, 
                         CELL_SIZE, CELL_SIZE, 
                         color=color, width=0)
        screen.draw.rect(CELL_SIZE*self.row, CELL_SIZE* self.column, 
                         CELL_SIZE, CELL_SIZE, 
                         color=(220,220,220), width=1)

def create_cell_list():
    """Create a list of Cells with one on Cell in the center."""
    new_list = []
    for j in range(GRID_H):
        new_list.append([])
        for i in range(GRID_W):
            new_list[j].append(Cell(i,j,0))

    new_list[GRID_H//2][GRID_W//2].state = 1
    return new_list

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    for row in cell_list:
        for cell in row:
            cell.display()

cell_list = create_cell_list()

run()
