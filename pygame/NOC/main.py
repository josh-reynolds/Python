import math
from random import uniform, randint, random, choice, seed
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
from face import Faces

WIDTH = 640
HEIGHT = 480
TITLE = "The Nature of Code"

class World:
    def __init__(self, size):
        self.bloops = [Bloop(PVector(randint(0,WIDTH), randint(0,HEIGHT)), DNA()) for i in range(size)]
        self.foods = [PVector(uniform(0,WIDTH), uniform(0,HEIGHT)) for i in range(size*50)]

    def update(self):
        for b in self.bloops:
            b.update()
            b.eat(self.foods)
            child = b.reproduce()
            if child is not None:
                self.bloops.append(child)
        for i in range(len(self.bloops)-1,-1,-1):
            if self.bloops[i].is_dead():
                self.bloops.remove(self.bloops[i])

    def draw(self):
        for b in self.bloops:
            b.draw()
        for f in self.foods:
            screen.draw.rect((f.x - 3, f.y - 3, 6, 6), (255,0,0), 0)

class DNA:
    def __init__(self):
        self.genes = [random()]

    def copy(self):
        d = DNA()
        d.genes = self.genes.copy()
        return d

    def mutate(self, mutation_rate):
        if random() < mutation_rate:
            self.genes = [random()]

class Bloop:
    def __init__(self, location, dna):
        self.location = location
        self.xoff = uniform(80.1,120.1)
        self.yoff = uniform(8.1,10.1)
        self.health = 100
        self.color = (randint(0,255), randint(0,255), randint(0,255))

        self.dna = dna
        self.r = remap(self.dna.genes[0], 0, 1, 0, 50)
        self.max_speed = remap(self.dna.genes[0], 0, 1, 15, 0)

    def update(self):
        vx = remap(noise(self.xoff),-1,1,-self.max_speed,self.max_speed)
        vy = remap(noise(self.yoff),-1,1,-self.max_speed,self.max_speed)
        velocity = PVector(vx,vy)
        self.xoff += 0.01
        self.yoff += 0.01

        self.location + velocity
        if self.location.x < 0:
            self.location.x = 0
        if self.location.x > WIDTH:
            self.location.x = WIDTH
        if self.location.y < 0:
            self.location.y = 0
        if self.location.y > HEIGHT:
            self.location.y = HEIGHT

        self.health -= 1

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.r, self.color)
        screen.draw.circle(self.location.x, self.location.y, self.r, (0,0,0), 1)

    def is_dead(self):
        return self.health < 0.0

    def eat(self, foods):
        for f in foods:
            d = PVector.dist(self.location, f)
            if d < self.r:
                self.health += 100
                foods.remove(f)

    def reproduce(self):
        if random() < 0.01:
            dna = self.dna.copy()
            dna.mutate(0.01)
            return Bloop(self.location, dna)
        else:
            return None

repeat = 128
scale = 0.1
#seed(100000)
gradients = [(1,1), (math.sqrt(2),0), (1,-1), (0,math.sqrt(2)),
             (0,-math.sqrt(2)), (-1,1), (-math.sqrt(2),0), (-1,1)]
random_values = [[randint(0,7) for i in range(repeat)] for i in range(repeat)]

def noise(offset):
    x = offset * scale
    y = 50.1 * scale

    x %= repeat
    y %= repeat

    # grid corners
    x1, y1 = int(x) % repeat, int(y) % repeat
    x2, y2 = (x1 + 1) % repeat, (y1 + 1) % repeat

    # distance vectors
    dA, dB, dC, dD = (x1 - x, y1 - y), \
                     (x1 - x, y2 - y), \
                     (x2 - x, y1 - y), \
                     (x2 - x, y2 - y)

    # gradient vectors
    gA, gB, gC, gD = gradients[random_values[x1][y1]], \
                     gradients[random_values[x1][y2]], \
                     gradients[random_values[x2][y1]], \
                     gradients[random_values[x2][y2]]

    # dot products
    dotA, dotB, dotC, dotD = (dA[0] * gA[0] + dA[1] * gA[1]), \
                             (dB[0] * gB[0] + dB[1] * gB[1]), \
                             (dC[0] * gC[0] + dC[1] * gC[1]), \
                             (dD[0] * gD[0] + dD[1] * gD[1])

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    # fade values
    u, v = fade(x - x1), fade(y - y1)

    #interpolation
    tmp1 = u * dotC + (1 - u) * dotA  # top edge
    tmp2 = u * dotD + (1 - u) * dotB  # bottom edge
    return v * tmp2 + (1 - v) * tmp1  # vertical


# ----------------------------------------------------
def update():
    w.update()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    w.draw()
# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
w = World(10)
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
