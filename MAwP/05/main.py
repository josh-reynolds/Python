"""Chapter 5 - Transforming Shapes with Geometry."""
from math import radians, sqrt
#from math import dist
#import pygame
from engine import run
from screen_matrix import push_matrix, translate, rotate, triangle, pop_matrix
#from screen_matrix import rect
# pylint: disable=C0103, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Geometry"

time = 0

def tri(length, color=(0,0,0), width=1):
    """Draw an equilateral triangle."""
    triangle(0, -length,
             -length*sqrt(3)/2, length/2,
             length*sqrt(3)/2, length/2,
             color, width)

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    # ----------------------------------------
    #global time
    #push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    #rotate(radians(time))
    #for _ in range(12):
        #push_matrix()
        #translate(200,0)
        #rotate(radians(time))
        #rect(0,0,50,50)
        #pop_matrix()
        #rotate(radians(360/12))
    #pop_matrix()
    #time += 1

    # ----------------------------------------
    #screen.fill((0,0,0))
    #mouse_x, mouse_y = pygame.mouse.get_pos()
    #for x in range(20):
        #for y in range(20):
            ## TO_DO: rect is distorted with new implementation, investigate
            #d = dist((30*x, 30* y), (mouse_x, mouse_y))
            #value = int(0.5*d % 255)
            ## TO_DO: book implementation uses HSV, I just have RGB here...
            #color = (value, value//2, value)

            #rect(30*x, 30*y, 25, 25, color)

    # ----------------------------------------
    #global time
    #push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    #rotate(radians(time))
    #tri(200)
    #pop_matrix()
    #time += 0.5

    # ----------------------------------------
    global time
    push_matrix()
    translate(WIDTH/2, HEIGHT/2)
    for i in range(90):
        rotate(radians(360/90))
        push_matrix()
        translate(200,0)
        rotate(radians(time + 2*i*360/90))
        tri(100, (255,0,0), 1)
        pop_matrix()
    pop_matrix()
    time += 1

run()
