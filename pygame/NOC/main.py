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
from particles import ParticleSystem, Particle

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

class SmokeParticle(Particle):
    def __init__(self, x, y):
        self.image = images.texture
        super().__init__(x,y)

    def draw(self):
        if self.lifespan >= 0:
            self.image.set_alpha(self.lifespan//2)
            screen.blit(self.image, (self.location.x, self.location.y))

class Smoke(ParticleSystem):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.gravity = PVector(0,-0.01)

    def add_particle(self):
        self.particles.append(SmokeParticle(self.origin.x, self.origin.y))

# TO_DO: add this to the engine...
def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

# ----------------------------------------------------
def update():
    if pygame.mouse.get_pressed()[0]:
        pos = pygame.mouse.get_pos()
        systems.append(Smoke(pos[0], pos[1]))

    for ps in systems:
        ps.add_particle()
        ps.update()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    for ps in systems:
        ps.draw()
# ----------------------------------------------------

systems = []

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
