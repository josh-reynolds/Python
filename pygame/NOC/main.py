from random import uniform, randint
import pygame
from pygame import Rect, Surface, transform
from pygame.locals import *
from engine import *
from mover import Mover
from pvector import PVector
from liquid import Liquid
from attractor import Attractor, Repulsor
from rotator import Rotator

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

def translate(rect, dx, dy):
    rect.x += dx
    rect.y += dy

def rotate(surface, degrees):
    transform.rotate(surface, degrees)
    # [0][0] = math.cos(radians)
    # [0][1] = -math.sin(radians
    # [1][0] = math.sin(radians)
    # [1][1] = math.cos(radians)

    # result = (0,0)
    # r1 = matrix[0]
    # row1 = (r1[0], r1[1])
    # result.x = row1.dot(point)

    # r2 = matrix[1]
    # row2 = (r2[0], r2[1])
    # result.y = row2.dot(point)
    pass


# ----------------------------------------------------
def update():
    for m in movers:
        m.update()
    r.update(0.1)
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    for m in movers:
        m.draw()
    r.draw()
# ----------------------------------------------------

movers = [Mover(1, randint(0,WIDTH), randint(0,HEIGHT), WIDTH, HEIGHT) for i in range(10)]

r = Rotator(WIDTH//2, HEIGHT//2, 0)

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
# different from the book version.

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
