"""Chapter 9 - Building Objects with Classes."""
import sys
from random import randrange, randint, choice
from engine import run
from screen_matrix import circle, rect
# pylint: disable=C0103, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Objects"

BLACK = (0,0,0)
WHITE = (255,255,255)
BROWN = (102,51,0)
RED = (255,0,0)
GREEN = (0,102,0)
YELLOW = (255,255,0)
PURPLE = (102,0,204)
COLOR_LIST = [WHITE, RED, YELLOW, PURPLE]

class Ball:
    """Bouncing Ball object."""

    def __init__(self, x, y):
        """Create a Ball object."""
        self.xcor = x
        self.ycor = y
        self.xvel = randrange(-2,2)
        self.yvel = randrange(-2,2)
        self.color = (randint(0,255),
                      randint(0,255),
                      randint(0,255))
        self.radius = randint(3,25)

    def update(self):
        """Update Ball state."""
        self.xcor += self.xvel
        self.ycor += self.yvel
        if self.xcor > WIDTH or self.xcor < 0:
            self.xvel = -self.xvel
        if self.ycor > WIDTH or self.ycor < 0:
            self.yvel = -self.yvel

    def draw(self):
        """Draw a Ball at its position."""
        circle(self.xcor, self.ycor, self.radius, self.color, 0)

class Sheep:
    """Sheep object."""

    def __init__(self, x, y, col):
        """Create a Sheep object."""
        self.x = x
        self.y = y
        self.sz = 5
        self.energy = 20
        self.col = col

    def update(self):
        """Update Sheep state."""
        move = 5
        self.energy -= 1
        if self.energy <= 0:
            sheep.remove(self)
        self.x += randint(-move,move)
        self.y += randint(-move,move)

        # text just has these as > tests,
        # which causes an index error when the value
        # exactly equals WIDTH
        if self.x >= WIDTH:
            self.x %= WIDTH
        if self.y >= HEIGHT:
            self.y %= HEIGHT
        if self.x < 0:
            self.x += WIDTH
        if self.y < 0:
            self.y += HEIGHT

        xscl = int(self.x / PATCH_SIZE)
        yscl = int(self.y / PATCH_SIZE)
        # text has a couple bugs that were causing index errors
        # here - added this try/catch to pin it down...
        try:
            g = grass[xscl * ROWS_OF_GRASS + yscl]
        except IndexError as e:
            print(e)
            print(f"xscl = {xscl}")
            print(f"sheep.x = {self.x}")
            print(f"yscl = {yscl}")
            print(f"sheep.y = {self.y}")
            print(f"ROWS_OF_GRASS = {ROWS_OF_GRASS}")
            print(f"product = {xscl * ROWS_OF_GRASS + yscl}")
            sys.exit()
        if not g.eaten:
            self.energy += g.energy
            g.eaten = True

    def draw(self):
        """Draw a Sheep at its position."""
        circle(self.x, self.y, self.sz, self.col, 0)

class Grass:
    """Grass object."""

    def __init__(self, x, y, sz):
        """Create a Grass object."""
        self.x = x
        self.y = y
        self.energy = 5
        self.eaten = False
        self.sz = sz

    def update(self):
        """Update Grass state."""

    def draw(self):
        """Draw a Grass at its position."""
        col = GREEN
        if self.eaten:
            col = BROWN
        rect(self.x, self.y, self.sz, self.sz, col, width=0)

def update():
    """Update the app state once per frame."""
    for g in grass:
        g.update()
    for s in sheep:
        s.update()

def draw():
    """Draw to the window once per frame."""
    for g in grass:
        g.draw()
    for s in sheep:
        s.draw()

sheep = []
for _ in range(20):
    sheep.append(Sheep(randint(0,WIDTH), 
                       randint(0,HEIGHT),
                       choice(COLOR_LIST)))

grass = []
PATCH_SIZE = 5
# text has this as floating point division, which causes an error
# when calclating an index above - needs to be integer division
ROWS_OF_GRASS = HEIGHT//PATCH_SIZE
for x in range(0, WIDTH, PATCH_SIZE):
    for y in range(0, HEIGHT, PATCH_SIZE):
        grass.append(Grass(x, y, PATCH_SIZE))

run()
