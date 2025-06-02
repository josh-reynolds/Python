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

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"


class FlowField:
    def __init__(self, resolution):
        self.resolution = resolution
        self.cols = WIDTH//resolution
        self.rows = HEIGHT//resolution
        self.field = [[self.make_vector(i,j) for i in range(self.cols)] for j in range(self.rows)]

    def make_vector(self, col, row):
        center = (self.resolution * col + self.resolution//2, 
                  self.resolution * row + self.resolution//2)
        v = PVector.sub(PVector(WIDTH//2, HEIGHT//2), PVector(*center))
        return PVector.normalize(v)

    def draw(self):
        for x in range(self.cols):
            for y in range(self.rows):
                self.draw_cell(y,x)

    def draw_cell(self, x, y):
        top = self.resolution * y
        left = self.resolution * x
        width = self.resolution
        height = self.resolution

        fill = 1

        center = (top + self.resolution//2, left + self.resolution//2)
        end = (center[0] + self.field[x][y].x * 20, center[1] + self.field[x][y].y * 20)

        screen.draw.rect((top, left, width, height), (255,64,64), fill)
        screen.draw.circle(center[0], center[1], 3, (0,0,0))
        screen.draw.line((0,0,0), center, end)

    def lookup(self, vector):
        column = max(min(vector.x//self.resolution, self.cols), 0)
        row = max(min(vector.y//self.resolution, self.rows), 0)
        return self.field[row][column]


# ----------------------------------------------------
def update():
    #global counter
    #v.seek(PVector(*pygame.mouse.get_pos()))
    #if counter % 4 == 0:
        #v.wander()
    #v.follow(ff)
    #v.update()
    #counter += 1

    global mse
    mse = PVector(*pygame.mouse.get_pos())

# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    #ff.draw()
    #g.draw(counter % 22 + 1)
    g.draw(20)
    #v.draw()

    screen.draw.circle(center.x, center.y, magnitude, (0,0,255), 1)

    screen.draw.line((0,0,0), (center.x, center.y), (v1.x + center.x, v1.y + center.y))

    v2 = PVector.sub(mse, center)
    v2 = v2.normalize() 
    v2 * magnitude
    screen.draw.line((0,0,0), (center.x, center.y), (v2.x + center.x, v2.y + center.y))

    radians = PVector.angle_between(v2, v1)
    degrees = math.degrees(radians)

    screen.draw.text(f"{degrees:0.2f} degrees", (80,200))
    screen.draw.text(f"{radians:0.2f} radians", (80,220))

# ----------------------------------------------------

#v = Vehicle(WIDTH//2, HEIGHT//2, WIDTH, HEIGHT)
#counter = 0

#ff = FlowField(40)
g = Grid(40, WIDTH, HEIGHT)

magnitude = 100
center = PVector(WIDTH//2,HEIGHT//2)

v1 = PVector(1,0)
v1 * magnitude

mse = PVector(0,0)

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
