import math
import pygame
from random import randint, uniform
from engine import *

WIDTH = 640
HEIGHT = 360
TITLE ="The Nature of Code"

class PVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return PVector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return PVector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return PVector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return PVector(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        m = self.mag()
        return 0 if m == 0 else self/m

class Mover:
    def __init__(self):
        self.location = PVector(randint(0,WIDTH), randint(0,HEIGHT))
        self.velocity = PVector(uniform(-2,2), uniform(-2,2))

    def update(self):
        self.location += self.velocity
        self.check_edges()

    def check_edges(self):
        #if ((self.location.x > WIDTH) or (self.location.x < 0)):
            #self.velocity.x *= -1
        #if ((self.location.y > HEIGHT) or (self.location.y < 0)):
            #self.velocity.y *= -1

        if self.location.x > WIDTH:
            self.location.x = 0
        elif self.location.x < 0:
            self.location.x = WIDTH

        if self.location.y > HEIGHT:
            self.location.y = 0
        elif self.location.y < 0:
            self.location.y = HEIGHT

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, 10, (255,0,0))

# ----------------------------------------------------
def update():
    b.update()

# ----------------------------------------------------
def draw():
    b.draw()

    # NOC Example 1.3 (p. 39) ------------------------
    # NOC Example 1.4 (p. 41) ------------------------
    x,y = pygame.mouse.get_pos()
    mouse = PVector(x,y)
    center = PVector(WIDTH//2, HEIGHT//2)
    mouse = mouse - center

    # NOC Example 1.6 (p. 45) ------------------------
    mouse = mouse.normalize()
    mouse = mouse * 50
    #mouse = mouse / 2
    m = mouse.mag()
    mouse = mouse + center
    screen.draw.line((0,0,0), (center.x, center.y), (mouse.x, mouse.y))

    # NOC Example 1.5 (p. 43) ------------------------
    screen.draw.rect((0,0,m,10), (255,0,0), 0)

# NOC Example 1.2 (p. 35) ----------------------------
b = Mover()

run()

# The primary difference from text: Processing does not redraw the background 
# automatically, but the engine does, so we aren't getting trails drawn 
# on-screen - consider implementing similar functionality

# Processing also expects a setup() function to be run once at the start - I toyed with
# this idea in the engine, but the top-level code just above the call to run() is 
# equivalent. If I _do_ add such a thing back to the engine, would need to use some
# trickery to avoid having to add a dummy setup() to old projects - we want backward
# compatibility.

# Latest hurdle: Processing includes a noise() function to generate Perlin noise. I don't
# have the equivalent in Pygame or stock Python. I _could_ import a module, but I am
# contemplating rolling my own and sticking into the engine. Researching now.

# Perlin noise project is working, need to package it up and add to the engine...

# Moving ahead to Chapter 1 now. New issue: the engine can't access top-level primitive 
# variables - or at least it can't modify them. But if we wrap the values in a class, it
# works fine. I think this is a referencing problem due to the way the engine finds the
# content of this parent script, need to fiddlw with this to sort it out. But for now,
# going ahead with class-based solution, which is why Example 1.1 above looks a little
# different from the book version.

# Another potential addition to the engine: mouse support.
