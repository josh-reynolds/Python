from random import randint
from engine import *

WIDTH = 640
HEIGHT = 240
TITLE ="The Nature of Code"

# ----------------------------------------------------
class Walker:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

    def display(self):
        #screen.draw.pixel(self.x, self.y, (255,0,0))
        screen.draw.circle(self.x, self.y, 10, (0,0,0))

    def step(self):
        step_x = randint(0,2) - 1
        step_y = randint(0,2) - 1
        self.x += step_x
        self.y += step_y
# ----------------------------------------------------

# ----------------------------------------------------
def update():
    #w.step()

    idx = randint(0, len(randomCounts)-1)
    randomCounts[idx] += 1

def draw():
    #w.display()

    bar_width = WIDTH // len(randomCounts)
    for i in range(len(randomCounts)):
        rect = (i * bar_width, HEIGHT - randomCounts[i], bar_width-1, randomCounts[i])
        screen.draw.rect(rect, (0,255,0), 0)

#w = Walker()

randomCounts = [0 for i in range(20)]

run()

# The primary difference from text: Processing does not redraw the background 
# automatically, but the engine does, so we aren't getting trails drawn 
# on-screen - consider implementing similar functionality

# Processing also expects a setup() function to be run once at the start - I toyed with
# this idea in the engine, but the top-level code just above the call to run() is 
# equivalent. If I _do_ add such a thing back to the engine, would need to use some
# trickery to avoid having to add a dummy setup() to old projects - we want backward
# compatibility.
