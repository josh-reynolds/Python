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

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"


# ----------------------------------------------------
def update():
    f.run()

# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    f.draw()

# ----------------------------------------------------

resolution = 20
grid = [[[] for i in range(WIDTH//resolution)] for i in range(HEIGHT//resolution)]
f = Flock(grid, WIDTH, HEIGHT, resolution)
for i in range(100):
    f.add_boid(Boid(WIDTH//2 + randint(-1,1), HEIGHT//2 + randint(-1,1), WIDTH, HEIGHT))

# ----------------------------------------------------
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
