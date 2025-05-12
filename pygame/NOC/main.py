from engine import *

WIDTH = 640
HEIGHT = 360
TITLE ="The Nature of Code"

class Ball:
    def __init__(self, x, y, xspeed, yspeed):
        self.x = x
        self.y = y
        self.xspeed = xspeed
        self.yspeed = yspeed

    def update(self):
        self.x += self.xspeed
        self.y += self.yspeed

        if ((self.x > WIDTH) or (self.x < 0)):
            self.xspeed *= -1
        if ((self.y > HEIGHT) or (self.y < 0)):
            self.yspeed *= -1

    def draw(self):
        screen.draw.circle(self.x, self.y, 10, (255,0,0))

# ----------------------------------------------------
def update():
    b.update()

# ----------------------------------------------------
def draw():
    b.draw()

# NOC Example 1.1 (p. 29) ----------------------------
b = Ball(100,100, 1, 3.3)

run()

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
