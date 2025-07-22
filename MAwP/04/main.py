"""Display equations on a graph."""
from engine import run, screen
from screen_matrix import push_matrix, translate, sm, line, circle, pop_matrix

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
YSCL = -HEIGHT / RANGEY

def parabola(_input):
    """Parabola formula."""
    return _input**2

def cubic(_input):
    """Cubic function."""
    return 6*_input**3 + 31*_input**2 + 3*_input - 10

def quadratic(_input):
    """Quadratic function."""
    return 2*x**2 + 7*x - 15

def graph(function):
    """Draw function curve on the window surface."""
    sm.color = (255,0,0)
    x_val = XMIN
    while x_val <= XMAX:
        value = function(x_val)
        line(x_val * XSCL, value * YSCL,
             (x_val + 0.001) * XSCL, function(x_val + 0.001) * YSCL)
        if value < 0.001 and value > -0.001:
            circle(x_val * XSCL, value * YSCL, 8, (255,0,0))
        x_val += 0.001

def grid():
    """Draw a grid on the window surface."""
    sm.color = (0,255,255)
    for i in range(XMIN, XMAX + 1):
        line(i * XSCL, YMIN * YSCL, i * XSCL, YMAX * YSCL)
        line(XMIN * XSCL, i * YSCL, XMAX * XSCL, i * YSCL)

    sm.color = (0,0,0)
    line(0, YMIN * YSCL, 0, YMAX * YSCL)
    line(XMIN * XSCL, 0, XMAX * XSCL, 0)

def update():
    """Update state once per frame."""

def draw():
    """Draw on window once per frame."""
    screen.fill((255,255,255))

    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    grid()
    #graph(parabola)
    graph(cubic)
    pop_matrix()

run()
