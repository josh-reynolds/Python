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
from screen_matrix import sm, line, translate, rotate, push_matrix, pop_matrix, circle
from lsystem import Rule, LSystem, Turtle
from rocket import SmartRockets
from face import Faces
from ecosystem import World
from perceptron import Simulation, VehicleSimulation

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

class Neuron:
    def __init__(self, x, y, id_):
        self.location = PVector(x,y)
        self.connections = []
        self.sum = 0
        self.id = id_
        self.color = (0,255,0)

    def draw(self):
        for c in self.connections:
            c.draw()
        circle(self.location.x, self.location.y, 16, self.color, 0)
        circle(self.location.x, self.location.y, 16, (0,0,0), 1)

    def update(self):
        for c in self.connections:
            c.update()

    def add_connection(self, connection):
        self.connections.append(connection)

    def feed_forward(self, value):
        self.sum += value
        if self.sum > 1:
            self.fire()
            self.color = (255,0,0)
        else:
            self.color = (0,255,0)

    def fire(self):
        for c in self.connections:
            c.feed_forward(self.sum)
        self.sum = 0

class Network:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        self.neurons = []

    def add_neuron(self, neuron):
        self.neurons.append(neuron)

    def connect(self, a, b):
        a.add_connection(Connection(a, b, random()))

    def draw(self):
        push_matrix()
        translate(self.location.x, self.location.y)
        for n in self.neurons:
            n.draw()
        pop_matrix()

    def feed_forward(self, value):
        start = self.neurons[0]
        start.feed_forward(value)

    def update(self):
        for n in self.neurons:
            n.update()

class Connection:
    def __init__(self, from_, to_, weight):
        self.weight = weight
        self.a = from_
        self.b = to_
        self.sending = False
        self.sender = from_.location.copy()
        self.output = 0

    def draw(self):
        line_weight = math.floor(remap(self.weight, 0, 1, 1, 6))
        line(self.a.location.x, self.a.location.y, self.b.location.x, self.b.location.y, line_weight)
        if self.sending:
            circle(self.sender.x, self.sender.y, 8, (0,0,0), 0)

    def update(self):
        if self.sending:
            self.sender.x = lerp(self.sender.x, self.b.location.x, 0.1)
            self.sender.y = lerp(self.sender.y, self.b.location.y, 0.1)

            d = PVector.dist(self.sender, self.b.location)

            if d < 1:
                self.b.feed_forward(self.output)
                self.sending = False

    def feed_forward(self, value):
        self.output = value * self.weight
        self.sender = self.a.location.copy()
        self.sending = True

class NeuralNetwork:
    def __init__(self):
        self.count = 0

        self.n = Network(WIDTH//2, HEIGHT//2)

        self.a = Neuron(-230,0, 'a')
        self.b = Neuron(0,100, 'b')
        self.c = Neuron(0,-100, 'c')
        self.d = Neuron(0,0, 'd')
        self.e = Neuron(200,0, 'e')

        self.n.add_neuron(self.a)
        self.n.add_neuron(self.b)
        self.n.add_neuron(self.c)
        self.n.add_neuron(self.d)
        self.n.add_neuron(self.e)

        self.n.connect(self.a,self.b)
        self.n.connect(self.a,self.c)
        self.n.connect(self.a,self.d)
        self.n.connect(self.b,self.e)
        self.n.connect(self.c,self.e)
        self.n.connect(self.d,self.e)

    def update(self):
        self.n.update()
        self.count += 1
        if self.count % 30 == 0:
            self.n.feed_forward(random())

    def draw(self):
        self.n.draw()
        screen.draw.text(str(self.count), pos=(WIDTH-50,20))

def lerp(a, b, scale):
    if scale <= 0:
        return a
    elif scale >= 1:
        return b
    else:
        return ((b - a) * scale) + a

# ----------------------------------------------------
def update():
    nn.update()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    nn.draw()
# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
nn = NeuralNetwork()
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

# Nearly done with the text - and I notice I've evolved a workflow of sorts for tackling these
# little projects. For the first many, I would just create the classes and get the thing running
# through code in update()/draw(). Then to preserve the work (and keep this file manageable), I'd
# shunt the classes off to a separate module, import, adjust till it works, then move on. Problem
# is, I was abandoning the code in update()/draw() every time. None of it was super-complicated - 
# the classes do all the heavy lifting - but I'd need to reconstruct in order to run that same
# project again, probably by referring to GitHub history.

# But for the last few, I've also added a 'World' or 'Simulation' class. It has a simple interface:
# ctor, update() and draw(). And for the most part, all of the setup code can drop right in, and
# then the main script becomes very simple. At some point, it might be good to circle back and 
# clean up every project to this standard. (Though I _also_ have acquired quite a backlog of 
# polish and integration work on the engine...)

# Another TO_DO: I hate the syntax I created for PVector math operators. The imperative mutator
# feels wrong every time I write it. Rework so I can replace with a civilized += notation instead.
