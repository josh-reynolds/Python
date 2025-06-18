import math
from random import uniform, randint, random, choice
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
from fractals import draw_circle, cantor, KochCurve, branch
from rotation_test import Test
from screen_matrix import sm, line, translate, rotate, push_matrix, pop_matrix
from lsystem import Rule, LSystem, Turtle
from rocket import SmartRockets

WIDTH = 860
HEIGHT = 200
TITLE = "The Nature of Code"

class DNA:
    def __init__(self):
        self.genes = [random() for i in range(20)]

class Face:
    def __init__(self, left, top):
        self.dna = DNA()
        self.fitness = 0
        self.rect = Rect(left, top, 160, 160)
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]
        self.border_color = (0,0,0)

    def draw(self):
        radius = remap(self.dna.genes[0], 0, 1, 20, 70)
        color = (int(self.dna.genes[1] * 255), 
                 int(self.dna.genes[2] * 255), 
                 int(self.dna.genes[3] * 255))
        screen.draw.circle(self.x, self.y, radius, color)

        eye_y = remap(self.dna.genes[4], 0, 1, 0, 15)
        eye_x = remap(self.dna.genes[5], 0, 1, 0, radius)
        eye_size = remap(self.dna.genes[5], 0, 1, 3, 15)
        eye_color = (int(self.dna.genes[4] * 255), 
                     int(self.dna.genes[5] * 255), 
                     int(self.dna.genes[6] * 255))
        screen.draw.circle(self.x - eye_x, self.y - eye_y, eye_size, eye_color)
        screen.draw.circle(self.x + eye_x, self.y - eye_y, eye_size, eye_color)

        mouth_color = (int(self.dna.genes[7] * 255), 
                       int(self.dna.genes[8] * 255), 
                       int(self.dna.genes[9] * 255))
        mouth_x = remap(self.dna.genes[5], 0, 1, -25, 25)
        mouth_y = remap(self.dna.genes[5], 0, 1, 0, 25)
        mouthw = remap(self.dna.genes[5], 0, 1, 0, 50)
        mouthh = remap(self.dna.genes[5], 0, 1, 0, 10)
        screen.draw.rect((self.x + mouth_x, self.y + mouth_y, mouthw, mouthh), mouth_color, 0)

        screen.draw.rect(self.rect, self.border_color, 1)

        screen.draw.text(str(self.fitness), (self.rect.left + 10, self.rect.top + 10))  

    def rollover(self, mouseX, mouseY):
        if self.rect.collidepoint((mouseX, mouseY)):
            self.border_color = (255,0,0)
            self.fitness += 1
        else:
            self.border_color = (0,0,0)

class Population:
    def __init__(self, mutation_rate, size):
        self.mutation_rate = mutation_rate
        self.size = size
        self.faces = [Face((10 * i + 10) + 160 * i, 10) for i in range(self.size)]

    def rollover(self, mouseX, mouseY):
        for f in self.faces:
            f.rollover(mouseX, mouseY)

    def draw(self):
        for f in self.faces:
            f.draw()

    def selection(self):
        print("Population.selection()")

    def reproduction(self):
        print("Population.reproduction()")

class Button:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.rect = Rect(x, y, w, h)
        self.active = False

    def clicked(self, mouseX, mouseY):
        if ((pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1]) and
            self.rect.collidepoint((mouseX, mouseY)) and not self.active):
            self.color = (255,128,128)
            self.active = True
            return True
        else:
            if (not pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[1]):
                self.active = False
            self.color = (255,255,255)
            return False

    def draw(self):
        screen.draw.rect(self.rect, self.color, 0)
        screen.draw.rect(self.rect, (0,0,0))
        screen.draw.text(self.text, pos=(self.x + 2, self.y))

# ----------------------------------------------------
def update():
    mouseX, mouseY = pygame.mouse.get_pos()
    population.rollover(mouseX, mouseY)
    if button.clicked(mouseX, mouseY):
        population.selection()
        population.reproduction()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    population.draw()
    button.draw()
    #f.draw()
# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
mutation_rate = 0.05
population = Population(mutation_rate, 5)
button = Button(15, 175, 180, 20, "evolve new generation")

f = Face(10, 10)

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

# Rotation was an issue again in the Fractal chapter (8). I implemented a rotate on my
# homegrown vector class, and a test class to verify everything is working OK. May still be
# some weirdness going on as compared to the Processing equivalent. Radians vs. degrees in
# the various function calls is easy to get crossed up. Behavior in all four quadrants, 
# rotational direction, and going past 360 degrees are all consderations too. But this is
# working well enough to get the Koch curve implemented.

# I've been able to survive without push/popmatrix so far, but the next section on Fractal
# Trees makes heavy use of it. Will need to think about an approach. As noted above, the
# long-term solution is probably to integrate this deeply into the engine, but that's more
# work than warranted just yet. But maybe a tiny class that wraps calls to screen.draw could
# give the desired behavior.

# What if screen retains the matrix settings? So you'd call screen.translate(), screen.rotate(),
# etc. It would maintain a transform matrix, which may be enough on its own. Translate by itself
# could be handled just by an 'origin' field, which by default is set to the top-left of the
# window (0,0).

# Additional hurdle to add into this one: the transform calls should be relative/accumulative,
# but the current model has us calling repeatedly in draw() - and we need to do that because
# otherwise the first draw() out of the run() loop will clear the screen. So... I'm adding
# back the setup() function with a hook in the main loop (I previously called this 'once()'). As
# noted above, we'll need to do something dynamic to preserve backward compatibility (i.e. don't
# barf if the main script does not have a setup() function.

# I also needed to suppress the auto-fill behavior in the main loop, via an optional flag to
# run(). This is a bit klunky right now, needs lots of smoothing before we can bring it back
# to the main engine project. But this is a good sandbox for figuring it all out.
