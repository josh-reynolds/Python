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
from fractals import draw_circle, cantor, KochCurve
from rotation_test import Test

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

class ScreenMatrix:
    def __init__(self):
        self.origin = PVector(0,0)
        self.color = (0,0,0)
        self.angle = 0
        self.stack = []

    def __repr__(self):
        return f"({self.origin.x:0.2f}, {self.origin.y:0.2f}) {self.angle:0.2f} : {self.stack}"

    def translate(self, target):
        print("TRANSLATE --------------------")
        print(f"original target: ({target.x:0.2f}, {target.y:0.2f})")
        print(f"current angle: {self.angle:0.5f}")
        target.rotate(math.degrees(self.angle))
        print(f"rotated target: ({target.x:0.2f}, {target.y:0.2f})")
        self.origin + target
        print(f"new origin: ({self.origin.x:0.2f}, {self.origin.y:0.2f})")

    def rotate(self, radians):
        print("ROTATE -----------------------")
        print(f"target angle: {radians:0.5f}")
        self.angle += radians
        print(f"new angle: {self.angle:0.5f}")

    def push_matrix(self):
        print("PUSH MATRIX ------------------")
        self.stack.append((self.origin.copy(), self.angle))
        print(self.stack)

    def pop_matrix(self):
        print("POP MATRIX -------------------")
        print(self.stack)
        if len(self.stack) > 0:
            self.origin, self.angle = self.stack.pop()
            print(f"reset origin: ({self.origin.x:0.2f}, {self.origin.y:0.2f})")
            print(f"reset angle: {self.angle:0.5f}")

    def draw_line(self, start, end, width=2):
        print("DRAW LINE --------------------")
        s = PVector(*start)
        s.rotate(math.degrees(self.angle))
        s + self.origin

        e = PVector(*end)
        e.rotate(math.degrees(self.angle))
        e + self.origin

        print(f"drawing between ({s.x:0.2f}, {s.y:0.2f}) and ({e.x:0.2f}, {e.y:0.2f})")

        screen.draw.line(self.color, (s.x, s.y), (e.x, e.y), width)
        screen.draw.circle(s.x, s.y, 3, (255,0,0))

def translate(x, y):
    sm.translate(PVector(x,y))

def rotate(radians):
    sm.rotate(radians)

def push_matrix():
    sm.push_matrix()

def pop_matrix():
    sm.pop_matrix()

def line(ax, ay, bx, by):
    sm.draw_line((ax, ay), (bx, by))

def branch(length):
    line(0, 0, 0, -length)
    translate(0, -length)

    length *= 0.66

    if length > 2:
        push_matrix()
        rotate(math.pi/6)
        branch(length)
        pop_matrix()

        #push_matrix()
        #rotate(-math.pi/6)
        #branch(length)
        #pop_matrix()

# ----------------------------------------------------
def update():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    screen.draw.line((0,0,255), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
    screen.draw.line((0,0,255), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 1)

    translate(WIDTH//2, HEIGHT//2)
    push_matrix()
    #branch(100)

    line(0, 0, 0, -100)
    translate(0, -100)
    pop_matrix()

    push_matrix()
    rotate(math.pi/2)
    line(0, 0, 0, -100)
    translate(0, -100)
    pop_matrix()

    push_matrix()
    rotate(math.pi/2)
    line(0, 0, 0, -100)
    translate(0, -100)
    pop_matrix()

    push_matrix()
    rotate(math.pi/2)
    line(0, 0, 0, -100)
    translate(0, -100)
    pop_matrix()
# ----------------------------------------------------

# ----------------------------------------------------
sm = ScreenMatrix()
theta = math.pi/6

run(draw=False)
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
