"""Chapter 6 - Creating Oscillations with Trigonometry."""
from math import radians, cos, sin
from engine import run
from screen_matrix import push_matrix, translate, pop_matrix, polygon, circle, line

WIDTH = 600
HEIGHT = 600
TITLE = "Trigonometry"

R1 = 100 # radius of big circle
R2 = 10  # radius of small circle
t = 0

def poly(sides, sz):
    """Draw a polygon of arbitrary size and number of sides."""
    # TO_DO: Maybe. Depends if we want to closely emulate Processing.
    #        The model there is to use beginShape, vertex and endShape.
    vertices = []
    step = radians(360/sides)
    for i in range(sides):
        vertices.append((sz * cos(step * i),
                         sz * sin(step * i)))
    polygon(vertices)

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    global t

    #push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    #poly(3,100)
    #pop_matrix()

    push_matrix()

    translate(WIDTH/4, HEIGHT/2)
    circle(0,0,R1)

    x = R1 * cos(t)
    y = R1 * sin(t)

    line(x,y,200,y)
    circle(200,y,R2,(0,255,0),0)
    circle(x,y,R2,(255,0,0),0)

    pop_matrix()

    t += 0.05


run()
