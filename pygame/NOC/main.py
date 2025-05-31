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

WIDTH = 640
HEIGHT = 360
TITLE = "The Nature of Code"

# The heading code isn't working properly, needs debugging
# I added some line indicators to see what's going on.
# Observed bugs:
#   [FIXED] Drawing orientation doesn't align with heading vector, and is inconsistent
#   [FIXED] Drawing rotates opposite direction from heading vector
#   [FIXED] Heading vector properly moves toward target only in lower two quadrants (PI to TWO_PI)
#     spins indefinitely conterclockwise in upper two without stopping on target
#   [FIXED] Rotation calculation doesn't properly handle crossing 0/360 degree boundary,
#     will take the long way around

# If we take out the sprite rotation, can see cause of first bug: it is using the 
# top-left corner of the image rect as axis - need to center this
# also, current drawing orientation is pointing down - either adapt or fix

# As for the quadrants, the top two return angles of 0 to -180, and the bottom
# return angles of 0 to 180 - need to adjust or accommodate in order to correct

# So, the heading calculation is just math.atan2(), which:
#   is oriented vertically (0 degrees is up)
#   returns positive values for the right-hand quadrants (+x,+y) and (+x,-y)
#   returns negative values for the left-hand quadrants (-x,+y) and (-x,-y)

# The vehicle angle is counting 0 to 360 degrees clockwise, oriented to the right:
#   0/360 degrees is (+x,0y)
#   90 degrees is (0x,-y)
#   180 degrees is (-x,0y))
#   270 degrees is (0x,+y)
# The current motion of the pointer, however, is counter-clockwise (decrementing angle)

# Fixed the quadrant problem, but that introduced a new issue: the delta always takes
# the long away around the circle - it can't cross the 0/360 boundary

# Instead of forcing atan values to 0-360 range, perhaps it's better to use the 
# +/- 180 range, which would indicate direction. Also could shift towards relative
# rather than absolute angles...

class Vehicle:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        width = 20
        height = 80
        self.rect = Rect(x - width/2, y - height/2, 20, 80)
        self.color = (0, 200, 0)
        
        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)
        pygame.draw.rect(self.surf, self.color, (0, 0, width, height), width=0) 
        pygame.draw.rect(self.surf, (0,0,0), (0, 0, width, height), width=1) 
        pygame.draw.circle(self.surf, (0,0,0), (10,10), 10, 0)
        self.original_surf = self.surf.copy()

        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)

        self.r = 3.0
        self.maxspeed = 4
        self.maxforce = 0.1

        self.angle = 0

        self.target = PVector(0,0)

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.maxspeed)
        self.location + self.velocity
        self.acceleration * 0

        prev_angle = self.angle % 360
        to_target = PVector.sub(self.target, self.location).normalize()
        screen.draw.line((0,0,0), (self.location.x, self.location.y), (self.target.x, self.target.y))

        pa = math.radians(prev_angle)
        angle_x = self.location.x + math.cos(pa) * 100
        angle_y = self.location.y + math.sin(pa) * 100
        screen.draw.line((255,0,0), (self.location.x, self.location.y), (angle_x, angle_y))

        target_angle = to_target.heading()
        if target_angle < 0:
            target_angle += 360

        delta = (target_angle - prev_angle)
        if delta > 180:
            delta = -(360 - delta)
        if delta < -180:
            delta = 360 + delta

        adjust = 0
        if delta > 1:
            adjust = 3
        elif delta < -1:
            adjust = -3

        self.angle = prev_angle + adjust
        self.rotate()

    def draw(self):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

    def apply_force(self, force):
        self.acceleration + force

    def seek(self, target):
        self.target = target
        desired = PVector.sub(target, self.location).normalize()
        desired * self.maxspeed
        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.maxforce)
        self.apply_force(steer)

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, -self.angle - 90)
        w,h = self.surf.get_size()
        self.rect = Rect(self.location.x-w/2, self.location.y-h/2, w, h)

# ----------------------------------------------------
def update():
    v.seek(PVector(*pygame.mouse.get_pos()))
    v.update()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    v.draw()
# ----------------------------------------------------

v = Vehicle(WIDTH//2, HEIGHT//2)

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
