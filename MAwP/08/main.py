"""Chapter 8 - Using Matrices for Computer Graphics."""
from engine import run
from screen_matrix import line, push_matrix, pop_matrix, translate, sm
# pylint: disable=C0103, C0200

WIDTH = 600
HEIGHT = 600
TITLE = "Matrices"

def add_matrices(a,b):
    """Add two 2x2 matrices together."""
    C = [[a[0][0] + b[0][0], a[0][1] + b[0][1]],
         [a[1][0] + b[1][0], a[1][1] + b[1][1]]]
    return C

def mult_matrices(a,b):
    """Multiply two matrices together."""
    m = len(a)
    n = len(b[0])
    new_matrix = []
    for i in range(m):
        row = []
        for j in range(n):
            sum1 = 0
            for k in range(len(b)):
                sum1 += a[i][k] * b[k][j]
            row.append(sum1)
        new_matrix.append(row)
    return new_matrix

def grid():
    """Draw a grid for graphing."""
    sm.color = (0,255,255)
    for i in range(xmin,xmax+1):
        line(i*xscl, ymin*yscl, i*xscl, ymax*yscl)
    for i in range(ymin,ymax+1):
        line(xmin*xscl, i*yscl, xmax*xscl, i*yscl)

    sm.color = (0,0,0)
    line(0, ymin*yscl, 0, ymax*yscl)
    line(xmin*xscl, 0, xmax*xscl, 0)


def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    grid()
    pop_matrix()

xmin = -10
xmax = 10

ymin = -10
ymax = 10

rangex = xmax - xmin
rangey = ymax - ymin

xscl = WIDTH/rangex
yscl = HEIGHT/rangey

run()
