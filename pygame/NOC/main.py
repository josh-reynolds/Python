import math
from random import uniform, randint, random
import pygame
from pygame import Rect, Surface, transform
from pygame.locals import *
from engine import *
from mover import Mover
from pvector import PVector
from liquid import Liquid
from attractor import Attractor, Repulsor
from rotator import Rotator
from orbiter import Orbiter
from oscillator import Oscillator
from wave import Wave
from pendulum import Pendulum
from spring import Spring
from particles import ParticleSystem, Particle, Smoke
from vehicle import Vehicle
from grid import Grid
from flow_field import FlowField
from path import Path
from boids import Boid
from flock import Flock
from wolfram import CA
from life import Life
from fractals import draw_circle, cantor

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

class KochLine:
    def __init__(self, a, b):
        self.start = a.copy()
        self.end = b.copy()

    def draw(self):
        screen.draw.line((0,0,0), (self.start.x, self.start.y), (self.end.x, self.end.y))
        #screen.draw.circle(self.koch_a().x, self.koch_a().y, 8, (255,0,0))
        #screen.draw.circle(self.koch_b().x, self.koch_b().y, 8, (255,0,0))
        #screen.draw.circle(self.koch_c().x, self.koch_c().y, 8, (255,0,255))
        #screen.draw.circle(self.koch_d().x, self.koch_d().y, 8, (255,0,0))
        #screen.draw.circle(self.koch_e().x, self.koch_e().y, 8, (255,0,0))

    def koch_a(self):
        return self.start.copy()

    def koch_b(self):
        v = PVector.sub(end, start)
        v / 3
        return PVector.add(self.start, v)

    def koch_c(self):
        v = PVector.sub(end, start)
        v / 3
        a = PVector.add(self.start, v)
        v.rotate(-60)
        return PVector.add(a,v)

    def koch_d(self):
        v = PVector.sub(end, start)
        v * 2
        v / 3
        return PVector.add(self.start, v)

    def koch_e(self):
        return self.end.copy()

class Test:
    def __init__(self):
        self.points = []
        start = PVector(100,0)
        for i in range(0, 280, 10):
            new_point = start.copy()
            new_point.rotate(i)
            self.points.append(new_point)

    def draw(self):
        for p in self.points:
            translate = PVector.add(p, PVector(WIDTH//2,HEIGHT//2))
            screen.draw.circle(translate.x, translate.y, 8, (255,0,0))
        screen.draw.circle(WIDTH//2, HEIGHT//2, 100, (0,0,0), 1)

def generate():
    global lines
    next_lines = []

    for kl in lines:
        a = kl.koch_a()
        b = kl.koch_b()
        c = kl.koch_c()
        d = kl.koch_d()
        e = kl.koch_e()

        next_lines.append(KochLine(a,b))
        next_lines.append(KochLine(b,c))
        next_lines.append(KochLine(c,d))
        next_lines.append(KochLine(d,e))

    lines = next_lines.copy()

# ----------------------------------------------------
def update():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    for kl in lines:
        kl.draw()
    #t.draw()
# ----------------------------------------------------

# ----------------------------------------------------
lines = []
start = PVector(0,200)
end = PVector(WIDTH, 200)
lines.append(KochLine(start, end))
generate()
#t = Test()
run()
# ----------------------------------------------------

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
# different from the book version. (Update - declaring as global in the function may do
# the trick...)

# Another potential addition to the engine: mouse support...

# The Processing transform functions are also handy. Don't have a good equivalent in
# Pygame. Could do something like it by:
#  1) drawing everything to a separate surface, not directly on the screen
#  2) applying the current 'screen transform' - defaulting to identity
#  3) blit the transformed surface to the screen surface
# translate(), rotate() etc. would modify the screen transform
# and then we'd want to also support push_matrix() and pop_matrix()
# fairly big change to the engine, with potential to break backwards compat, so need
# to approach carefully and test everything thoroughly

# Chapter 5 covers physics libraries. Apparently there _is_ a version of Box2D for pygame
# (pybox2d), and it seems to be available on NixOS according to the search page. But the 
# available versions are for Python 3.12 and 3.13, while I currently have 3.11. Some
# fiddling required. The story with toxiclibs is murkier. But a general search for 
# 'pygame physics libraries' turns up pymunk, so may give that one a go.

# In the meantime, I think I'll skip over Chapter 5 and revisit it later.
