from random import randint, random, gauss, uniform
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
        ### NOC Example 1.1 ----------------
        #step_x = randint(0,2) - 1
        #step_y = randint(0,2) - 1
        #self.x += step_x
        #self.y += step_y

        ### NOC Example 1.3 ----------------
        #r = random()
        #if (r < 0.4):
            #self.x += 1
        #elif (r < 0.6):
            #self.x -= 1
        #elif (r < 0.8):
            #self.y += 1
        #else:
            #self.y -= 1

        ### NOC Example 1.3 ----------------
        #num = gauss()
        #sd = 60
        #mean = WIDTH // 2
        #self.x = int(sd * num + mean)
        #self.y = HEIGHT // 2

        ### NOC Exercise 1.5 ---------------
        #self.x += int(4 * gauss())
        #self.y += int(4 * gauss())

        stepsize = 2 * montecarlo()
        self.x += uniform(-stepsize, stepsize)
        self.y += uniform(-stepsize, stepsize)

# ----------------------------------------------------
def montecarlo():
    while True:
        r1 = random()
        r2 = random()
        if r2 < (r1 ** 2):
            return r1

# ----------------------------------------------------
def update():
    w.step()
#
    #idx = randint(0, len(randomCounts)-1)
    #randomCounts[idx] += 1

def draw():
    ### NOC Example 1.2 ----------------
    #bar_width = WIDTH // len(randomCounts)
    #for i in range(len(randomCounts)):
        #rect = (i * bar_width, HEIGHT - randomCounts[i], bar_width-1, randomCounts[i])
        #screen.draw.rect(rect, (0,255,0), 0)

    w.display()

    #for i in range(100):
        #color = (colors[i][0], colors[i][1], colors[i][2]) 
        #screen.draw.circle(dots[i][0], dots[i][1], 10, color)


w = Walker()

#randomCounts = [0 for i in range(20)]

### NOC Exercise 1.4 ----------------
#dots = []
#colors = []
#for i in range(100):
    #x = int(gauss() * 60 + WIDTH // 2)
    #y = int(gauss() * 24 + HEIGHT // 2)
    #dots.append((x,y))
#
    #r = int(gauss() * 24 + 256 // 2)
    #g = int(gauss() * 24 + 256 // 2)
    #b = int(gauss() * 24 + 256 // 2)
    #colors.append((r,g,b))

run()

# The primary difference from text: Processing does not redraw the background 
# automatically, but the engine does, so we aren't getting trails drawn 
# on-screen - consider implementing similar functionality

# Processing also expects a setup() function to be run once at the start - I toyed with
# this idea in the engine, but the top-level code just above the call to run() is 
# equivalent. If I _do_ add such a thing back to the engine, would need to use some
# trickery to avoid having to add a dummy setup() to old projects - we want backward
# compatibility.
