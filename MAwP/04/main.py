"""Display equations on a graph."""
from engine import run, screen
from screen_matrix import push_matrix, translate, sm, line, pop_matrix

WIDTH = 600
HEIGHT = 600
TITLE = "Graphing Equations"

XMIN = -10
XMAX = 10

YMIN = -10
YMAX = 10

RANGEX = XMAX - XMIN
RANGEY = YMAX - YMIN

XSCL = WIDTH / RANGEX
YSCL = HEIGHT / RANGEY


def update():
    """Update state once per frame."""

def draw():
    """Draw on window once per frame."""
    screen.fill((255,255,255))

    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    sm.color = (0,255,255)
    for i in range(XMIN, XMAX + 1):
        line(i * XSCL, YMIN * YSCL, i * XSCL, YMAX * YSCL)
        line(XMIN * XSCL, i * YSCL, XMAX * XSCL, i * YSCL)
    pop_matrix()

run()
