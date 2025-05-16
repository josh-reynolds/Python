from engine import *
from random import uniform
from pygame import Rect
from mover import Mover
from pvector import PVector

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

class Attractor:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        self.mass = 20

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.mass*2, (0,0,255))
        screen.draw.circle(self.location.x, self.location.y, self.mass*2, (0,0,0), 1)

    def attract(self, mover):
        force = PVector.sub(self.location, mover.location)
        distance = force.mag()
        distance = max(min(distance, 25), 5)
        force.normalize()
        strength = (G * self.mass * mover.mass) / (distance * distance)
        force * strength
        return force

# ----------------------------------------------------
class Liquid:
    def __init__(self, x, y, w, h, c):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c
        self.rect = Rect(x, y, w, h)

    def draw(self):
        screen.draw.rect(self.rect, (0,0,200,128), 0)
        # TO_DO: check alpha value support - isn't working as expected
        # OK, according to StackOverflow, draw doesn't support alpha
        # instead we need to draw to a separate surface, and blit that
        # to the screen - will need to think about how to fold this 
        # functionality into the engine

# ----------------------------------------------------
def update():
    for m in movers:
        for mv in movers:
            if mv is not m:
                f = mv.attract(m)
                m.apply_force(f)
        m.update()

# ----------------------------------------------------
def draw():
    for m in movers:
        m.draw()

G = 0.4
movers = [Mover(uniform(0.1, 2), uniform(0, WIDTH), uniform(0, HEIGHT), WIDTH, HEIGHT) for i in range(10)]

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
