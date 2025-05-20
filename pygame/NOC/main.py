from random import uniform, randint
import pygame
from pygame import Rect, Surface, transform
from pygame.locals import *
from engine import *
from mover import Mover
from pvector import PVector
from liquid import Liquid
from attractor import Attractor, Repulsor

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

class Block:
    def __init__(self, x, y, a_vel):
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 80, 20)
        self.color = (0, 200, 0)

        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)
        self.surf.fill(self.color)
        pygame.draw.rect(self.surf, (0,0,0), self.surf.get_rect(), 1)
        self.original_surf = self.surf.copy()

        self.angle = 0
        self.a_vel = a_vel

    def update(self):
        self.a_vel += a_acceleration
        self.angle += self.a_vel

    def draw(self):
        screen.blit(self.surf, (self.rect.x, self.rect.y))
        #screen.draw.rect(self.surf.get_rect(), (0,0,0), 1)
        screen.draw.circle(self.x, self.y, 5, (255,0,0))

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, self.angle)
        w,h = self.surf.get_size()
        self.rect = Rect(self.x-w/2, self.y-h/2, w, h)

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

# ----------------------------------------------------
def update():
    for b in blocks:
        b.rotate()
        b.update()

# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    for b in blocks:
        b.draw()
# ----------------------------------------------------

angle = 0
a_velocity = 0
a_acceleration = 0.001

blocks = []
for i in range(1):
    blocks.append(Block(WIDTH//2, HEIGHT//2, a_velocity))


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
