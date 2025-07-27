"""Chapter 6 - Creating Oscillations with Trigonometry."""
from math import radians, cos, sin
from engine import run
from screen_matrix import push_matrix, translate, pop_matrix
from screen_matrix import polygon, circle, line
# pylint: disable=C0103, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Trigonometry"

R1 = 300 # radius of big circle
R2 = 105 # radius of small circles
R3 = 5   # radius of drawing dot
PROP = 0.8

x1, y1 = 0, 0

t = 0
points = []

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
    global t, points

    #push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    #poly(3,100)
    #pop_matrix()

    #push_matrix()
#
    #translate(WIDTH/4, HEIGHT/2)
    #circle(0,0,R1)
#
    #x = R1 * cos(t)
    #y = R1 * sin(t)
    #circle_list = [y] + circle_list[:249]
#
    #line(x, y, 200, y)
    #circle(200, y, R2, (0,255,0), 0)
    #circle(x, y, R2, (255,0,0), 0)
#
    #for i,c in enumerate(circle_list):
        #circle(200+i, c, 4, (0,255,0), 0)
#
    #pop_matrix()
#

    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    circle(x1, y1, R1)

    x2 = (R1 - R2) * cos(t)
    y2 = (R1 - R2) * sin(t)
    circle(x2, y2, R2)

    x3 = x2 + PROP * (R2 - R3) * cos(-((R1-R2)/R2)*t)
    y3 = y2 + PROP * (R2 - R3) * sin(-((R1-R2)/R2)*t)

    points = [[x3,y3]] + points[:2000]
    for i,p in enumerate(points):
        if i < len(points)-1:
            line(p[0], p[1], points[i+1][0], points[i+1][1])

    circle(x3, y3, R3, (255,0,0), 0)

    pop_matrix()

    t += 0.05


run()
