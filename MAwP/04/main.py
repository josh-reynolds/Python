"""Display equations on a graph."""
from math import sin
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

def parabola(input_):
    """Parabola formula."""
    return input_**2

def cubic(input_):
    """Cubic function."""
    return 6*input_**3 + 31*input_**2 + 3*input_ - 10

def quadratic(input_):
    """Quadratic function."""
    return 2*input_**2 + 7*input_ - 15

def sine(input_):
    """Sine function."""
    return sin(input_)

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
    #graph(cubic)
    #graph(quadratic)
    graph(sine)
    pop_matrix()

run()
