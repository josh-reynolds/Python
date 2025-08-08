"""Chapter 11 - Cellular Automata."""
from engine import run, screen, keyboard
# pylint: disable=C0103, E1121, W0603, E1101

WIDTH = 600
HEIGHT = 600
TITLE = "Cellular Automata"

GRID_W = 50
GRID_H = 50
CELL_SIZE = WIDTH // GRID_W

generation = 0
key_down = False

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
                         color, 0)
        screen.draw.rect(CELL_SIZE*self.row, CELL_SIZE* self.column,
                         CELL_SIZE, CELL_SIZE,
                         (220,220,220), 1)

    def check_neighbors(self):
        """Examine states of neighbor cells."""
        if self.state == 1:
            return 1
        neighbors = 0
        for dr,dc in [[-1,0],[1,0],[0,-1],[0,1]]:
            try:
                if cell_list[self.row + dr][self.column + dc].state == 1:
                    neighbors += 1
            except IndexError:
                continue
        if neighbors in [1,4]:
            return 1
        return 0

def create_cell_list():
    """Create a list of Cells with one on Cell in the center."""
    new_list = []
    for j in range(GRID_H):
        new_list.append([])
        for i in range(GRID_W):
            new_list[j].append(Cell(i,j,0))

    new_list[GRID_H//2][GRID_W//2].state = 1
    return new_list

def update_cell_list(c_list):
    """Create next generation of a CA using a double-buffer."""
    new_list = []
    for r,row in enumerate(c_list):
        new_list.append([])
        for c,cell in enumerate(row):
            new_list[r].append(Cell(c,r,cell.check_neighbors()))
    return new_list[::]

def update():
    """Update the app state once per frame."""
    global key_down, cell_list, generation
    if keyboard.up and not key_down:
        cell_list = update_cell_list(cell_list)
        generation += 1
    key_down = keyboard.up

def draw():
    """Draw to the window once per frame."""
    for row in cell_list:
        for cell in row:
            cell.display()
    screen.draw.text("Press up-arrow to increase generation.", pos=(20,20),
                     color=(0,0,255))
    screen.draw.text(f"Generation: {generation}", pos=(460,20),
                     color=(255,0,0))
    #if generation == 3:
        #no_loop()       # TO_DO: don't have this functionality yet
                         #        in the engine

cell_list = create_cell_list()

run()
