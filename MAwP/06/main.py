"""Chapter 6 - Creating Oscillations with Trigonometry."""
from math import radians, cos, sin, pi, e
from engine import run
from screen_matrix import push_matrix, translate, pop_matrix
from screen_matrix import polygon, circle, line, sm
# pylint: disable=C0103, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Trigonometry"

R1 = 300 # radius of big circle
R2 = 105 # radius of small circles
R3 = 5   # radius of drawing dot
PROP = 0.8

x1, y1 = 0, 0

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

def harmonograph(t):
    """Return a point on a harmonograph given a time value."""
    a1=a2=a3=a4 = 100                 # amplitude
    f1,f2,f3,f4 = 2.01,3,3,2          # frequency
    p1,p2,p3,p4 = -pi/2,0,-pi/16,0    # phase shift
    d1,d2,d3,d4 = 0.00085,0.0065,0,0  # decay
    x = (a1 * cos(f1 * t + p1) * e**(-d1 * t) + 
         a3 * cos(f3 * t + p3) * e**(-d3 * t))
    y = (a2 * sin(f2 * t + p2) * e**(-d2 * t) +
         a4 * sin(f4 * t + p4) * e**(-d4 * t))
    return [x,y]

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
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

    #push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    #circle(x1, y1, R1)
#
    #x2 = (R1 - R2) * cos(t)
    #y2 = (R1 - R2) * sin(t)
    #circle(x2, y2, R2)
#
    #x3 = x2 + PROP * (R2 - R3) * cos(-((R1-R2)/R2)*t)
    #y3 = y2 + PROP * (R2 - R3) * sin(-((R1-R2)/R2)*t)
#
    #points = [[x3,y3]] + points[:2000]
    #for i,p in enumerate(points):
        #if i < len(points)-1:
            #line(p[0], p[1], points[i+1][0], points[i+1][1])
#
    #circle(x3, y3, R3, (255,0,0), 0)
#
    #pop_matrix()

    push_matrix()
    translate(WIDTH/2, HEIGHT/2)

    for i,p in enumerate(points):
        if i < len(points)-1:
            sm.color = (255,0,0)
            line(p[0], p[1], points[i+1][0], points[i+1][1])

    pop_matrix()

points = []
t = 0
while t < 1000:
    points.append(harmonograph(t))
    t += 0.01

run()
