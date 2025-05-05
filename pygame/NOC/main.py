import pygame.gfxdraw
from random import randint
from engine import *

WIDTH = 640
HEIGHT = 360
TITLE ="The Nature of Code"

class Walker:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

    def display(self):
        #pygame.gfxdraw.pixel(screen.surface, self.x, self.y, (0,0,0))
        pygame.gfxdraw.circle(screen.surface, self.x, self.y, 10, (0,0,0))

    def step(self):
        choice = randint(0,4)
        if choice == 0:
            self.x += 1
        elif choice == 1:
            self.x -= 1
        elif choice == 2:
            self.y += 1
        elif choice == 3:
            self.y -= 1

def update():
    w.step()

def draw():
    w.display()

w = Walker()

run()

# The primary difference from text: Processing does not redraw the background 
# automatically, but the engine does, so we aren't getting trails drawn 
# on-screen - consider implementing similar functionality

# Processing also expects a setup() function to be run once at the start - I toyed with
# this idea in the engine, but the top-level code just above the call to run() is 
# equivalent. If I _do_ add such a thing back to the engine, would need to use some
# trickery to avoid having to add a dummy setup() to old projects - we want backward
# compatibility.

# Should also implement Painter methods for pixel and circle so we don't need to 
# import and use pygame.gfxdraw at this level.
